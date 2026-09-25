import easyocr


OCR_LANGUAGES = ["te", "en"]
OCR_USE_GPU = False


reader = easyocr.Reader(
    OCR_LANGUAGES,
    gpu=OCR_USE_GPU
)


def extract_text_from_image(file):
    """
    Extract text from an image using EasyOCR.

    The OCR reader is initialized once when this module
    is loaded and reused for subsequent requests.
    """

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