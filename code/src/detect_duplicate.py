import openai
import pinecone
import numpy as np
import uuid
from pinecone import Pinecone

pc = Pinecone(api_key="")
index = pc.Index("email-embedding")

def is_duplicate_email(email_embedding,email_body, threshold=0.9):
    """Detects duplicate emails using Pinecone embeddings."""

    # Search for similar emails in Pinecone
    query_results = index.query(vector=email_embedding, top_k=1, include_metadata=True)

    if query_results["matches"] and query_results["matches"][0]["score"] > 0.85:  # Confidence threshold
        id = query_results["matches"][0]["id"]
        duplicate_metadata = query_results["matches"][0]["metadata"]
        request_type = duplicate_metadata.get("request_type", "Unknown")
        sub_request_type = duplicate_metadata.get("sub_request_type", "Unknown")
        entities = duplicate_metadata.get("entities", {})
        confidence_score = duplicate_metadata.get("confidence_score", 0.0)

        return True, request_type, sub_request_type,entities, confidence_score, "The request already exists with ID - "+id  # Returning multiple values

    return False, None, None, None, None, "New Request"  # No duplicate found


def insert_vector(email_embedding, email_body, request_type, sub_request_type, entities, confidence_score):
    # If no close match found, store this new email
    vector_id = str(uuid.uuid4())
    index.upsert(vectors=[{
    "id": vector_id,  
    "values": email_embedding,  
    "metadata": {
        "email": email_body,
        "request_type": request_type, 
        "sub_request_type": sub_request_type,
        "entities": entities,
        "confidence_score": confidence_score 
    }
}])

