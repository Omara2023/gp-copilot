from pydantic import BaseModel
from langgraph.graph import START, END, StateGraph
from docling_core.transforms.chunker.base import BaseChunk
from numpy.typing import NDArray
from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.docling_parser import DoclingParser

class IndexerState(BaseModel):
    path: str
    chunks: list[BaseChunk]
    metadata: list[ClinicalMetadata] #pydantic model to create
    embeddings: NDArray

def chunker(state: IndexerState):
    parser = DoclingParser()
    path = state["path"]
    chunks = parser.process_document(path)
    {"chunks" : chunks}

def embedder(state: IndexerState):
    pass

def metadata_extractor(state: IndexerState):
    pass

def main():
    builder = StateGraph(IndexerState)

    builder.add_node()

if __name__ == "__main__":
    main()