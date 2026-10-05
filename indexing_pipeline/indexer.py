import uuid
import logging
from pydantic import BaseModel, Field
from langgraph.graph import START, END, StateGraph
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc.document import DoclingDocument
from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.vector_client import VectorClient
from indexing_pipeline.clinical_metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)

class IndexerState(BaseModel):
    path: str
    document_id: str
    patient_id: str
    
    document: DoclingDocument | None = None
    chunks: list[BaseChunk] = Field(default_factory=list)
    metadata: list[ClinicalMetadata] = Field(default_factory=list)

class Indexer:
    """Indexing pipeline for GP Copilot."""
    
    def __init__(self, parser: DoclingParser, metadata_extractor: MetadataExtractor, vector_client: VectorClient):
        self.parser = parser
        self.metadata_extractor = metadata_extractor
        self.vector_client = vector_client

        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(IndexerState)
        
        builder.add_node("document_processing", self.document_processing)
        builder.add_node("metadata_extraction", self.metadata_extraction)
        builder.add_node("injection", self.injection)
    
        builder.add_edge(START, "document_processing")
        builder.add_edge("document_processing", "metadata_extraction")
        builder.add_edge("metadata_extraction", "injection")
        builder.add_edge("injection", END)
        
        return builder.compile()

    def document_processing(self, state: IndexerState) -> dict:
        document = self.parser.parse(state.path)
        chunks = self.parser.chunk(document)
        return {"document": document, "chunks": chunks}

    def metadata_extraction(self, state: IndexerState) -> dict:
        logger.info("Executing metadata extraction node")
        chunks = state.chunks
        metadata = []
        for c in chunks:
            result = self.metadata_extractor.invoke(c.text)
            metadata.append(result)
            logger.debug("Chunk: %s", c)
            logger.debug("Extracted clinical metadata: %s", result)

        return {"metadata": metadata}

    def injection(self, state: IndexerState) -> dict:
        document_id, patient_id = state.document_id, state.patient_id

        documents = [chunk.text for chunk in state.chunks]
        metadata = [m.to_chroma_metadata(document_id, patient_id) for m in state.metadata]
        ids = [str(uuid.uuid4()) for _ in documents]
        
        self.vector_client.add(documents=documents, metadata=metadata, ids=ids)
        return {}

    def run(self, path: str, document_id: str, patient_id: str):
        self.graph.invoke({"path": path, "document_id": document_id, "patient_id": patient_id}) # type: ignore