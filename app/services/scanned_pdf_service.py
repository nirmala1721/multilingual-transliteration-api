import cv2
import numpy as np
import pymupdf

from app.config import (
    MAX_PDF_PAGES,
    MAX_TEXT_LENGTH,
)
from app.services.ocr_service import get_reader


PDF_RENDER_SCALE = 3
CROP_THRESHOLD = 245
CROP_MARGIN = 20


def crop_text_area(image):
    """
    Detect the area containing visible content and crop the image
    with a small margin around the detected content.

    If no content area is detected, the original image is returned.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    _, threshold = cv2.threshold(
        gray,
        CROP_THRESHOLD,
        255,
        cv2.THRESH_BINARY_INV
    )

    coordinates = cv2.findNonZero(
        threshold
    )

    if coordinates is None:
        return image

    x, y, width, height = cv2.boundingRect(
        coordinates
    )

    x = max(
        0,
        x - CROP_MARGIN
    )

    y = max(
        0,
        y - CROP_MARGIN
    )

    width = min(
        image.shape[1] - x,
        width + (2 * CROP_MARGIN)
    )

    height = min(
        image.shape[0] - y,
        height + (2 * CROP_MARGIN)
    )

    return image[
        y:y + height,
        x:x + width
    ]


def render_pdf_page(page):
    """
    Render a PDF page into an OpenCV image.
    """

    matrix = pymupdf.Matrix(
        PDF_RENDER_SCALE,
        PDF_RENDER_SCALE
    )

    pixmap = page.get_pixmap(
        matrix=matrix
    )

    image_bytes = pixmap.tobytes(
        "png"
    )

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "Could not render PDF page as image"
        )

    return image


def perform_ocr(image):
    """
    Run EasyOCR on the supplied image and return
    the extracted text.

    The EasyOCR reader is initialized lazily and
    reused for subsequent OCR requests.
    """

    reader = get_reader()

    results = reader.readtext(
        image,
        detail=1,
        paragraph=False
    )

    page_text = []

    for result in results:

        text = result[1]

        if text.strip():

            page_text.append(
                text
            )

    return "\n".join(
        page_text
    )


def extract_text_from_scanned_pdf(file):
    """
    Extract text from a scanned PDF using OCR.

    The PDF page count is checked before OCR starts.

    OCR processing also stops when the configured
    maximum extracted text length is reached.
    """

    pdf_document = pymupdf.open(
        stream=file.read(),
        filetype="pdf"
    )

    extracted_pages = []
    total_text_length = 0

    try:

        # -------------------------
        # PDF PAGE LIMIT
        # -------------------------

        page_count = pdf_document.page_count

        if page_count > MAX_PDF_PAGES:

            raise ValueError(
                f"PDF contains {page_count} pages. "
                f"The maximum allowed is "
                f"{MAX_PDF_PAGES} pages."
            )

        # -------------------------
        # PROCESS EACH PAGE
        # -------------------------

        for page_number, page in enumerate(
            pdf_document,
            start=1
        ):

            # -------------------------
            # 1. RENDER PDF PAGE
            # -------------------------

            image = render_pdf_page(
                page
            )

            # -------------------------
            # 2. CROP CONTENT AREA
            # -------------------------

            cropped_image = crop_text_area(
                image
            )

            # -------------------------
            # 3. OCR
            # -------------------------

            extracted_text = perform_ocr(
                cropped_image
            )

            if not extracted_text.strip():

                continue

            # -------------------------
            # 4. TEXT SIZE PROTECTION
            # -------------------------

            remaining_length = (
                MAX_TEXT_LENGTH
                - total_text_length
            )

            if remaining_length <= 0:

                raise ValueError(
                    "Extracted text exceeds the maximum "
                    "allowed length of 100,000 characters"
                )

            if len(extracted_text) > remaining_length:

                raise ValueError(
                    "Extracted text exceeds the maximum "
                    "allowed length of 100,000 characters"
                )

            # -------------------------
            # 5. STORE PAGE RESULT
            # -------------------------

            extracted_pages.append(
                {
                    "page": page_number,
                    "text": extracted_text,
                }
            )

            total_text_length += len(
                extracted_text
            )

    finally:

        pdf_document.close()

    # -------------------------
    # COMBINE PAGE TEXT
    # -------------------------

    final_text = "\n\n".join(
        page["text"]
        for page in extracted_pages
    )

    return {
        "text": final_text,
        "has_text": bool(
            final_text.strip()
        ),
        "pages": extracted_pages,
    }