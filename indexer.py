from pydantic import BaseModel
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc.document import DoclingDocument
from chromadb import Embeddings
from models.clinical_metadata import ClinicalMetadata
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.chroma_client import ChromaClient

class IndexerState(BaseModel):
    path: str
    document: DoclingDocument
    chunks: list[BaseChunk]
    metadata: list[ClinicalMetadata] 
    embeddings: Embeddings #only necessary if we precompute embeddings with an external model before handoff to chroma

def parse_node(state: IndexerState, config: RunnableConfig) -> dict:
    parser = config["configurable"]["parser"]
    document = parser.read(state["path"])
    return {"document": document}

def chunk_node(state: IndexerState, config: RunnableConfig) -> dict:
    chunker = config["configurable"]["chunker"]
    document = state["document"]
    chunks = chunker.chunk(document)
    return {"chunks" : chunks}

def embed_node(state: IndexerState, config: RunnableConfig) -> dict:
    embedder = config["configurable"]["embedder"]
    vectors = embedder.embed_documents(state["chunks"])
    return {"embeddings": vectors}

def metadata_extract_node(state: IndexerState, config: RunnableConfig) -> dict:
    metadata_extractor = config["configurable"]["metadata_extractor"]
    chunks = state["chunks"]

    metadata = []
    for c in chunks:
        result = metadata_extractor.invoke(c)
        if result:
            metadata.append(result)

    return {"metadata": metadata}


def inject_node(state: IndexerState, config: RunnableConfig) -> dict:
    vector_client = config["configurable"]["vector_client"]
    chunks, metadata = state["chunks"], state["metadatas"]
    ids = [chunk.id for chunk in chunks]

    # if not precomputed_embeddings:
    #     vector_client.add(docuements=chunks, metadatas=metadata, ids=ids) #silent assumption being that we're not using external embeddings and relying on chroma fully
    # else:
    #     vector_client.add(docuements=chunks, metadatas=metadata, ids=ids) 
    #for now just assume no precomputed embeddings.
    vector_client.add(docuements=chunks, metadatas=metadata, ids=ids)
    return {}

def main():
    builder = StateGraph(IndexerState)

    builder.add_node("chunker", chunk_node)
    builder.add_node("metadata_extractor", metadata_extract_node)
    builder.add_node("injector", inject_node)

    builder.add_edge(START, "chunker")
    builder.add_edge("chunker", "injector")
    #can worry about parallelism and precomputing vectors next.
    builder.add_edge("injector", END)
    
    app = builder.compile()

    app.invoke()

if __name__ == "__main__":
    main()