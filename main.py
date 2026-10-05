import datetime
import logging
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from services.cloud_storage_client import CloudStorageClient 
from indexing_pipeline.indexer import Indexer
from models.index_request import IndexRequest
from dependencies import get_indexer, get_gcs_client

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

app = FastAPI()

@app.post("/documents")
async def upload_document(
    document_id: str = Form(...),
    patient_id: str = Form(...),
    file: UploadFile = File(...),
    cloud_storage_client: CloudStorageClient = Depends(get_gcs_client),
    indexer: Indexer = Depends(get_indexer)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    data = await file.read()

    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    request = IndexRequest(document_id=document_id, patient_id=patient_id)
    blob_name = f"documents/{request.document_id}.pdf"
    await cloud_storage_client.upload(data, blob_name)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{request.document_id}.pdf"

        await cloud_storage_client.download(blob_name, str(path))

        start = datetime.datetime.now()
        indexer.run(path=str(path), document_id=request.document_id,patient_id=request.patient_id)
        duration = datetime.datetime.now() - start

        logger.info("Time to index: %.2f seconds", duration.total_seconds())

    return {"status": "indexed", "document_id": request.document_id, "patient_id": request.patient_id}