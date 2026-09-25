import easyocr


OCR_LANGUAGES = ["te", "en"]
OCR_USE_GPU = False

_reader = None


def get_reader():
    """
    Initialize the EasyOCR reader only when OCR is actually needed.
    The initialized reader is then reused for subsequent requests.
    """

    global _reader

    if _reader is None:
        _reader = easyocr.Reader(
            OCR_LANGUAGES,
            gpu=OCR_USE_GPU
        )

    return _reader


def extract_text_from_image(file):
    """
    Extract text from an image using EasyOCR.

    The OCR reader is initialized lazily on the first OCR request
    and reused for subsequent requests.
    """

    reader = get_reader()

    image_bytes = file.read()

    results = reader.readtext(
        image_bytes
    )

    extracted_text = []

    for result in results:

        text = result[1]

        if text.strip():
            extracted_text.append(
                text
            )

    final_text = "\n".join(
        extracted_text
    )

    return {
        "text": final_text,
        "has_text": bool(
            final_text.strip()
        )
    }