import datetime
import logging
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, Depends
from services.cloud_storage_client import CloudStorageClient 
from indexing_pipeline.indexer import Indexer
from dependencies import get_indexer, get_gcs_client

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

app = FastAPI()

@app.post("/documents")
async def upload_document(file: UploadFile, cloud_storage_client: CloudStorageClient = Depends(get_gcs_client), indexer: Indexer = Depends(get_indexer)): 
    data = await file.read()

    if data is None or file.filename is None:
        raise Exception("Uploaded file could not be read.")
    
    blob_name = f"documents/{file.filename}" #should replace with a uuid for gcs key

    await cloud_storage_client.upload(data, blob_name)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / file.filename
        await cloud_storage_client.download(blob_name, str(path))
        start = datetime.datetime.now()
        indexer.run(str(path))
        duration = datetime.datetime.now() - start
        logger.info(f"Time to index: {duration.total_seconds()}") 

    return {"status": "indexed"}

