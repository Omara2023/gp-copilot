from pathlib import Path
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from docling_core.transforms.chunker.base import BaseChunk
from docling.chunking import HybridChunker
from indexing_pipeline.document_parser import DocumentParser

class DoclingParser(DocumentParser):
    """Open source Docling parser."""

    def __init__(self) -> None:
        self.converter = DocumentConverter() 
        self.chunker = HybridChunker() #consider DI for both

    def read(self, path: str) -> DoclingDocument:  
        p = Path(path)
        if p.exists() and p.is_file() and p.name.endswith(".pdf"):  
            return self.converter.convert(path)
        return DoclingDocument()

    def chunk(self, doc: DoclingDocument) -> list[BaseChunk]:
        return [chunk for chunk in self.chunker.chunk(doc)]
        #llm metadata extraction & embedding. this needs to be a langraph parallelisation    
        #could parallelise this with asyncio or do langrpaph on the collection as a whole, evaluate/consider both.
