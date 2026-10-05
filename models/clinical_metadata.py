from pydantic import BaseModel

class ClinicalMetadata(BaseModel):
    """LLM-extracted clinical metadata from a document chunk."""

    medications: list[str]
    conditions: list[str]
    symptoms: list[str]
    events: list[str]

    def to_chroma_metadata(self, document_id: str, patient_id: str) -> dict:
        return {
            "document_id": document_id,
            "patient_id": patient_id,
            "medications": self.medications or ["__none__"],
            "conditions": self.conditions or ["__none__"],
            "symptoms": self.symptoms or ["__none__"],
            "events": self.events or ["__none__"]
        }