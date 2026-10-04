from services.cloud_storage_client import CloudStorageClient
from google.cloud import storage

class GCSClient(CloudStorageClient):
    """Wrapper for GCS upload and download with a single bucket."""

    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(self.bucket_name)

    async def upload(self, file_bytes: bytes, blob_name: str) -> None:
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(file_bytes, content_type="application/pdf")

    async def download(self, blob_name: str, destination: str) -> None:
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination)