# ============================================================
# FILE SIZE LIMIT
# ============================================================

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# TEXT LIMIT
# ============================================================

MAX_TEXT_LENGTH = 100_000


# ============================================================
# PDF LIMIT
# ============================================================

# Maximum number of pages allowed in a PDF.
#
# This protects the API from very large scanned PDFs because
# scanned PDF pages require OCR processing, which can be slow.
MAX_PDF_PAGES = 10


# ============================================================
# ALLOWED FILE EXTENSIONS
# ============================================================

ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
}