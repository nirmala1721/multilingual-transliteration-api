from app.providers.selector import ProviderSelector
from app.detectors.detector_service import (
    detect_text_information,
    SCRIPT_TO_LANGUAGE,
)
from app.services.text_normalization_service import normalize_text


provider_selector = ProviderSelector()


def transliterate_text(text, language=None):
    """
    Transliterate text while supporting both explicit language
    selection and automatic language detection.

    Args:
        text: Input text to transliterate.
        language: Optional requested language. Use None or "auto"
                  for automatic detection.

    Returns:
        Provider-specific transliteration result.

    Raises:
        ValueError: If the language cannot be detected, the requested
                    language does not match the detected language,
                    or no provider is available.
    """

    # Normalize input before detection and transliteration.
    text = normalize_text(text)

    # Detect language and script from the normalized text.
    detection_result = detect_text_information(text)

    detected_language = detection_result["language"]
    detected_script = detection_result["script"]

    # Normalize the requested language.
    requested_language = (
        language.lower().strip()
        if isinstance(language, str)
        else None
    )

    # Treat "auto" the same as no explicit language.
    if requested_language == "auto":
        requested_language = None

    # ============================================================
    # EXPLICIT LANGUAGE VALIDATION
    # ============================================================

    if requested_language is not None:

        # Prefer language-level validation when detection
        # successfully identifies the language.
        if detected_language is not None:

            if requested_language != detected_language:
                raise ValueError(
                    f"Language mismatch: detected language is "
                    f"{detected_language}, but requested language is "
                    f"{requested_language}"
                )

        # If language detection is unavailable, validate using
        # the detected script where possible.
        else:

            expected_language = SCRIPT_TO_LANGUAGE.get(
                detected_script
            )

            if (
                expected_language is not None
                and requested_language != expected_language
            ):
                raise ValueError(
                    f"Language mismatch: detected script is "
                    f"{detected_script}, but requested language is "
                    f"{requested_language}"
                )

    # ============================================================
    # DETERMINE FINAL LANGUAGE
    # ============================================================

    # Explicit language takes priority.
    # Otherwise use automatically detected language.
    final_language = (
        requested_language or detected_language
    )

    if final_language is None:
        raise ValueError(
            "Could not detect the input language"
        )

    # ============================================================
    # PROVIDER SELECTION
    # ============================================================

    provider = provider_selector.get_provider(
        final_language
    )

    if provider is None:
        raise ValueError(
            f"No transliteration provider available for language: "
            f"{final_language}"
        )

    # ============================================================
    # TRANSLITERATION
    # ============================================================

    return provider.transliterate(
        text,
        final_language
    )