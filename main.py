import os
import datetime
import logging
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile
from chromadb import CloudClient
# from services.cloud_storage import upload_to_gcs, download_from_gcs
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.clinical_metadata_extractor import ClinicalMetadataExtractor
from indexing_pipeline.chroma_client import ChromaClient
from indexing_pipeline.indexer import Indexer
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# GCS_BUCKET = "..."
MODEL_NAME = os.getenv("MODEL_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME") 
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE= os.getenv("CHROMA_DATABASE")
CHROMA_API_KEY= os.getenv("CHROMA_API_KEY")

app = FastAPI()
client = CloudClient(tenant=CHROMA_TENANT, database=CHROMA_DATABASE, api_key=CHROMA_API_KEY)
indexer = Indexer(DoclingParser(), ClinicalMetadataExtractor(MODEL_NAME), ChromaClient(client, COLLECTION_NAME))

@app.post("/documents")
async def upload_document(file: UploadFile):
    data = await file.read()
    blob_name = f"documents/{file.filename}" #should replace with a uuid for gcs key

    # await upload_to_gcs(data, bucket_name=GCS_BUCKET, blob_name=blob_name)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / file.filename

        # await download_from_gcs(GCS_BUCKET, blob_name, str(path))
        with open(path, "wb") as local:
            local.write(data)
        start = datetime.datetime.now()
        indexer.run(str(path))
        duration = datetime.datetime.now() - start
        logger.info(f"Time to index: {duration.total_seconds()}") #to add proper logging.

    return {"status": "indexed"}

