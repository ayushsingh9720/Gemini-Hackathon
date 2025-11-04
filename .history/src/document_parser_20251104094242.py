# src/document_parser.py

import fitz # PyMuPDF
from docx import Document
from PIL import Image
import pytesseract
from pathlib import Path
import os
import io

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error parsing PDF {file_path}: {e}")
        return ""
    return text

def parse_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error parsing DOCX {file_path}: {e}")
        return ""
    return text

def parse_txt(file_path: str) -> str:
    """Extracts text from a simple TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error parsing TXT {file_path}: {e}")
        return ""

def parse_image_ocr(file_path: str) -> str:
    """Extracts text from an image (or scanned PDF page) using Tesseract OCR."""
    try:
        # Tesseract is usually configured by environment variables.
        # Ensure it's reachable in the Docker container.
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error performing OCR on {file_path}: {e}")
        return ""

def parse_document(file_path: str) -> str:
    """
    Master function to select the appropriate parser based on file extension.
    """
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    if extension == '.pdf':
        text = parse_pdf(file_path)
        # Check if PDF is text-based or scanned. If text is sparse, try OCR.
        if len(text.strip()) < 100:
             print("Warning: PDF text extraction was sparse, attempting OCR...")
             # For a hackathon, we can simplify and assume PDF OCR needs
             # a temporary conversion, which adds complexity. For now, 
             # let's rely on the dedicated OCR function for images/scans
             # but note this is a simplification for a true hybrid PDF.
             return parse_image_ocr(file_path) # Treating the whole file as an image (simple OCR path)
        return text
    
    elif extension in ('.docx', '.doc'):
        return parse_docx(file_path)
    
    elif extension == '.txt':
        return parse_txt(file_path)
    
    elif extension in ('.jpg', '.jpeg', '.png'):
        return parse_image_ocr(file_path)
        
    else:
        print(f"Unsupported format: {extension}")
        return ""

# Add __init__.py if you haven't yet, to make src a package:
# touch src/__init__.py