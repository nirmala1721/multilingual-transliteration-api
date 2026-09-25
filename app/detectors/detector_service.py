from app.detectors.language_detector import detect_language
from app.detectors.script_detector import detect_script


SCRIPT_TO_LANGUAGE = {
    "telugu": "telugu",
    "kannada": "kannada",
    "tamil": "tamil",
    "bengali": "bengali",
    "gujarati": "gujarati",
    "gurmukhi": "punjabi",
    "oriya": "odia",
    "malayalam": "malayalam",
    "devanagari": "hindi",
}


def detect_text_information(text):
    """
    Detect both script and language from the input text.

    Language detection is attempted first using the
    language detector. If language detection fails,
    the detected script is used as a fallback.

    Args:
        text: Input text to analyze.

    Returns:
        A dictionary containing:
            script: Detected script name or None.
            language: Detected language name or None.
    """

    script = detect_script(text)
    language = detect_language(text)

    if language is None:
        language = SCRIPT_TO_LANGUAGE.get(script)

    return {
        "script": script,
        "language": language,
    }