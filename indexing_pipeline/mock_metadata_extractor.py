from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.metadata_extractor import MetadataExtractor

class MockMetadataExtractor(MetadataExtractor):
    def invoke(self, chunk: str) -> ClinicalMetadata:
        return {
            "patient_id": "mock-patient",
            "document_type": "mock",
        }