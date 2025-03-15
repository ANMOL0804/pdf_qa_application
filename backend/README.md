# PDF Q&A Chatbot Backend

This backend service allows users to upload a PDF file, extract its text, and interact with it through a chat-based interface. Users can ask questions about the PDF content, and the backend will provide answers based on the text extracted from the PDF.

## Features
- **PDF Upload**: Allows users to upload a PDF file. The file's text is extracted and stored in the database.
- **Summarization**: The backend provides a summary of the uploaded PDF using the Hugging Face Summarization model (`facebook/bart-large-cnn`).
- **Chat**: Users can interact with the uploaded PDF by asking questions. The backend returns answers using the Hugging Face QA model (`deepset/roberta-base-squad2`).
- **Session Management**: Each interaction with the PDF is tracked via a unique session ID, and chat history is stored in the database.
- **End Session**: Users can terminate a session, which deletes all chat history and associated PDF data from the database.

## API Endpoints

### 1. Upload PDF
**POST /upload**

This endpoint allows users to upload a PDF file. The text is extracted from the PDF, and a summary is generated.

- **Request**: A PDF file is uploaded using `multipart/form-data`.
- **Response**: Returns a JSON response with a session ID and the PDF summary.


## Endpoint

### **POST /chat/**

This endpoint enables users to send a question related to the uploaded PDF, and the backend will return the most relevant answer based on the text extracted from the PDF.

#### **Request**

The request body should include the following fields:

- **session_id** (string): A unique identifier for the PDF session. This session ID is generated when the PDF is uploaded.
- **message** (string): The question the user wants to ask about the uploaded PDF.



# Libraries and Modules Used

The "Chat with PDF" API utilizes various libraries and modules to handle different tasks such as PDF extraction, question answering, text processing, and database interaction. Below is a list of the key libraries and modules used:

## Libraries

### **FastAPI**
- **Description**: A modern web framework for building APIs with Python. It is fast and easy to use, and provides automatic validation, interactive API documentation, and more.
- **Usage**: FastAPI is used to define the API routes, handle HTTP requests, and validate input data through Pydantic models.

### **Pydantic**
- **Description**: A data validation and settings management library using Python type annotations.
- **Usage**: Pydantic is used to define request and response models, such as the `ChatRequest` model for the `/chat/` endpoint.

### **SQLAlchemy**
- **Description**: A SQL toolkit and Object Relational Mapper (ORM) for Python. It provides an easy way to interact with databases in Python.
- **Usage**: SQLAlchemy is used for database session management and storing the uploaded PDF content and chat messages.

### **Pdfplumber**
- **Description**: A Python library for extracting text and tables from PDF files.
- **Usage**: Pdfplumber is used to extract text from the uploaded PDF files.

### **Requests**
- **Description**: A simple HTTP library for Python.
- **Usage**: The `requests` library is used to make API calls to Hugging Face's model for both summarization and question answering.

### **Transformers**
- **Description**: Hugging Face’s library for natural language processing (NLP) models.
- **Usage**: The `AutoTokenizer` and model from the Transformers library are used for tokenizing the text and interacting with pre-trained models for question answering and summarization.

### **Scikit-learn**
- **Description**: A machine learning library for Python.
- **Usage**: Scikit-learn's `TfidfVectorizer` is used to convert text into a numerical format and compute cosine similarity to find the most relevant chunks of text.

### **Dotenv**
- **Description**: A library for reading environment variables from a `.env` file.
- **Usage**: Used to load environment variables, such as the Hugging Face API key, from a `.env` file.

## Modules

### **app.database**
- **Description**: Contains database models and session management for SQLAlchemy.
- **Usage**: The `SessionLocal`, `PDFSession`, and `ChatMessage` modules are imported to interact with the database and store session and message data.

### **app.routers**
- **Description**: Contains the FastAPI route definitions.
- **Usage**: The `router` module contains the `/upload`, `/chat/`, and `/chat/end/{session_id}` endpoints, handling file uploads, chat interactions, and session management.

### **app.utils**
- **Description**: Contains utility functions for tasks like text extraction, chunking, and similarity computation.
- **Usage**: Functions like `extract_text`, `split_text_into_chunks`, and `get_most_relevant_chunk` are used to process the PDF content and match user questions to relevant text.

## Summary

- **FastAPI**: For building the API and managing requests.
- **Pydantic**: For request and response validation.
- **SQLAlchemy**: For database management.
- **Pdfplumber**: For extracting text from PDFs.
- **Requests**: For making HTTP requests to Hugging Face APIs.
- **Transformers**: For interacting with pre-trained NLP models.
- **Scikit-learn**: For text processing and similarity calculations.
- **Dotenv**: For environment variable management.

These libraries and modules work together to enable the "Chat with PDF" functionality, allowing users to interact with PDF content through a question-answering API.
