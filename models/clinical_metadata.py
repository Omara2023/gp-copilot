from pydantic import BaseModel

class ClinicalMetadata(BaseModel):
    """Extracted metadata from clinical document chunks."""

    document_id: str
    patient_id: str
    medications: list[str]
    conditions: list[str]
    symptoms: list[str]
    events: list[str]

    def _to_chroma_metadata(self) -> dict:
        return {
            "document_id": self.document_id,
            "patient_id": self.patient_id,
            "medications": self.medications or ["__none__"],
            "conditions": self.conditions or ["__none__"],
            "symptoms": self.symptoms or ["__none__"],
            "events": self.events or ["__none__"]
        }