from dataclasses import dataclass


@dataclass
class TransliterationResult:
    """
    Standard result returned by a transliteration provider.
    """

    text: str
    language: str
    provider: str
    provider_type: str
    confidence: float | None = None