from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Path as FastAPIPath
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import datetime
import os
import uuid
import time
from pathlib import Path

# Project specific imports
from .tasks import process_resume
from .crud import create_resume_record, get_db, get_resume
from .models import Resume as ResumeDBModel # Import the SQLAlchemy Model
from .matching import calculate_match_score # Import the matching logic

# Define the directory where raw resumes will be stored
UPLOAD_DIR = Path("uploads")
# Ensure the directory exists when the API starts. This is safe to run multiple times.
UPLOAD_DIR.mkdir(exist_ok=True) 

# --- 1. FastAPI Application Initialization ---
app = FastAPI(
    title="AI Resume Parser API",
    version="v1",
    description="Intelligent Resume Parser integrated with LLMs."
)

# --- 2. Pydantic Models (API Response Schemas) ---

class UploadResponse(BaseModel):
    """Response model for a successful resume upload initiation."""
    id: str
    status: str
    message: str
    estimatedProcessingTime: int

class ResumeDataResponse(BaseModel):
    """Response model for retrieving full parsed data (matches the DB model)."""
    id: str
    status: str
    file_name: str
    uploaded_at: datetime.datetime
    # Note: parsed_data is optional as it will be NULL during 'processing'
    parsed_data: Optional[Dict[str, Any]] = None 
    
    # Configuration to handle SQLAlchemy model
    class Config:
        from_attributes = True

class JobRequirementsInput(BaseModel):
    required: Optional[list[str]] = []
    preferred: Optional[list[str]] = []

class JobDescriptionInput(BaseModel):
    title: str
    description: str
    requirements: JobRequirementsInput

class MatchOptionsInput(BaseModel):
    includeExplanation: Optional[bool] = True

class MatchRequestInput(BaseModel):
    jobDescription: JobDescriptionInput
    options: MatchOptionsInput

class MatchResultResponse(BaseModel):
    matchId: str
    overallScore: int
    recommendation: str
    explanation: Dict[str, Any]
    categoryScores: Dict[str, Any]
    gapAnalysis: Dict[str, Any]


# --- 3. API Endpoints ---

# Health Check Endpoint (Must-Have)
@app.get("/health", summary="Health Check")
async def health_check():
    """
    Checks the status of the API service.
    """
    return {"status": "ok", "message": "Resume Parser API is running!"}


@app.post("/resumes/upload", response_model=UploadResponse, status_code=202, summary="Upload and Parse Resume")
async def upload_resume(
    file: UploadFile = File(..., description="The resume file (PDF, DOCX, TXT, etc.)"),
    db: Session = Depends(get_db) # Dependency Injection for DB session
):
    """
    Handles file validation, saves the resume, creates a DB record, and queues 
    an asynchronous task for AI-powered parsing.
    """
    # --- 1. File Validation and Storage ---
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Read the file content for size check and saving
    file_contents = await file.read()
    if len(file_contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="File size exceeds the 10MB limit."
        )

    # Generate unique ID and file path
    resume_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix.lower()
    file_path = UPLOAD_DIR / f"{resume_id}{file_extension}"
    
    # Save the file content
    try:
        with open(file_path, "wb") as f:
            f.write(file_contents)
            
    except Exception as e:
        print(f"File Save Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file on the server.")

    # --- 2. Database Record Creation ---
    try:
        # Create the initial DB record with status="processing"
        new_record = create_resume_record(db, resume_id, file.filename)
    except Exception as e:
        # DB failure: clean up the file and raise error
        print(f"DB Record Creation Error: {e}")
        Path(file_path).unlink(missing_ok=True) 
        raise HTTPException(status_code=500, detail="Failed to create initial database record.")
        
    # --- 3. Queue the Parsing Task ---
    
    # Pass necessary data to the Celery worker
    process_resume.delay(
        resume_id=resume_id, 
        file_path=str(file_path), 
        file_name=file.filename
    )
    
    return UploadResponse(
        id=resume_id,
        status=new_record.status, 
        message=f"Resume '{file.filename}' uploaded and queued for processing.",
        estimatedProcessingTime=30
    )

# Retrieve Parsed Data Endpoint (Must-Have)
@app.get("/resumes/{id}", response_model=ResumeDataResponse, summary="Retrieve Parsed Resume Data")
def retrieve_parsed_data(id: str, db: Session = Depends(get_db)):
    """
    Retrieves the complete resume record, including parsed data (if available).
    """
    db_resume = get_resume(db, id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # The ResumeDBModel can be returned directly because of the Config setting
    return db_resume 

# Parsing Status Endpoint (Must-Have)
@app.get("/resumes/{id}/status", summary="Get Parsing Status")
def get_parsing_status(id: str, db: Session = Depends(get_db)):
    """
    Returns the current processing status of a resume job.
    """
    db_resume = get_resume(db, id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    return {"id": db_resume.id, "status": db_resume.status}

# Resume-Job Matching Endpoint (Advanced Feature - High Points!)
@app.post("/resumes/{id}/match", response_model=MatchResultResponse, summary="Match Resume with Job Description")
def match_resume(
    match_request: MatchRequestInput,  # Non-default, request body goes first
    id: str = FastAPIPath(..., description="The Resume UUID"), # Default value goes second
    db: Session = Depends(get_db)
):
    """
    Performs an AI-powered comparison between a parsed resume and a job description.
    """
    db_resume = get_resume(db, id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if db_resume.status != "completed" or not db_resume.parsed_data:
        raise HTTPException(
            status_code=409, 
            detail="Resume parsing not complete. Current status: " + db_resume.status
        )

    # Use the imported logic to calculate the score
    match_results = calculate_match_score(db_resume, match_request.dict())

    return MatchResultResponse(
        matchId=str(uuid.uuid4()),
        **match_results
    )
