from models.clinical_metadata import ClinicalMetadata

class MetadataNormaliser:
    """Deduplication and normalisation of metadata strings."""

    def normalise(self, metadata: list[ClinicalMetadata]) -> list[ClinicalMetadata]:
        for item in metadata:
            item.symptoms = self._process(item.symptoms)
            item.conditions = self._process(item.conditions)
            item.medications = self._process(item.medications)
            item.events = self._process(item.events) 

        return metadata

    def _process(self, values: list[str]) -> list[str]:
        normalised = []

        for value in values:
            value = value.lower().strip()
            if value and value not in normalised:
                normalised.append(value)
        
        return normalised