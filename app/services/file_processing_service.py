import zipfile

import pymupdf
from PIL import Image
from werkzeug.utils import secure_filename

from app.config import (
    ALLOWED_EXTENSIONS,
    MAX_PDF_PAGES,
    MAX_TEXT_LENGTH,
)
from app.services.docx_extraction_service import (
    extract_text_from_docx,
)
from app.services.file_extraction_service import (
    extract_text_from_pdf,
)
from app.services.ocr_service import (
    extract_text_from_image,
)
from app.services.scanned_pdf_service import (
    extract_text_from_scanned_pdf,
)


# ============================================================
# FILE HELPERS
# ============================================================

def get_file_extension(filename):
    """
    Return the lowercase file extension.

    Examples:
        "document.PDF" -> ".pdf"
        "image.PNG"    -> ".png"
    """

    if not filename or "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[1].lower()


def get_allowed_extensions_message():
    """
    Build the supported file type message from configuration.
    """

    allowed_types = ", ".join(
        sorted(ALLOWED_EXTENSIONS)
    )

    return (
        "Unsupported file type. "
        f"Allowed types: {allowed_types}"
    )


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_image_content(file):
    """
    Validate that the uploaded file is a real image.
    """

    file.seek(0)

    try:
        with Image.open(file) as image:
            image.verify()

    except Exception as error:
        raise ValueError(
            "Invalid image file content"
        ) from error

    finally:
        file.seek(0)


# ============================================================
# PDF VALIDATION
# ============================================================

def validate_pdf_content(file):
    """
    Validate that the uploaded file has a valid PDF signature.
    """

    file.seek(0)

    try:
        header = file.read(5)

    finally:
        file.seek(0)

    if header != b"%PDF-":
        raise ValueError(
            "Invalid PDF file content"
        )


def validate_pdf_page_count(file):
    """
    Validate the number of pages in a PDF before extraction
    or OCR processing begins.

    This prevents very large PDFs from entering the
    expensive extraction/OCR pipeline.
    """

    file.seek(0)

    try:
        pdf_document = pymupdf.open(
            stream=file.read(),
            filetype="pdf",
        )

        try:
            page_count = pdf_document.page_count

        finally:
            pdf_document.close()

    except Exception as error:
        raise ValueError(
            "Invalid or corrupted PDF file"
        ) from error

    finally:
        file.seek(0)

    if page_count > MAX_PDF_PAGES:
        raise ValueError(
            f"PDF contains {page_count} pages. "
            f"The maximum allowed is "
            f"{MAX_PDF_PAGES} pages."
        )

    return page_count


# ============================================================
# DOCX VALIDATION
# ============================================================

def validate_docx_content(file):
    """
    Validate that the uploaded file is a valid DOCX package.
    """

    file.seek(0)

    try:
        with zipfile.ZipFile(file) as document:

            if document.testzip() is not None:
                raise ValueError(
                    "Invalid DOCX file content"
                )

            if "word/document.xml" not in document.namelist():
                raise ValueError(
                    "Invalid DOCX file content"
                )

    except zipfile.BadZipFile as error:
        raise ValueError(
            "Invalid DOCX file content"
        ) from error

    finally:
        file.seek(0)


# ============================================================
# TXT EXTRACTION
# ============================================================

def extract_text_from_txt(file):
    """
    Extract UTF-8 text from a TXT file.
    """

    file.seek(0)

    content = file.read()

    try:
        text = content.decode("utf-8")

    except UnicodeDecodeError as error:
        raise ValueError(
            "TXT file must be UTF-8 encoded"
        ) from error

    finally:
        file.seek(0)

    return text.strip()


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_text_from_pdf_file(file):
    """
    Extract text from a PDF.

    Flow:

        PDF validation
            ↓
        Page count validation
            ↓
        Normal PDF text extraction
            ↓
        Scanned PDF OCR fallback
    """

    # -------------------------
    # PDF VALIDATION
    # -------------------------

    validate_pdf_content(file)

    # -------------------------
    # PAGE COUNT VALIDATION
    # -------------------------

    validate_pdf_page_count(file)

    # -------------------------
    # NORMAL TEXT EXTRACTION
    # -------------------------

    file.seek(0)

    extraction_result = extract_text_from_pdf(file)

    if extraction_result["has_text"]:
        file.seek(0)
        return extraction_result["text"]

    # -------------------------
    # SCANNED PDF OCR
    # -------------------------

    file.seek(0)

    ocr_result = extract_text_from_scanned_pdf(file)

    if not ocr_result["has_text"]:
        raise ValueError(
            "Could not extract text from PDF"
        )

    file.seek(0)

    return ocr_result["text"]


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_text_from_docx_file(file):
    """
    Extract text from a DOCX file.
    """

    validate_docx_content(file)

    file.seek(0)

    extraction_result = extract_text_from_docx(file)

    if not extraction_result["has_text"]:
        raise ValueError(
            "Could not extract text from DOCX"
        )

    file.seek(0)

    return extraction_result["text"]


# ============================================================
# IMAGE EXTRACTION
# ============================================================

def extract_text_from_image_file(file):
    """
    Validate an image and extract its text using OCR.
    """

    validate_image_content(file)

    file.seek(0)

    ocr_result = extract_text_from_image(file)

    if not ocr_result["has_text"]:
        raise ValueError(
            "Could not extract text from image"
        )

    file.seek(0)

    return ocr_result["text"]


# ============================================================
# EXTRACTED TEXT VALIDATION
# ============================================================

def validate_extracted_text(text):
    """
    Apply common validation to extracted text.
    """

    if text is None:
        raise ValueError(
            "File cannot be empty"
        )

    if not isinstance(text, str):
        raise ValueError(
            "Extracted file content must be text"
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "File cannot be empty"
        )

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            "Extracted text exceeds the maximum allowed "
            f"length of {MAX_TEXT_LENGTH:,} characters"
        )

    return text


# ============================================================
# MAIN FILE PROCESSING ENTRY POINT
# ============================================================

def extract_text_from_file(file):
    """
    Main file-processing entry point.

    Flow:

        filename validation
            ↓
        extension validation
            ↓
        file-specific validation
            ↓
        PDF page-count validation
            ↓
        file-specific extraction
            ↓
        common text validation
            ↓
        extracted text
    """

    # ========================================================
    # FILE VALIDATION
    # ========================================================

    if file is None:
        raise ValueError(
            "File is required"
        )

    if not file.filename:
        raise ValueError(
            "File name is required"
        )

    filename = secure_filename(file.filename)

    if not filename:
        raise ValueError(
            "Invalid file name"
        )

    # ========================================================
    # EXTENSION VALIDATION
    # ========================================================

    extension = get_file_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            get_allowed_extensions_message()
        )

    # ========================================================
    # FILE EXTRACTION
    # ========================================================

    if extension == ".txt":

        text = extract_text_from_txt(file)

    elif extension == ".pdf":

        text = extract_text_from_pdf_file(file)

    elif extension == ".docx":

        text = extract_text_from_docx_file(file)

    elif extension in {
        ".png",
        ".jpg",
        ".jpeg",
    }:

        text = extract_text_from_image_file(file)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    # ========================================================
    # COMMON VALIDATION
    # ========================================================

    return validate_extracted_text(text)