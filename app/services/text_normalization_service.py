import re


MULTIPLE_SPACES_PATTERN = r"[ \t]+"
MULTIPLE_BLANK_LINES_PATTERN = r"\n{3,}"


def normalize_text(text):
    """
    Normalize extracted or user-provided text before
    language detection and transliteration.

    Normalization:
    - Handles None safely.
    - Ensures the input is a string.
    - Removes leading and trailing whitespace.
    - Converts multiple spaces/tabs into one space.
    - Reduces 3 or more consecutive blank lines to 2.

    Args:
        text: Input text to normalize.

    Returns:
        Normalized text as a string.
    """

    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    if not text:
        return ""

    text = re.sub(
        MULTIPLE_SPACES_PATTERN,
        " ",
        text,
    )

    text = re.sub(
        MULTIPLE_BLANK_LINES_PATTERN,
        "\n\n",
        text,
    )

    return text