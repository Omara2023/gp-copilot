from indexing_pipeline.vector_client import VectorClient

class MockVectorClient(VectorClient):
    """Wrapper to interact with chromadb database."""

    def __init__(self, name: str):
        self.name = name 

    def add(self, documents: list[str], metadata: list[dict], ids: list[str]):
        print(f"{len(documents)} successfully added.")

    def query(self, query: str, k: int = 5, metadata_filter: dict | None = None):
        results = {"document": "The cat sat on the mat.", "metadata": {"author": "Bobbington"}}
        return results