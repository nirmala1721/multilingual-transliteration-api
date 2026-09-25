from flask_restx import Api
from werkzeug.exceptions import RequestEntityTooLarge

from app.api.health import health_ns
from app.api.transliteration import transliteration_ns
from app.api.documents import documents_ns


api = Api(
    title="Universal Multilingual Transliteration API",
    version="1.0",
    description="API for multilingual text transliteration.",
)


@api.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    """
    Handle requests that exceed the configured upload limit.
    """

    return {
        "success": False,
        "message": "File size must not exceed 10 MB",
    }, 413


api.add_namespace(
    health_ns,
    path="/api/v1/health",
)

api.add_namespace(
    transliteration_ns,
    path="/api/v1/transliterate",
)

api.add_namespace(
    documents_ns,
    path="/api/v1/documents",
)