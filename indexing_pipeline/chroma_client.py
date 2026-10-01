from chromadb.api import ClientAPI
from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.vector_client import VectorClient

class ChromaClient(VectorClient):
    """Wrapper to interact with chromadb database."""

    def __init__(self, client: ClientAPI, name: str):
        self.client = client
        self.collection = self.client.get_or_create_collection(name=name)

    def add(self, documents: list[str], metadata: list[dict], ids: list[str]):
        self.collection.add(documents=documents, metadatas=metadata, ids=ids)

    def query(self, query: str, k: int = 5, metadata_filter: dict | None = None):
        results = self.collection.query(query_texts=[query], k=k, where=metadata_filter)
        return results