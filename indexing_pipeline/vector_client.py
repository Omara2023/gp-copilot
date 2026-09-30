from abc import ABC, abstractmethod

class VectorClient(ABC):
    """Client interface for interacting with vector databases."""

    @abstractmethod
    def add(self, documents: list[str], metadata: list[dict], ids: list[str]):
        pass

    @abstractmethod
    def query(self, query: str, k: int = 5, metadata_filter: dict | None = None):
        pass
