# src/tasks.py

from .celery_config import celery_app
import time
from pathlib import Path
from .document_parser import parse_document
from .ai_parser import process_ai_extraction
from .crud import create_resume_record, get_db, get_resume

@celery_app.task(name='src.tasks.process_resume')
def process_resume(resume_id: str, file_path: str, file_name: str):
    """
    Handles the heavy-lifting, long-running resume parsing process.
    1. Extracts raw text. 2. Runs AI extraction. 3. Saves results to DB.
    """
    start_time = time.time()
    print(f"--- Worker received job: {resume_id} for file: {file_name} ---")
    
    # Initialize DB session
    db = next(get_db())
    
    try:
        # --- STEP 1: DOCUMENT PRE-PROCESSING (Actual Text Extraction) ---
        print(f"Starting document extraction for: {file_name}...")
        raw_text = parse_document(file_path)
        
        if not raw_text.strip():
            raise ValueError("Failed to extract meaningful text from document.")
            
        print(f"Successfully extracted {len(raw_text)} characters.")
        
        # --- STEP 2: AI/ML EXTRACTION ---
        print("Starting AI/ML data extraction...")
        
        # CALL THE AI FUNCTION CORRECTLY
        structured_data = process_ai_extraction(raw_text)
        
        # Add metadata required by the database/API response structure
        structured_data["metadata"] = {
            "id": resume_id,
            "fileName": file_name,
            "processingTime": round(time.time() - start_time, 2)
        }
        
        # --- STEP 3: DATABASE UPDATE ---
        print(f"Saving structured data for {resume_id}...")
        
        # Update the database record with the final parsed JSON
        update_resume_data(db, resume_id, structured_data, status="completed")
        print(f"Finished job: {resume_id}. Database status updated to 'completed'.")
        
    except Exception as e:
        # If any part of the process fails, update the DB status to 'failed'
        error_message = f"Critical Error processing {resume_id}: {e}"
        print(error_message)
        
        # Attempt to update status to failed
        try:
             update_resume_data(db, resume_id, parsed_data={"error": error_message}, status="failed") 
        except Exception:
             print("Failed to update database with failure status.")

        raise # Re-raise to mark task as failed in Celery

    finally:
        db.close()
        # Clean up the raw file after processing
        Path(file_path).unlink(missing_ok=True)
    
    return {"status": "completed", "resume_id": resume_id}
