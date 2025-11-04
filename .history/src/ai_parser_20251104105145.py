# src/ai_parser.py

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from typing import List, Dict, Any

# --- 1. Model Setup ---
# For a hackathon, we'll use a pre-trained model fine-tuned for NER
# A popular choice for fine-tuning on custom entities is a BERT/RoBERTa variant.
# NOTE: Replace 'path/to/your/custom/model' with a real Hugging Face model or your fine-tuned model path later.
# For simplicity, let's use a robust general NER model for demonstration.
MODEL_NAME = "dslim/bert-base-NER" # A general NER model. You'd train a custom one for higher accuracy.

try:
    # Initialize the NER pipeline (This will download the model the first time)
    ner_pipeline = pipeline(
        "ner", 
        model=MODEL_NAME, 
        tokenizer=MODEL_NAME, 
        aggregation_strategy="simple"
    )
except Exception as e:
    print(f"Warning: Could not load NER model. Running in simulation mode. Error: {e}")
    ner_pipeline = None

# --- 2. Post-Processing Function ---

def group_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Groups and structures the flat list of extracted entities into the required JSON structure.
    This is the most complex step and requires sophisticated custom logic.
    For the hackathon, we'll implement a simplified version.
    """
    structured_data = {
        "personalInfo": {"name": "", "contact": {"email": "", "phone": ""}},
        "experience": [],
        "education": [],
        "skills": {"technical": [], "soft": []}
    }
    
    # Simplified mapping (Requires customization for resume-specific models)
    current_experience = None
    
    for entity in entities:
        label = entity['entity_group']
        word = entity['word'].strip()
        
        if label == 'PER': # Person (Name)
            structured_data['personalInfo']['name'] += word + " "
        elif label == 'ORG': # Organization (Company/Institution)
            if current_experience is None or 'title' in current_experience:
                # Simple logic to start a new experience block
                current_experience = {"company": word, "title": "", "duration": "TBD"}
                structured_data['experience'].append(current_experience)
            else:
                 current_experience['company'] = word
        elif label == 'MISC': # Catch-all, often includes skills or titles in general NER
             if "engineer" in word.lower() or "developer" in word.lower():
                 if current_experience:
                      current_experience['title'] = word
             elif len(word) > 2:
                 # Simple filtering for short words
                 structured_data['skills']['technical'].append(word)
        
        # NOTE: Custom logic for dates, skills, and address needs a resume-specific NER model.

    # Clean up name and deduplicate skills
    structured_data['personalInfo']['name'] = structured_data['personalInfo']['name'].strip()
    structured_data['skills']['technical'] = sorted(list(set(structured_data['skills']['technical'])))
    
    return structured_data

# --- 3. Main AI Processing Function ---

def process_ai_extraction(raw_text: str) -> Dict[str, Any]:
    """
    Runs NER on the raw text and structures the result.
    """
    if not ner_pipeline:
        # Simulation Mode
        print("Running AI extraction in SIMULATION MODE.")
        return {
            "personalInfo": {"name": "John Doe (Simulated)", "contact": {"email": "sim@example.com", "phone": "555-555-5555"}},
            "experience": [{"title": "Software Engineer", "company": "Simulated Tech Co.", "duration": "5 years"}],
            "skills": {"technical": ["Python", "Docker", "AWS", "Simulated Skill"], "soft": ["Leadership"]}
        }
        
    print("Running Hugging Face NER pipeline...")
    
    # 3.1. Run Model Inference
    ner_results = ner_pipeline(raw_text)
    
    # 3.2. Post-Process and Structure
    structured_json = group_entities(ner_results)
    
    # 3.3. Add required status and metadata
    structured_json['status'] = 'parsed'
    
    return structured_json