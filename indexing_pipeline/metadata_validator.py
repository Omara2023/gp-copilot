import logging
from dataclasses import dataclass, field
from models.clinical_metadata import ClinicalMetadata

logger = logging.getLogger(__name__)

CLINICAL_FIELDS = ("medications", "conditions", "symptoms", "events")

@dataclass
class MetadataValidationResult:
    valid: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

class MetadataValidator:
    """Deterministic validation of LLM-extracted clinical metadata. Determines correct syntactic correctness for indexing, not medical soundness."""

    def validate(self, metadata: ClinicalMetadata, source_text: str | None = None) -> MetadataValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        for field_name in CLINICAL_FIELDS:
            values = getattr(metadata, field_name)
            self._validate_values(field_name, values, errors, warnings)
            if source_text:
                self._check_source_correspondence(field_name, values, source_text, warnings)

        return MetadataValidationResult(valid=not errors, warnings=warnings, errors=errors)

    @staticmethod
    def _validate_values(field_name: str, values: list[str], errors: list[str], warnings: list[str]) -> None:
        if not isinstance(values, list):
            errors.append(f"{field_name} is not a list")
            return

        for value in values:
            if not isinstance(value, str):
                errors.append(f"{field_name} contains a non-string value: {value!r}")
                continue

            if not value.strip():
                errors.append(f"{field_name} contains an empty value")

        normalised = [value.strip().lower() for value in values if isinstance(value, str)]

        if len(normalised) != len(set(normalised)):
            errors.append(f"{field_name} contains duplicate values")

        if len(values) > 50:
            warnings.append(f"{field_name} contains {len(values)} values; this is unusually large for a single chunk")

    @staticmethod
    def _check_source_correspondence(field_name: str, values: list[str], source_text: str, warnings: list[str]) -> None:
        source = source_text.lower()

        for value in values:
            value_normalised = value.strip().lower()
            if value_normalised and value_normalised not in source:
                warnings.append(f"{field_name} value {value!r} does not appear verbatim in the source chunk")