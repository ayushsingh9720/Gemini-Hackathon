# src/crud.py

from sqlalchemy.orm import Session
from typing import Dict, Any
from .models import Resume, SessionLocal

# Dependency to get the database session (used in FastAPI endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD function to create a new resume record
def create_resume_record(db: Session, resume_id: str, file_name: str, status: str = "processing"):
    db_resume = Resume(
        id=resume_id,
        file_name=file_name,
        status=status
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

# CRUD function to update the parsed data after AI processing
def update_resume_data(db: Session, resume_id: str, parsed_data: Dict[str, Any], status: str = "completed"):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if db_resume:
        db_resume.parsed_data = parsed_data
        db_resume.status = status
        db.commit()
        db.refresh(db_resume)
        return db_resume
    return None

# CRUD function to retrieve data for the API endpoint
def get_resume(db: Session, resume_id: str):
    return db.query(Resume).filter(Resume.id == resume_id).first()