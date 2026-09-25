SCRIPT_RANGES = {
    # Indian scripts
    "telugu": (0x0C00, 0x0C7F),
    "kannada": (0x0C80, 0x0CFF),
    "malayalam": (0x0D00, 0x0D7F),
    "tamil": (0x0B80, 0x0BFF),
    "bengali": (0x0980, 0x09FF),
    "oriya": (0x0B00, 0x0B7F),
    "gujarati": (0x0A80, 0x0AFF),
    "gurmukhi": (0x0A00, 0x0A7F),
    "devanagari": (0x0900, 0x097F),

    # Other scripts
    # Kept for identifying unsupported input.
    "arabic": (0x0600, 0x06FF),
    "cyrillic": (0x0400, 0x04FF),
    "greek": (0x0370, 0x03FF),
    "hiragana": (0x3040, 0x309F),
    "katakana": (0x30A0, 0x30FF),
    "han": (0x4E00, 0x9FFF),
}


def detect_script(text: str) -> str:
    """
    Detect the dominant Unicode script in the input text.

    The script with the highest number of recognized
    characters is returned.

    If no known script is found, the input is treated
    as Latin text.
    """

    script_counts: dict[str, int] = {}

    for character in text:

        code_point = ord(character)

        for script, (start, end) in SCRIPT_RANGES.items():

            if start <= code_point <= end:

                script_counts[script] = (
                    script_counts.get(script, 0) + 1
                )

                break

    if not script_counts:
        return "latin"

    return max(
        script_counts,
        key=lambda script: script_counts[script],
    )