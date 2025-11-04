# src/tasks.py (Updates for the parsing logic)

from .celery_config import celery_app
import time
from pathlib import Path
from .document_parser import parse_document # <-- IMPORT THE NEW PARSER
from .ai_parser import process_ai_extraction # <-- IMPORT NEW AI FUNCTION

# NOTE: You will need to re-run docker-compose up --build 
# if you added Pillow/other libraries to requirements.txt

@celery_app.task(name='src.tasks.process_resume')
def process_resume(resume_id: str, file_path: str, file_name: str):
    """
    Handles the heavy-lifting, long-running resume parsing process.
    """
    start_time = time.time()
    print(f"--- Worker received job: {resume_id} for file: {file_name} ---")
    
    try:
        # --- STEP 1: DOCUMENT PRE-PROCESSING (Actual Text Extraction) ---
        print(f"Starting document extraction for: {file_name}...")
        
        raw_text = parse_document(file_path) # <-- CALL THE MASTER PARSING FUNCTION
        
        if not raw_text.strip():
            # If extraction failed, mark as failed
            raise ValueError("Failed to extract meaningful text from document.")
            
        print(f"Successfully extracted {len(raw_text)} characters.")
        
        # --- STEP 2: AI/ML EXTRACTION (To be implemented in Step 5) ---
        print("Starting AI/ML data extraction...")
        
        # Placeholder for structured data result (for now, use the raw text)
        structured_data = {
            "id": resume_id,
            "rawText": raw_text[:500] + "...", # Store beginning of text for debugging
            "status": "extracted",
            "processingTime": round(time.time() - start_time, 2)
        }
        
        time.sleep(10) # Simulate model inference time

        # --- STEP 3: DATABASE UPDATE (To be implemented in Step 5/6) ---
        # Save structured_data to PostgreSQL
        print(f"Finished job: {resume_id}. Updating database status.")
        
    except Exception as e:
        print(f"Critical Error processing {resume_id}: {e}")
        # In a real app, update DB status to 'failed' here
        return {"status": "failed", "error": str(e)}

    # Clean up the raw file after successful processing (optional but good practice)
    # Path(file_path).unlink(missing_ok=True)
    
    return {"status": "completed", "resume_id": resume_id}