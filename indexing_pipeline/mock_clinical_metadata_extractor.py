from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.metadata_extractor import MetadataExtractor

class MockClinicalMetadataExtractor(MetadataExtractor):
    def invoke(self, chunk: str):
        return ClinicalMetadata(
            patient_id="mock-patient",
            document_id="mock-document",
            medications=[],
            conditions=[],
            symptoms=[],
            events=[],
            document_type="mock",
        )