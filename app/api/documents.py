import os

from flask import send_file
from flask_restx import Namespace, Resource

from app.api.response import error_response, success_response
from app.services.document_storage_service import (
    DocumentStorageService,
)


documents_ns = Namespace(
    "documents",
    description="Document management operations",
)


# ============================================================
# DOCUMENT LIST
# ============================================================

@documents_ns.route("")
class DocumentList(Resource):

    @documents_ns.response(
        200,
        "Documents retrieved successfully",
    )
    def get(self):
        """
        Return all stored documents.
        """

        try:

            storage_service = DocumentStorageService()

            documents = (
                storage_service.get_all_documents()
            )

            return success_response(
                data={
                    "documents": documents,
                    "count": len(documents),
                },
                status_code=200,
            )

        except Exception as error:

            return error_response(
                f"Failed to retrieve documents: {str(error)}",
                500,
            )


# ============================================================
# SINGLE DOCUMENT
# ============================================================

@documents_ns.route("/<string:document_id>")
class DocumentDetails(Resource):

    @documents_ns.response(
        200,
        "Document retrieved successfully",
    )
    @documents_ns.response(
        404,
        "Document not found",
    )
    def get(self, document_id):
        """
        Return one stored document.
        """

        try:

            storage_service = DocumentStorageService()

            document = (
                storage_service.get_document(
                    document_id
                )
            )

            if document is None:

                return error_response(
                    "Document not found",
                    404,
                )

            return success_response(
                data=document,
                status_code=200,
            )

        except Exception as error:

            return error_response(
                f"Failed to retrieve document: {str(error)}",
                500,
            )

    # ========================================================
    # DELETE DOCUMENT
    # ========================================================

    @documents_ns.response(
        200,
        "Document deleted successfully",
    )
    @documents_ns.response(
        404,
        "Document not found",
    )
    def delete(self, document_id):
        """
        Delete a stored document and its metadata.
        """

        try:

            storage_service = DocumentStorageService()

            deleted = (
                storage_service.delete_document(
                    document_id
                )
            )

            if not deleted:

                return error_response(
                    "Document not found",
                    404,
                )

            return success_response(
                data={
                    "document_id": document_id,
                    "message": (
                        "Document deleted successfully"
                    ),
                },
                status_code=200,
            )

        except Exception as error:

            return error_response(
                f"Failed to delete document: {str(error)}",
                500,
            )


# ============================================================
# DOCUMENT FILE
# ============================================================

@documents_ns.route(
    "/<string:document_id>/file"
)
class DocumentFile(Resource):

    @documents_ns.response(
        200,
        "Document file retrieved successfully",
    )
    @documents_ns.response(
        404,
        "Document not found",
    )
    def get(self, document_id):
        """
        Return the actual stored document file.

        This endpoint is used by the frontend for
        displaying stored PDF and image files.
        """

        try:

            storage_service = DocumentStorageService()

            document = (
                storage_service.get_document(
                    document_id
                )
            )

            if document is None:

                return error_response(
                    "Document not found",
                    404,
                )

            file_path = document.get(
                "file_path"
            )

            if not file_path:

                return error_response(
                    "Stored document file path not found",
                    404,
                )

            if not os.path.isfile(file_path):

                return error_response(
                    "Stored document file not found",
                    404,
                )

            return send_file(
                file_path,
                as_attachment=False,
                download_name=document["filename"],
            )

        except Exception as error:

            return error_response(
                f"Failed to retrieve document file: {str(error)}",
                500,
            )