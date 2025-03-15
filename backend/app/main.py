from fastapi import FastAPI
from app.routes import pdf  # ✅ Import the upload route
import os
app = FastAPI()

# ✅ Include the PDF upload route
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
HF_API_KEY = os.getenv("HF_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
app.include_router(pdf.router, prefix="/pdf", tags=["PDF Processing"])

