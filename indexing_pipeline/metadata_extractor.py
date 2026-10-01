from abc import ABC, abstractmethod
from models.clinical_metadata import ClinicalMetadata

class MetadataExtractor(ABC):
    """Extract entities from text."""

    @abstractmethod
    def invoke(self, chunk: str) -> ClinicalMetadata:
        pass

    