from abc import ABC, abstractmethod

class DocumentParser(ABC):
    """Parse PDFs for text."""

    @abstractmethod
    def parse(self, path: str) -> str:
        pass
