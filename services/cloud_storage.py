from google.cloud import storage

#consider putting this into a class to encapsulate function and have one shared client via DI.

storage_client = storage.Client()

async def upload_to_gcs(file_bytes: bytes, bucket_name: str, blob_name: str) -> None:
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(file_bytes, content_type="application/pdf")

async def download_from_gcs(bucket_name: str, blob_name: str, destination: str) -> None:
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.download_to_filename(destination)
