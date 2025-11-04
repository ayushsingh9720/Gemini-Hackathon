# src/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import os
# Import the task definition directly for use in the endpoint
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
    # In a real scenario, you'd handle file upload (Multipart),
    # save it to storage, and get its unique ID (UUID).
    
    # Placeholder: Generate a dummy job ID
    dummy_job_id = f"job-{int(time.time())}"
    
    # Send the task to the Celery worker
    # We'll define 'process_resume' in the next step
    # celery_app.send_task('src.tasks.process_resume', args=[dummy_job_id])
    
    return UploadResponse(
        id=dummy_job_id,
        status="processing",
        message="Resume uploaded successfully. Processing initiated.",
        estimatedProcessingTime=30 # 30 seconds estimate
    )


# --- 3. Placeholder for Celery Tasks ---
# For now, we'll keep this separate in src/tasks.py for better structure.