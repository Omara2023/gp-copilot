from pydantic import BaseModel
from langgraph.graph import START, END, StateGraph
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc.document import DoclingDocument
from chromadb import Client
from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.chroma_client import ChromaClient
from indexing_pipeline.clinical_metadata_extractor import ClinicalMetadataExtractor

MODEL_NAME = "gemini-2.5-flash"
COLLECTION_NAME = "clinical_documents" #replace with env variables

class IndexerState(BaseModel):
    path: str
    document: DoclingDocument | None = None
    chunks: list[BaseChunk]
    metadata: list[ClinicalMetadata] 

class Indexer:

    def __init__(self, parser: DoclingParser, metadata_extractor: ClinicalMetadataExtractor, vector_client: ChromaClient):
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
        document = self.parser.read(state["path"])
        chunks = self.parser.chunk(document)
        return {"document": document, "chunks": chunks}

    def metadata_extraction(self, state: IndexerState) -> dict:
        chunks = state["chunks"]
        metadata = []
        for c in chunks:
            result = self.metadata_extractor.invoke(c)
            metadata.append(result)

        return {"metadata": metadata}

    def injection(self, state: IndexerState) -> dict:
        chunks = state["chunks"]
        metadata = [m.model_dump() for m in state["metadata"]]
        ids = [chunk.id for chunk in chunks]
        self.vector_client.add(docuements=chunks, metadatas=metadata, ids=ids)
        return {}

    def run(self, path: str):
        self.graph.invoke({"path": path})

if __name__ == "__main__":
    client = Client()
    indexer = Indexer(DoclingParser(), ClinicalMetadataExtractor(MODEL_NAME), ChromaClient(client, COLLECTION_NAME))
    indexer.run("data/mr_xander.pdf")