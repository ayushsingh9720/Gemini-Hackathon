# src/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import time
import os
# Import the task definition directly for use in the endpoint
from .tasks import process_resume
import uuid
from pathlib import Path
from .tasks import process_resume

# --- 1. FastAPI Application Initialization ---
app = FastAPI(
    title="AI Resume Parser API",
    version="v1",
    description="Intelligent Resume Parser integrated with LLMs."
)

# --- 2. API Endpoints ---

# Health Check Endpoint (Must-Have)
@app.get("/health", summary="Health Check")
async def health_check():
    """
    Checks the status of the API service.
    """
    return {"status": "ok", "message": "Resume Parser API is running!"}


# Placeholder for the main upload endpoint
class UploadResponse(BaseModel):
    id: str
    status: str
    message: str
    estimatedProcessingTime: int

@app.post("/resumes/upload", response_model=UploadResponse, status_code=202, summary="Upload and Parse Resume")
async def upload_resume():
    """
    Simulates the resume upload and asynchronous processing task initiation.
    """
    # Placeholder: Generate a dummy job ID
    dummy_job_id = f"job-{int(time.time())}"
    
    # Send the task to the Celery worker
    # Use .delay() to execute the task asynchronously
    process_resume.delay(dummy_job_id) # <--- USE THE IMPORTED TASK
    
    return UploadResponse(
        id=dummy_job_id,
        status="processing",
        message="Resume uploaded successfully. Processing initiated.",
        estimatedProcessingTime=30 # 30 seconds estimate
    )


# --- 3. Placeholder for Celery Tasks ---
# For now, we'll keep this separate in src/tasks.py for better structure.