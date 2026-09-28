from app.providers.selector import ProviderSelector
from app.providers.result import TransliterationResult
from app.detectors.detector_service import (
    detect_text_information,
    SCRIPT_TO_LANGUAGE,
)
from app.services.text_normalization_service import normalize_text


provider_selector = ProviderSelector()


# ============================================================
# SCRIPT RANGES
# ============================================================

SCRIPT_RANGES = {
    "telugu": (0x0C00, 0x0C7F),
    "kannada": (0x0C80, 0x0CFF),
    "malayalam": (0x0D00, 0x0D7F),
    "tamil": (0x0B80, 0x0BFF),
    "bengali": (0x0980, 0x09FF),
    "oriya": (0x0B00, 0x0B7F),
    "gujarati": (0x0A80, 0x0AFF),
    "gurmukhi": (0x0A00, 0x0A7F),
    "devanagari": (0x0900, 0x097F),
}


SCRIPT_LANGUAGE = {
    "telugu": "telugu",
    "kannada": "kannada",
    "malayalam": "malayalam",
    "tamil": "tamil",
    "bengali": "bengali",
    "oriya": "odia",
    "gujarati": "gujarati",
    "gurmukhi": "punjabi",
    "devanagari": "hindi",
}


def _get_character_script(character):
    """
    Return the Indian script for a character.

    Latin/English characters and other characters return None.
    """

    code_point = ord(character)

    for script, (start, end) in SCRIPT_RANGES.items():

        if start <= code_point <= end:
            return script

    return None


def _split_mixed_text(text):
    """
    Split text into segments based on Unicode script.

    Indian-script text becomes language-specific segments.
    Latin text is kept as a separate segment.

    Whitespace and punctuation remain attached to the
    surrounding segment as much as possible.
    """

    if not text:
        return []

    segments = []

    current_text = []
    current_script = None

    for character in text:

        character_script = _get_character_script(character)

        # ----------------------------------------------------
        # Indian-script character
        # ----------------------------------------------------

        if character_script is not None:

            if (
                current_text
                and current_script is not None
                and character_script != current_script
            ):
                segments.append(
                    (
                        current_script,
                        "".join(current_text),
                    )
                )

                current_text = []

            elif (
                current_text
                and current_script == "latin"
            ):
                segments.append(
                    (
                        "latin",
                        "".join(current_text),
                    )
                )

                current_text = []

            current_script = character_script
            current_text.append(character)

            continue

        # ----------------------------------------------------
        # Latin / punctuation / whitespace
        # ----------------------------------------------------

        if current_script is None:
            current_script = "latin"

        current_text.append(character)

    if current_text:
        segments.append(
            (
                current_script,
                "".join(current_text),
            )
        )

    # --------------------------------------------------------
    # Merge consecutive Latin segments
    # --------------------------------------------------------

    merged_segments = []

    for script, segment_text in segments:

        if (
            merged_segments
            and script == "latin"
            and merged_segments[-1][0] == "latin"
        ):
            previous_script, previous_text = (
                merged_segments[-1]
            )

            merged_segments[-1] = (
                previous_script,
                previous_text + segment_text,
            )

        else:
            merged_segments.append(
                (
                    script,
                    segment_text,
                )
            )

    return merged_segments


def _transliterate_mixed_text(text):
    """
    Transliterate mixed Indian-language text while preserving
    Latin/English text.

    Example:

        Telugu + English + Hindi

    becomes:

        Telugu transliteration
        + unchanged English
        + Hindi transliteration
    """

    segments = _split_mixed_text(text)

    if not segments:
        raise ValueError(
            "Could not detect the input language"
        )

    output_parts = []

    languages_used = []
    providers_used = []
    provider_types_used = []
    confidences = []

    for script, segment_text in segments:

        # ----------------------------------------------------
        # Latin / English
        # ----------------------------------------------------

        if script == "latin":

            output_parts.append(segment_text)

            if segment_text.strip():

                language_result = detect_text_information(
                    segment_text
                )

                if language_result["language"]:
                    languages_used.append(
                        language_result["language"]
                    )
                else:
                    languages_used.append(
                        "english"
                    )

            continue

        # ----------------------------------------------------
        # Indian script
        # ----------------------------------------------------

        language = SCRIPT_LANGUAGE.get(script)

        if language is None:
            output_parts.append(segment_text)
            continue

        provider = provider_selector.get_provider(
            language
        )

        if provider is None:
            raise ValueError(
                f"No transliteration provider available "
                f"for language: {language}"
            )

        result = provider.transliterate(
            segment_text,
            language,
        )

        output_parts.append(result.text)

        languages_used.append(language)

        if result.provider:
            providers_used.append(
                result.provider
            )

        if result.provider_type:
            provider_types_used.append(
                result.provider_type
            )

        if result.confidence is not None:
            confidences.append(
                result.confidence
            )

    # --------------------------------------------------------
    # Remove duplicates while preserving order
    # --------------------------------------------------------

    languages_used = list(
        dict.fromkeys(languages_used)
    )

    providers_used = list(
        dict.fromkeys(providers_used)
    )

    provider_types_used = list(
        dict.fromkeys(provider_types_used)
    )

    # --------------------------------------------------------
    # Build combined metadata
    # --------------------------------------------------------

    language = (
        languages_used[0]
        if len(languages_used) == 1
        else "mixed"
    )

    provider = (
        providers_used[0]
        if len(providers_used) == 1
        else "mixed"
    )

    provider_type = (
        provider_types_used[0]
        if len(provider_types_used) == 1
        else "mixed"
    )

    confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else None
    )

    return TransliterationResult(
        text="".join(output_parts),
        language=language,
        provider=provider,
        provider_type=provider_type,
        confidence=confidence,
        languages=languages_used,
    )


