from sqlalchemy import create_engine, Column, String, Text, ForeignKey,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# SQLite database file

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session Local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()

class PDFSession(Base):
    __tablename__ = "pdf_sessions"

    session_id = Column(String, primary_key=True, index=True)
    pdf_name = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)

    # Establish relationship with ChatMessage
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("pdf_sessions.session_id"), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("PDFSession", back_populates="messages")
Base.metadata.create_all(bind=engine)
