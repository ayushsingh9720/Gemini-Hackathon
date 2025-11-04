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



# Define the directory where raw resumes will be stored (needs a Docker volume mount)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True) # Ensure the directory exists

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

# src/main.py (Updated upload_resume function)

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import time
import os
import uuid
from pathlib import Path
from .tasks import process_resume

# Define the directory where raw resumes will be stored
# NOTE: This must be accessible via the shared volume mount (. : /app)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True) # Ensure the directory exists when the API starts

# Define the response model and main app (assuming these are defined elsewhere)
# ... (App init and response model definition) ...

@app.post("/resumes/upload", response_model=UploadResponse, status_code=202, summary="Upload and Parse Resume")
async def upload_resume(
    file: UploadFile = File(..., description="The resume file (PDF, DOCX, TXT, etc.)"),
    # options: Optional[str] = None # Will be implemented later
):
    """
    Handles file validation, saves the resume, and queues an asynchronous task 
    for AI-powered parsing.
    """
    # --- 1. File Validation and Storage ---
    
    # 1.1. Check file size (Max 10MB requirement)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Read the file content in chunks to get size without loading entire file into memory (better for large files)
    file_contents = await file.read()
    if len(file_contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="File size exceeds the 10MB limit."
        )

    # 1.2. Generate a unique ID for the resume/job (The 'id' in the response)
    resume_id = str(uuid.uuid4())
    
    # 1.3. Define the file path using the unique ID and the original extension
    file_extension = Path(file.filename).suffix.lower()
    file_path = UPLOAD_DIR / f"{resume_id}{file_extension}"
    
    # 1.4. Save the file content
    try:
        # We use 'file_contents' saved from the size check for efficiency
        with open(file_path, "wb") as f:
            f.write(file_contents)
            
    except Exception as e:
        # Ideally, log the error to a service (e.g., Sentry)
        print(f"File Save Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file on the server.")

    # --- 2. Queue the Parsing Task ---
    
    # Pass the unique resume ID and the full path to the file to the Celery worker
    process_resume.delay(
        resume_id=resume_id, 
        file_path=str(file_path), 
        file_name=file.filename
    )
    
    return UploadResponse(
        id=resume_id,
        status="processing",
        message=f"Resume '{file.filename}' uploaded and queued for processing.",
        estimatedProcessingTime=30
    )


# --- 3. Placeholder for Celery Tasks ---
# For now, we'll keep this separate in src/tasks.py for better structure.