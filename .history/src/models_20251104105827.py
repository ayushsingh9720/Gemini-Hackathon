# src/models.py

from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# --- 1. Database Setup ---
# Use the DATABASE_URL defined in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/resumedb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. Resume Model Definition ---
class Resume(Base):
    """
    Database model for a parsed resume, using JSONB for the content.
    """
    __tablename__ = "resumes"

    # Core required fields
    id = Column(String, primary_key=True, index=True) # Matches the UUID used for the file
    status = Column(String, default="processing")     # e.g., 'processing', 'completed', 'failed'
    file_name = Column(String, index=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # The crucial column for storing AI-extracted structured data
    parsed_data = Column(JSON, nullable=True) 

    # We can add a simple index for easy lookups
    __table_args__ = ({'schema': 'public'},)