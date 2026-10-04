from abc import ABC, abstractmethod

class CloudStorageClient:
    """Interface to run io to/from a set cloud storage bucket."""

    @abstractmethod
    async def upload(self, file_bytes: bytes, blob_name: str) -> None:
        pass

    @abstractmethod
    async def download(self, blob_name: str, destination: str) -> None:
        pass