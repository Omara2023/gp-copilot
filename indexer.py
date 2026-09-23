from pydantic import BaseModel
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig
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

def document_processing_node(state: IndexerState, config: RunnableConfig) -> dict:
    parser = config["configurable"]["parser"]
    document = parser.read(state["path"])
    chunks = parser.chunk(document)
    return {"document": document, "chunks": chunks}

def metadata_extraction_node(state: IndexerState, config: RunnableConfig) -> dict:
    metadata_extractor = config["configurable"]["metadata_extractor"]
    chunks = state["chunks"]

    metadata = []
    for c in chunks:
        result = metadata_extractor.invoke(c)
        metadata.append(result)

    return {"metadata": metadata}

def injection_node(state: IndexerState, config: RunnableConfig) -> dict:
    vector_client = config["configurable"]["vector_client"]
    chunks, metadata = state["chunks"], state["metadata"]
    ids = [chunk.id for chunk in chunks]
    vector_client.add(docuements=chunks, metadatas=metadata, ids=ids)
    return {}

def main():
    builder = StateGraph(IndexerState)

    builder.add_node("document_processing", document_processing_node)
    builder.add_node("metadata_extraction", metadata_extraction_node)
    builder.add_node("injection", injection_node)

    builder.add_edge(START, "document_processing")
    builder.add_edge("document_processing", "metadata_extraction_node")
    builder.add_edge("metadata_extraction_node", "injector")
    builder.add_edge("injector", END)
    
    app = builder.compile()
    client = Client()

    config = {
        "configurable": {
            "parser": DoclingParser(),
            "metadata_extractor": ClinicalMetadataExtractor(MODEL_NAME),
            "vector_client": ChromaClient(client, COLLECTION_NAME),
        }
    }

    result = app.invoke(
        {"path": "data/mr_xander.pdf"},
        config=config,
    )

if __name__ == "__main__":
    main()