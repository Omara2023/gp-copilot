from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.clinical_metadata import ClinicalMetadata

class ClinicalMetadataExtractor:

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.llm = GoogleGenerativeAI(model=model, temperature=0)

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
                You extract structured metadata from clinical records.

                Extract only information explicitly stated in the supplied
                record chunk. Never infer or invent clinical information.

                Identify relevant patient identifiers, medications,
                conditions, symptoms and clinical incidents.

                If information is not present, leave the corresponding
                field empty.
                """
            ),
            (
                "human",
                "{chunk}"
            ),
        ])

        self.chain = (
            prompt
            | self.llm.with_structured_output(ClinicalMetadata)
        )

    def invoke(self, chunk: str) -> ClinicalMetadata:
        return self.chain.invoke(input={"chunk": chunk})