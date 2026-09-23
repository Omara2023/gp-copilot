from langchain_google_genai import GoogleGenerativeAI
from models.clinical_metadata import ClinicalMetadata

class ClinicalMetadataExtractor:

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.llm = GoogleGenerativeAI(model=model, temperature=0)
        self.extractor = self.llm.with_structured_output(ClinicalMetadata)

    def invoke(self, chunk: str) -> ClinicalMetadata:
        prompt = f"""
        Extract clinical metadata from the following medical record chunk.

        Only extract information explicitly present in the chunk.
        Do not infer diagnoses, medications, relationships, or events
        that are not documented.

        Return an empty field when the relevant information is absent.

        Clinical record:
        {chunk}
        """

        return self.extractor.invoke(input=prompt)