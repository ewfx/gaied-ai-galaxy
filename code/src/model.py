import re
import pdfplumber
import docx
import email
from bs4 import BeautifulSoup
import json
import os
import pandas as pd  # Ensure pandas is installed
from mistralai.client import MistralClient
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

from detect_duplicate import insert_vector, is_duplicate_email


# Initialize Mistral API
MISTRAL_API_KEY = ""
client = MistralClient(api_key=MISTRAL_API_KEY)

# Request type definitions
REQUEST_TYPES = {
    "Adjustment": [],
    "AU Transfer": [],
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement - Inbound": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"],
    "Money Movement - Outbound": ["Timebound", "Foreign Currency"],
}

def extract_emailBody_attachments(eml_path, save_dir="attachments/"):
    """Extracts and saves attachments from an EML file."""
    os.makedirs(save_dir, exist_ok=True)
    with open(eml_path, "r", encoding="utf-8") as file:
        msg = email.message_from_file(file)

    attachments = []
    body = ""

    for part in msg.walk():
        if part.get_content_type() == "text/plain" and part.get_content_disposition() is None:
            body = part.get_payload(decode=True).decode(errors="ignore")
        elif part.get_content_type() == "text/html" and part.get_content_disposition() is None:
            html_content = part.get_payload(decode=True).decode(errors="ignore")
            body = BeautifulSoup(html_content, "html.parser").get_text()  # Convert HTML to plain text

        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(save_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                attachments.append(filepath)

    # print(process_attachment(att) for att in attachments)
    extracted_text = body.strip() + "\n" + "\n".join([process_attachment(att) for att in attachments])

    return extracted_text

def process_attachment(file_path):
    """Extracts text from PDF, DOCX, or XLSX attachments."""
    ext = os.path.splitext(file_path)[-1].lower()
    
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    elif ext in [".doc", ".docx"]:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
        return df.to_string()  # Convert table data to text
    
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string()
    
    return "Unsupported file format"

def classify_request(text):
    """Classifies request type using Mistral AI."""
    prompt = f"""
    Categorize the following email content into a predefined request type and sub-request type:
    {text}

    Available request types and subtypes:
    {json.dumps(REQUEST_TYPES, indent=2)}

    

    Return output as JSON with "request_type" and "sub_request_type". If unsure, return 'Unknown'. 
    Also, provide a confidence score between 0 to 1. Classify it request_type as Others and sub_request_type as Unknown if confidence score is less than 0.85. 
    If there are multiple requests detected, return all the valid request types and their sub request types. set the confidence score as confidence_score.
    **Return JSON Format Only (No extra text or explanations):**
    {{
        "request_type": "Category Name",
        "sub_request_type": "Subcategory Name",
        "confidence_score": Confidence Value (0 to 1)
    }}
    """

    messages = [
        {"role": "system", "content": "You are an expert in email classification."},
        {"role": "user", "content": prompt},
    ]

    response = client.chat(model="mistral-small", messages=messages, temperature=0)
    # print(response)
    match = re.search(r"\{.*\}", response.choices[0].message.content, re.DOTALL)
    return  json.loads(match.group())

def extract_entities(text):
    """Extracts entities dynamically using Mistral AI."""
    prompt = f"""
    Extract key details dynamically from the following document:

    {text}

    Return output as JSON with auto-detected field names and values.
    """

    messages = [
        {"role":"system", "content":"Extract structured data from unstructured text."},
        {"role":"user", "content":prompt}
    ]

    response = client.chat(model="mistral-small", messages=messages, temperature=0)
    return response.choices[0].message.content

def get_email_embeddings(text):
    """Generate embeddings using SentenceTransformers (since Mistral does not provide embeddings)."""
    embedding = embedding_model.encode(text, convert_to_numpy=True)
    return embedding.tolist()  # Convert NumPy array to Python list

