import uuid
import pdfplumber
import requests
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from app.database import SessionLocal, PDFSession, ChatMessage  # Ensure correct import path
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer

load_dotenv()
router = APIRouter()

# Hugging Face API Configuration
HF_API_KEY = os.getenv("HF_API_KEY")
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
QA_MODEL = "deepset/roberta-base-squad2"

tokenizer = AutoTokenizer.from_pretrained(QA_MODEL)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for chat requests
class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Validate PDF file
        if not file_bytes.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="Invalid PDF file. Please upload a valid PDF.")

        # Extract text from the PDF bytes
        text = extract_text(file_bytes)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Uploaded PDF contains no readable text.")

        # Get summary from Hugging Face
        summary = get_summary(text)

        # Store in the database
        pdf_session = PDFSession(
            session_id=session_id,
            pdf_name=file.filename,
            text=text,
            summary=summary
        )
        db.add(pdf_session)
        db.commit()

        return JSONResponse(content={"message": "PDF uploaded successfully", "session_id": session_id, "summary": summary})
    
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "An unexpected error occurred. Please try again."})

def extract_text(pdf_bytes):
    """Extract text from PDF file bytes using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        raise HTTPException(status_code=400, detail="Error processing PDF. Please upload a valid file.")
    return text.strip()

def get_summary(text):
    """Call Hugging Face Summarization API"""
    url = f"https://api-inference.huggingface.co/models/{SUMMARIZATION_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text})

    if response.status_code == 200:
        return response.json()[0].get('summary_text', "Summary not available.")
    return "Summary not available."

def split_text_into_chunks(text, chunk_size=512, overlap=100):
    """Splits text into overlapping chunks using Hugging Face tokenizer."""
    tokens = tokenizer.tokenize(text)
    chunks = []
    
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(tokenizer.convert_tokens_to_string(chunk))

    return chunks

def get_most_relevant_chunk(text_chunks, question, top_n=1):
    """Finds the most relevant text chunk based on similarity with the question."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([question] + text_chunks)
    
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]

    return [text_chunks[i] for i in top_indices]

@router.post("/chat/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    message = request.message

    pdf_session = db.query(PDFSession).filter(PDFSession.session_id == session_id).first()
    if not pdf_session:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    # Split text into chunks
    text_chunks = split_text_into_chunks(pdf_session.text)

    # Retrieve the most relevant chunk
    relevant_chunks = get_most_relevant_chunk(text_chunks, message)

    # Get an answer from Hugging Face
    response_text = get_answer(relevant_chunks, message)

    # Store chat in database
    chat_message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        user_message=message,
        bot_response=response_text,
        timestamp=datetime.utcnow()
    )
    db.add(chat_message)
    db.commit()

    return JSONResponse(content={"response": response_text})

def get_answer(text_chunks, question):
    """Call Hugging Face QA model with the most relevant text chunk."""
    url = f"https://api-inference.huggingface.co/models/{QA_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    best_answer = None
    best_score = 0

    for chunk in text_chunks:
        payload = {"question": question, "context": chunk}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            answer_data = response.json()
            score = answer_data.get("score", 0)  # Confidence score
            if score > best_score:
                best_score = score
                best_answer = answer_data.get("answer", "I couldn't find an answer.")

    return best_answer or "No relevant information found."

@router.delete("/chat/end/{session_id}")
async def end_chat(session_id: str, db: Session = Depends(get_db)):
    pdf_session = db.query(PDFSession).filter(PDFSession.session_id == session_id).first()
    if not pdf_session:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.delete(pdf_session)
    db.commit()

    return JSONResponse(content={"message": "Chat session ended successfully."})
