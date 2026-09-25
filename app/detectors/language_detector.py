from lingua import Language, LanguageDetectorBuilder


LINGUA_LANGUAGES = [
    Language.TELUGU,
    Language.HINDI,
    Language.TAMIL,
    Language.BENGALI,
    Language.GUJARATI,
    Language.PUNJABI,
    Language.ENGLISH,
    Language.MARATHI,
]


ASSAMESE_CHARACTERS = {
    "ৰ",
    "ৱ",
}


ASSAMESE_WORDS = {
    "মই",
    "আপুনি",
    "কেনে",
    "অসমীয়া",
    "আছোঁ",
    "আছে",
    "শিকি",
}


detector = LanguageDetectorBuilder.from_languages(
    *LINGUA_LANGUAGES
).build()


def detect_assamese(text):
    """
    Detect Assamese using Assamese-specific characters
    and common Assamese words.

    Assamese is handled separately because the current
    Lingua configuration does not include Assamese.
    """

    if not isinstance(text, str) or not text.strip():
        return False

    for character in text:
        if character in ASSAMESE_CHARACTERS:
            return True

    words = set(text.split())

    matches = ASSAMESE_WORDS.intersection(words)

    return len(matches) >= 2


def detect_language(text):
    """
    Detect the language of the supplied text.

    Assamese is checked first using the custom heuristic.
    Other configured languages are detected using Lingua.

    Args:
        text: Input text to analyze.

    Returns:
        Language name in lowercase, or None if detection fails.
    """

    if not isinstance(text, str) or not text.strip():
        return None

    if detect_assamese(text):
        return "assamese"

    language = detector.detect_language_of(text)

    if language is None:
        return None

    return language.name.lower()