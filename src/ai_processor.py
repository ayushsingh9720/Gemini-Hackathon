from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from typing import List, Dict, Any
import numpy as np
# ------------------------------------------------------------------
# 🔑 LOCATION: Import the library needed for semantic matching
from sentence_transformers import SentenceTransformer, util
# ------------------------------------------------------------------

# --- 1. Model Setup ---
# General NER model (used for parsing)
NER_MODEL_NAME = "dslim/bert-base-NER" 

# Semantic Similarity model (Used for matching)
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' 

# ... (rest of the file remains the same, assuming you implemented 
#      the calculate_match_score function using this import)
