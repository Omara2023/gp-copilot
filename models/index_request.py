from pydantic import BaseModel

class IndexRequest(BaseModel):
    """Incoming POST request data."""
    document_id: str
    patient_id: str