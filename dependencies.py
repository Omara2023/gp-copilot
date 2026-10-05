import os
import logging
from chromadb import CloudClient
from dotenv import load_dotenv

from indexing_pipeline.indexer import Indexer
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.clinical_metadata_extractor import ClinicalMetadataExtractor
from indexing_pipeline.chroma_client import ChromaClient

from services.gcs_client import GCSClient

load_dotenv()

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_NAME = os.getenv("MODEL_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME") 
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE= os.getenv("CHROMA_DATABASE")
CHROMA_API_KEY= os.getenv("CHROMA_API_KEY")

if BUCKET_NAME is None:
    raise Exception("Missing BUCKET_NAME.")
elif MODEL_NAME is None:
    raise Exception("Missing MODEL_NAME.")
elif COLLECTION_NAME is None:
    raise Exception("Missing COLLECTION_NAME.")
elif CHROMA_TENANT is None:
    raise Exception("Missing CHROMA_TENANT.")
elif CHROMA_DATABASE is None:
    raise Exception("Missing CHROMA_DATABASE.")
elif CHROMA_API_KEY is None:
    raise Exception("Missing CHROMA_API_KEY")


client = CloudClient(tenant=CHROMA_TENANT, database=CHROMA_DATABASE, api_key=CHROMA_API_KEY)
indexer = Indexer(
    parser=DoclingParser(),
    metadata_extractor=ClinicalMetadataExtractor(MODEL_NAME),
    vector_client=ChromaClient(client=client, name=COLLECTION_NAME),
)

gcs_client = GCSClient(BUCKET_NAME)

def get_indexer() -> Indexer:
    return indexer

def get_gcs_client() -> GCSClient:
    return gcs_client