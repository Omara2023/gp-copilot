from chromadb import Client
from chromadb.api import ClientAPI

COLLECTION_NAME = "clinical_documents" #replace with env variables

class ChromaClient:
    """Wrapper to interact with chromadb vector database."""

    def __init__(self, client: ClientAPI, name: str):
        self.client = client
        self.collection = self.client.get_or_create_collection(name=name)

    def add(self, docuements: list[str], metadatas: list[dict], ids: list[str]):
        self.collection.add(documents=docuements, metadatas=metadatas, ids=ids)

    def query(self, query: str, k: int = 5, metadata_filter: dict = {}):
        results = self.collection.query(query_texts=[query], k=k, where=metadata_filter)
        return results