from pathlib import Path
from docling.document_converter import DocumentConverter
from indexing_pipeline.document_parser import DocumentParser

class DoclingParser(DocumentParser):
    """Open source Docling parser."""

    def __init__(self) -> None:
        self.converter = DocumentConverter()

    def __parse__(self, path: str) -> str:  
        p = Path(path)
        if p.exists() and p.is_file() and p.name.endswith(".pdf"):  
            result = self.converter.convert(path)
            return result.document.export_to_text()
        return ""