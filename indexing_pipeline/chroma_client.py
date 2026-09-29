from chromadb.api import ClientAPI
from models.clinical_metadata import ClinicalMetadata

class ChromaClient:
    """Wrapper to interact with chromadb vector database."""

    def __init__(self, client: ClientAPI, name: str):
        self.client = client
        self.collection = self.client.get_or_create_collection(name=name)

    def add(self, documents: list[str], metadata: list[dict], ids: list[str]):
        self.collection.add(documents=documents, metadatas=metadata, ids=ids)

    def query(self, query: str, k: int = 5, metadata_filter: dict | None = None):
        results = self.collection.query(query_texts=[query], k=k, where=metadata_filter)
        return results

    def _to_chroma_metadata(self, metadata: ClinicalMetadata) -> dict: #consider moving to clinical metadata model itself.
        return {
            "document_id": metadata.document_id,
            "patient_id": metadata.patient_id,
            "medications": metadata.medications or ["__none__"],
            "conditions": metadata.conditions or ["__none__"],
            "symptoms": metadata.symptoms or ["__none__"],
            "events": metadata.events or ["__none__"],
        }