def transliterate_text(text, language=None):
    """
    Transliterate text while supporting:

    1. Explicit single-language input.
    2. Automatic single-language detection.
    3. Mixed Indian-language input when language is auto.

    Latin/English text is preserved.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "Input text is required"
        )

    # --------------------------------------------------------
    # NORMALIZE INPUT
    # --------------------------------------------------------

    text = normalize_text(text)

    # --------------------------------------------------------
    # NORMALIZE REQUESTED LANGUAGE
    # --------------------------------------------------------

    requested_language = (
        language.lower().strip()
        if isinstance(language, str)
        else None
    )

    if requested_language == "auto":
        requested_language = None

    # ========================================================
    # EXPLICIT LANGUAGE
    # ========================================================

    if requested_language is not None:

        detection_result = detect_text_information(
            text
        )

        detected_language = detection_result["language"]
        detected_script = detection_result["script"]

        if detected_language is not None:

            if requested_language != detected_language:

                raise ValueError(
                    f"Language mismatch: detected language is "
                    f"{detected_language}, but requested language is "
                    f"{requested_language}"
                )

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

        provider = provider_selector.get_provider(
            requested_language
        )

        if provider is None:
            raise ValueError(
                f"No transliteration provider available for language: "
                f"{requested_language}"
            )

        result = provider.transliterate(
            text,
            requested_language,
        )

        # ----------------------------------------------------
        # Ensure languages metadata is available
        # ----------------------------------------------------

        if result.languages is None:
            result.languages = [
                requested_language
            ]

        return result

    # ========================================================
    # AUTOMATIC / MIXED LANGUAGE
    # ========================================================

    segments = _split_mixed_text(text)

    # If there are multiple Indian scripts, or Indian script
    # combined with Latin text, process as mixed input.

    indian_scripts = {
        script
        for script, segment in segments
        if script != "latin"
        and segment.strip()
    }

    has_latin = any(
        script == "latin" and segment.strip()
        for script, segment in segments
    )

    if len(indian_scripts) > 1 or (
        len(indian_scripts) >= 1 and has_latin
    ):

        return _transliterate_mixed_text(
            text
        )

    # ========================================================
    # NORMAL SINGLE-LANGUAGE FLOW
    # ========================================================

    detection_result = detect_text_information(
        text
    )

    detected_language = detection_result["language"]
    detected_script = detection_result["script"]

    final_language = detected_language

    if final_language is None:
        final_language = SCRIPT_TO_LANGUAGE.get(
            detected_script
        )

    # --------------------------------------------------------
    # PURE LATIN TEXT
    # --------------------------------------------------------

    if final_language is None and detected_script == "latin":

        return TransliterationResult(
            text=text,
            language="english",
            provider="passthrough",
            provider_type="passthrough",
            confidence=None,
            languages=["english"],
        )

    if final_language is None:
        raise ValueError(
            "Could not detect the input language"
        )

    provider = provider_selector.get_provider(
        final_language
    )

    if provider is None:
        raise ValueError(
            f"No transliteration provider available for language: "
            f"{final_language}"
        )

    result = provider.transliterate(
        text,
        final_language,
    )

    # --------------------------------------------------------
    # Ensure languages metadata is available
    # --------------------------------------------------------

    if result.languages is None:
        result.languages = [
            final_language
        ]

    return result