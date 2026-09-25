from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage

from app.extensions import limiter
from app.api.response import error_response, success_response
from app.config import (
    MAX_FILE_SIZE,
    MAX_TEXT_LENGTH,
)
from app.services.document_storage_service import (
    DocumentStorageService,
)
from app.services.file_processing_service import (
    extract_text_from_file,
)
from app.services.transliteration_service import (
    transliterate_text,
)


transliteration_ns = Namespace(
    "transliteration",
    description="Text transliteration operations",
)


# ============================================================
# TEXT API MODEL
# ============================================================

text_model = transliteration_ns.model(
    "TextTransliterationRequest",
    {
        "text": fields.String(
            required=True,
            description=(
                "Text to transliterate. "
                "Maximum 100,000 characters."
            ),
            example="తిన్నావా?",
        ),
        "language": fields.String(
            required=False,
            description=(
                "Optional language of the input text. "
                "If omitted, the API detects the language automatically."
            ),
            example="telugu",
        ),
    },
)


# ============================================================
# TEXT ENDPOINT
# ============================================================

@transliteration_ns.route("/text")
class TextTransliteration(Resource):

    @limiter.limit("60 per minute")
    @transliteration_ns.doc(
        description=(
            "Transliterates Indian-language text into Latin/English "
            "characters while preserving pronunciation."
        )
    )
    @transliteration_ns.expect(text_model)
    @transliteration_ns.response(
        200,
        "Transliteration successful",
    )
    @transliteration_ns.response(
        400,
        "Invalid request",
    )
    def post(self):
        """
        Transliterate text supplied in the request body.
        """

        # ========================================================
        # REQUEST VALIDATION
        # ========================================================

        data = request.get_json(silent=True)

        if not data:
            return error_response(
                "Request body is required",
                400,
            )

        text = data.get("text")
        language = data.get("language")

        if text is None:
            return error_response(
                "Text is required",
                400,
            )

        if not isinstance(text, str):
            return error_response(
                "Text must be a string",
                400,
            )

        text = text.strip()

        if not text:
            return error_response(
                "Text cannot be empty",
                400,
            )

        if len(text) > MAX_TEXT_LENGTH:
            return error_response(
                "Text exceeds the maximum allowed length of "
                f"{MAX_TEXT_LENGTH:,} characters",
                400,
            )

        # ========================================================
        # LANGUAGE VALIDATION
        # ========================================================

        if language is not None:

            if not isinstance(language, str):
                return error_response(
                    "Language must be a string",
                    400,
                )

            language = language.strip().lower()

            if not language:
                language = None

        # ========================================================
        # TRANSLITERATION
        # ========================================================

        try:

            result = transliterate_text(
                text,
                language,
            )

        except ValueError as error:

            return error_response(
                str(error),
                400,
            )

        except Exception as error:

            return error_response(
                f"Transliteration failed: {str(error)}",
                500,
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        return success_response(
            data={
                "original_text": text,
                "language": result.language,
                "transliterated_text": result.text,
                "provider": result.provider,
                "provider_type": result.provider_type,
                "confidence": result.confidence,
            },
            status_code=200,
        )


# ============================================================
# FILE API MODEL
# ============================================================

file_model = transliteration_ns.parser()

file_model.add_argument(
    "file",
    type=FileStorage,
    location="files",
    required=True,
    help=(
        "File to transliterate. "
        "Supported: .txt, .pdf, .docx, .png, .jpg, .jpeg"
    ),
)


# ============================================================
# FILE ENDPOINT
# ============================================================

@transliteration_ns.route("/file")
class FileTransliteration(Resource):

    @limiter.limit("10 per minute")
    @transliteration_ns.expect(file_model)
    @transliteration_ns.response(
        200,
        "File processed and transliterated successfully",
    )
    @transliteration_ns.response(
        400,
        "Invalid file or unsupported file type",
    )
    @transliteration_ns.response(
        413,
        "File size exceeds 10 MB",
    )
    def post(self):
        """
        Extract text from an uploaded file and transliterate it.
        """

        # ========================================================
        # FILE VALIDATION
        # ========================================================

        if "file" not in request.files:

            return error_response(
                "File is required",
                400,
            )

        file = request.files["file"]

        if not file.filename:

            return error_response(
                "File name is required",
                400,
            )

        # ========================================================
        # FILE SIZE VALIDATION
        # ========================================================

        try:

            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)

        except Exception as error:

            return error_response(
                f"Unable to determine file size: {str(error)}",
                400,
            )

        if file_size > MAX_FILE_SIZE:

            return error_response(
                "File size exceeds the maximum allowed "
                "limit of 10 MB",
                413,
            )

        if file_size == 0:

            return error_response(
                "File cannot be empty",
                400,
            )

        # ========================================================
        # TEXT EXTRACTION
        # ========================================================

        try:

            text = extract_text_from_file(file)

        except ValueError as error:

            error_message = str(error)

            if (
                "maximum allowed is" in error_message
                and "pages" in error_message
            ):
                return error_response(
                    error_message,
                    413,
                )

            return error_response(
                error_message,
                400,
            )

        except Exception as error:

            return error_response(
                f"File processing failed: {str(error)}",
                500,
            )

        # ========================================================
        # EXTRACTED TEXT VALIDATION
        # ========================================================

        if text is None:

            return error_response(
                "No text could be extracted from the file.",
                400,
            )

        if not isinstance(text, str):

            return error_response(
                "Extracted file content must be text.",
                400,
            )

        text = text.strip()

        if not text:

            return error_response(
                "No text could be extracted from the file.",
                400,
            )

        if len(text) > MAX_TEXT_LENGTH:

            return error_response(
                "Extracted text exceeds the maximum allowed "
                f"length of {MAX_TEXT_LENGTH:,} characters",
                400,
            )

        # ========================================================
        # TRANSLITERATION
        # ========================================================

        try:

            result = transliterate_text(text)

        except ValueError as error:

            return error_response(
                str(error),
                400,
            )

        except Exception as error:

            return error_response(
                f"Transliteration failed: {str(error)}",
                500,
            )

        # ========================================================
        # STORE ORIGINAL FILE
        # ========================================================

        try:

            # Text extraction may have consumed the
            # uploaded file stream. Reset it before saving.
            file.seek(0)

            file_type = (
                file.filename
                .rsplit(".", 1)[-1]
                .lower()
                if "." in file.filename
                else "unknown"
            )

            storage_service = DocumentStorageService()

            document = storage_service.save_document(
                file=file,
                file_type=file_type,
                language=result.language,
                original_text=text,
                transliterated_text=result.text,
                provider=result.provider,
                provider_type=result.provider_type,
                confidence=result.confidence,
            )

        except Exception as error:

            return error_response(
                f"Document storage failed: {str(error)}",
                500,
            )

        # ========================================================
        # RESPONSE
        # ========================================================

        return success_response(
            data={
                "document_id": document["id"],
                "filename": document["filename"],
                "original_text": text,
                "language": result.language,
                "transliterated_text": result.text,
                "provider": result.provider,
                "provider_type": result.provider_type,
                "confidence": result.confidence,
                "status": document["status"],
                "created_at": document["created_at"],
            },
            status_code=200,
        )