from pydantic import BaseModel

class ClinicalMetadata(BaseModel):
    """Extracted metadata from clinical document chunks."""

    #chunk_id????
    document_id: str
    patient_id: str
    medications: list[str]
    conditions: list[str]
    symptoms: list[str]
    events: list[str]