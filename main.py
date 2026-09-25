import datetime
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile
from chromadb import Client
from services.cloud_storage import upload_to_gcs, download_from_gcs
from indexing_pipeline.docling_parser import DoclingParser
from indexing_pipeline.clinical_metadata_extractor import ClinicalMetadataExtractor
from indexing_pipeline.chroma_client import ChromaClient
from indexing_pipeline.indexer import Indexer

GCS_BUCKET = "..."
MODEL_NAME = "gemini-2.5-flash"
COLLECTION_NAME = "clinical_documents" #replace with env variables

app = FastAPI()
client = Client()
indexer = Indexer(DoclingParser(), ClinicalMetadataExtractor(MODEL_NAME), ChromaClient(client, COLLECTION_NAME))

@app.post("/documents")
async def upload_document(file: UploadFile):
    data = await file.read()
    blob_name = f"documents/{file.filename}" #should replace with a uuid for gcs key

    await upload_to_gcs(data, bucket_name=GCS_BUCKET, blob_name=blob_name)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / file.filename

        await download_from_gcs(GCS_BUCKET, blob_name, str(path))
        start = datetime.datetime.now()
        indexer.run(path)
        duration = start - datetime.datetime.now()
        print(f"Time to index: {duration.total_seconds()}") #to add proper logging.

    return {"status": "indexed"}

