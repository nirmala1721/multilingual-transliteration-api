import pymupdf


BAD_CHARACTERS = {
    "\ufffd",  # replacement character �
    "\u00b7",  # middle dot ·
}


SUPPORTED_SCRIPT_RANGES = [
    (0x0900, 0x097F),  # Devanagari
    (0x0980, 0x09FF),  # Bengali
    (0x0A00, 0x0A7F),  # Gurmukhi
    (0x0A80, 0x0AFF),  # Gujarati
    (0x0B00, 0x0B7F),  # Odia
    (0x0B80, 0x0BFF),  # Tamil
    (0x0C00, 0x0C7F),  # Telugu
    (0x0C80, 0x0CFF),  # Kannada
    (0x0D00, 0x0D7F),  # Malayalam
]


MINIMUM_MEANINGFUL_RATIO = 0.30
MAX_BAD_CHARACTER_RATIO = 0.50


def is_usable_text(text):
    """
    Determine whether extracted PDF text is usable.

    Text is considered unusable when:
    - It is empty.
    - More than 50% consists of known bad characters.
    - It contains no meaningful supported characters.
    - Less than 30% of the content is meaningful supported text.
    """

    if not text:
        return False

    text = text.strip()

    if not text:
        return False

    bad_count = sum(
        1
        for character in text
        if character in BAD_CHARACTERS
    )

    if (
        bad_count / len(text)
        > MAX_BAD_CHARACTER_RATIO
    ):
        return False

    meaningful_characters = 0

    for character in text:

        if not character.isalnum():
            continue

        code_point = ord(character)

        # Latin letters and digits
        if character.isascii():

            meaningful_characters += 1

            continue

        # Supported Indian scripts
        for start, end in SUPPORTED_SCRIPT_RANGES:

            if start <= code_point <= end:

                meaningful_characters += 1

                break

    if meaningful_characters == 0:
        return False

    meaningful_ratio = (
        meaningful_characters / len(text)
    )

    return (
        meaningful_ratio
        >= MINIMUM_MEANINGFUL_RATIO
    )


def extract_text_from_pdf(file):
    """
    Extract text from all pages of a PDF.

    The returned `has_text` value indicates whether the
    extracted text appears usable. If it is False, the
    caller can fall back to scanned-PDF OCR.
    """

    pdf_document = pymupdf.open(
        stream=file.read(),
        filetype="pdf"
    )

    extracted_text = []

    try:

        for page in pdf_document:

            text = page.get_text().strip()

            if text:

                extracted_text.append(
                    text
                )

    finally:

        pdf_document.close()

    final_text = "\n".join(
        extracted_text
    )

    return {
        "text": final_text,
        "has_text": is_usable_text(
            final_text
        )
    }