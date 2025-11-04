
from sentence_transformers import SentenceTransformer, util
from typing import Dict, Any
import torch

# --- 1. Model Initialization ---
# Using a good all-around model for text embedding/semantic search
MODEL_NAME = 'all-MiniLM-L6-v2' 
try:
    # Check if a GPU is available, otherwise use CPU (safer for Docker)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer(MODEL_NAME, device=device)
    print(f"INFO: Matching model loaded successfully on {device}.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to load SentenceTransformer model. Matching will return default score. Error: {e}")
    model = None

# --- 2. Helper Functions ---

def get_text_from_data(resume_data: Any) -> str:
    """Extracts and concatenates relevant text fields for matching."""
    
    # Access the parsed JSON data correctly from the SQLAlchemy model attribute
    data = resume_data.parsed_data or {}
    
    text_parts = []
    
    # 1. Summary
    summary = data.get('summary', {}).get('text', '')
    if summary:
        text_parts.append(summary)

    # 2. Skills
    technical_skills = data.get('skills', {}).get('technical', [])
    
    # Handle the complex nested structure of skills
    if isinstance(technical_skills, list):
        for category in technical_skills:
            if isinstance(category, dict) and 'items' in category:
                text_parts.extend(category['items'])
            elif isinstance(category, str):
                text_parts.append(category)

    # 3. Experience descriptions (simplified)
    for exp in data.get('experience', []):
        text_parts.append(exp.get('title', ''))
        text_parts.append(exp.get('description', ''))
        
    return " ".join([p for p in text_parts if p]).strip()

def calculate_semantic_score(resume_text: str, job_description_text: str) -> float:
    """Calculates semantic similarity using Sentence Transformers."""
    # Ensure model is loaded and inputs exist before attempting calculation
    if model is None or not resume_text or not job_description_text:
        return 0.0

    try:
        # Encode the texts into embeddings
        embeddings = model.encode([resume_text, job_description_text], convert_to_tensor=True, device=model.device)
        
        # Calculate cosine similarity
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
        
        # Scale score from -1 to 1 to 0 to 100 for easier interpretation
        score = (cosine_scores.item() + 1) / 2 * 100
        return score
        
    except Exception as e:
        # Catch any internal Torch/Transformer errors gracefully
        print(f"Error during semantic embedding: {e}")
        return 0.0

# --- 3. Main Matching Function ---

def calculate_match_score(resume_data: Any, job_description_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combines skill matching and semantic similarity into a single score.
    """
    
    # Fallback structure to ensure the endpoint always returns a valid response
    fallback_response = {
        "overallScore": 50,
        "recommendation": "Needs Review (AI Matching Failed)",
        "explanation": {"summary": "An internal error prevented the semantic matching from running. Manual review required.", "keyFactors": []},
        "categoryScores": {},
        "gapAnalysis": {},
    }

    # CRITICAL FIX: The logic must be inside try/except block to prevent 500 error
    try:
        # Extract Text for semantic matching
        resume_text = get_text_from_data(resume_data)
        job_description_text = job_description_input['jobDescription'].get('description', '')
        
        # Simple Skill Match (Rule-based score)
        required_skills = [s.lower() for s in job_description_input['jobDescription'].get('requirements', {}).get('required', [])]
        
        # Access the parsed data for skills correctly
        parsed_skills_data = resume_data.parsed_data.get('skills', {})
        extracted_skills_list = parsed_skills_data.get('technical', [])
        
        # Flatten skills into a single list of strings
        extracted_skills = []
        if isinstance(extracted_skills_list, list):
            for item in extracted_skills_list:
                if isinstance(item, dict) and 'items' in item:
                    extracted_skills.extend([s.lower() for s in item['items']])
                elif isinstance(item, str):
                    extracted_skills.append(item.lower())

        matched_count = len(set(required_skills) & set(extracted_skills))
        total_required = len(required_skills) if required_skills else 1
        
        skill_score = (matched_count / total_required) * 100 * 0.40 # 40% weight
        
        # Semantic Score (LLM/Transformer-based score)
        semantic_score = calculate_semantic_score(resume_text, job_description_text) * 0.60 # 60% weight
        
        # Combined Score
        final_score = int(skill_score + semantic_score)
        
        recommendation = "Strong Match" if final_score >= 80 else ("Good Match" if final_score >= 60 else "Needs Development")

        return {
            "overallScore": final_score,
            "recommendation": recommendation,
            "explanation": {
                "summary": f"Combined similarity analysis resulted in a score of {final_score}. Semantic match was highly weighted.",
                "keyFactors": [
                    f"Semantic similarity contributes {round(semantic_score)} points.",
                    f"Rule-based skill match achieved {round(skill_score)} points.",
                    f"Matched {matched_count} out of {total_required} core skills."
                ]
            },
            "categoryScores": {
                "skillsMatch": {"score": int(skill_score / 0.4)}, # Return original 0-100 score
                "semanticMatch": {"score": int(semantic_score / 0.6)}, # Return original 0-100 score
            },
            "gapAnalysis": {
                "missingSkills": list(set(required_skills) - set(extracted_skills)),
                "improvementAreas": ["Enhance quantifiable achievements.", "Include more industry-specific jargon."],
            }
        }
        
    except Exception as e:
        # If anything in the complex logic fails, catch it and return the safe fallback
        print(f"CRITICAL ERROR in calculate_match_score: {e}")
        return fallback_response