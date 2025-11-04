# src/tasks.py

from .celery_config import celery_app
import time

@celery_app.task(name='src.tasks.process_resume')
def process_resume(job_id: str):
    """
    Simulates the heavy-lifting, long-running resume parsing process.
    """
    print(f"--- Worker received job: {job_id} ---")
    
    # --- STEP 1: DOCUMENT PRE-PROCESSING (e.g., PDF to Text/OCR) ---
    print("Starting document pre-processing...")
    time.sleep(5) # Simulate document extraction time
    
    # --- STEP 2: AI/ML EXTRACTION (e.g., NER) ---
    print("Starting AI/ML data extraction...")
    time.sleep(15) # Simulate model inference time
    
    # --- STEP 3: DATABASE UPDATE ---
    # In a real app, you would save the parsed JSON structure to PostgreSQL here
    print(f"Finished job: {job_id}. Updating database status.")
    
    # Return a result (optional)
    return {"status": "completed", "parsed_fields": ["name", "email", "skills"]}