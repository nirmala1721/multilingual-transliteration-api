import os
import sqlite3
import uuid
from datetime import datetime, timezone

from flask import current_app


class DocumentStorageService:
    """
    Handles storing uploaded document files and their
    transliteration metadata.

    Development storage:
    - Actual files -> storage/documents/
    - Metadata/results -> SQLite database
    """

    def __init__(self):
        self.storage_directory = os.path.abspath(
            os.path.join(
                current_app.root_path,
                "storage",
                "documents",
            )
        )

        self.database_path = os.path.join(
            current_app.root_path,
            "storage",
            "documents.db",
        )

        os.makedirs(
            self.storage_directory,
            exist_ok=True,
        )

        self._create_table()

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def _get_connection(self):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    # ========================================================
    # FILE PATH SECURITY
    # ========================================================

    def _get_safe_file_path(self, filename):
        """
        Return a file path guaranteed to remain inside the
        configured document storage directory.

        Prevents path traversal attacks and protects against
        manipulated filenames or database values.
        """

        storage_directory = os.path.abspath(
            self.storage_directory
        )

        file_path = os.path.abspath(
            os.path.join(
                storage_directory,
                filename,
            )
        )

        try:
            common_path = os.path.commonpath(
                [
                    storage_directory,
                    file_path,
                ]
            )

        except ValueError as error:
            raise ValueError(
                "Invalid document storage path"
            ) from error

        if common_path != storage_directory:
            raise ValueError(
                "Invalid document storage path"
            )

        return file_path

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    def _create_table(self):
        connection = self._get_connection()

        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    language TEXT,
                    status TEXT NOT NULL,
                    original_text TEXT,
                    transliterated_text TEXT,
                    provider TEXT,
                    provider_type TEXT,
                    confidence REAL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

        finally:
            connection.close()

    # ========================================================
    # SAVE DOCUMENT
    # ========================================================

    def save_document(
        self,
        file,
        file_type,
        language,
        original_text,
        transliterated_text,
        provider=None,
        provider_type=None,
        confidence=None,
    ):
        """
        Save the uploaded file and its metadata.

        A UUID-based filename is generated for physical
        storage so the original filename is never used
        as the actual storage filename.
        """

        if file is None:
            raise ValueError(
                "File is required"
            )

        if not file.filename:
            raise ValueError(
                "File name is required"
            )

        document_id = str(
            uuid.uuid4()
        )

        original_filename = os.path.basename(
            file.filename
        )

        extension = os.path.splitext(
            original_filename
        )[1].lower()

        stored_filename = (
            f"{document_id}{extension}"
        )

        file_path = self._get_safe_file_path(
            stored_filename
        )

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        # ----------------------------------------------------
        # SAVE PHYSICAL FILE
        # ----------------------------------------------------

        try:
            file.save(file_path)

        except Exception as error:
            # Do not leave a partially-created file behind.

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            raise RuntimeError(
                f"Unable to save document file: {str(error)}"
            ) from error

        # ----------------------------------------------------
        # SAVE DATABASE METADATA
        # ----------------------------------------------------

        connection = self._get_connection()

        try:
            connection.execute(
                """
                INSERT INTO documents (
                    id,
                    filename,
                    stored_filename,
                    file_type,
                    file_path,
                    language,
                    status,
                    original_text,
                    transliterated_text,
                    provider,
                    provider_type,
                    confidence,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    original_filename,
                    stored_filename,
                    file_type,
                    file_path,
                    language,
                    "Completed",
                    original_text,
                    transliterated_text,
                    provider,
                    provider_type,
                    confidence,
                    created_at,
                ),
            )

            connection.commit()

        except Exception:
            connection.rollback()

            # Database insertion failed after the physical
            # file was created. Remove the orphaned file.

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            raise

        finally:
            connection.close()

        document = self.get_document(
            document_id
        )

        if document is None:
            raise RuntimeError(
                "Document was saved but could not be retrieved"
            )

        return document

    # ========================================================
    # GET SINGLE DOCUMENT
    # ========================================================

    def get_document(self, document_id):
        if not document_id:
            return None

        connection = self._get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    id,
                    filename,
                    stored_filename,
                    file_type,
                    file_path,
                    language,
                    status,
                    original_text,
                    transliterated_text,
                    provider,
                    provider_type,
                    confidence,
                    created_at
                FROM documents
                WHERE id = ?
                """,
                (document_id,),
            ).fetchone()

            if row is None:
                return None

            return dict(row)

        finally:
            connection.close()

    # ========================================================
    # GET ALL DOCUMENTS
    # ========================================================

    def get_all_documents(self):
        connection = self._get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    filename,
                    file_type,
                    language,
                    status,
                    original_text,
                    transliterated_text,
                    provider,
                    provider_type,
                    confidence,
                    created_at
                FROM documents
                ORDER BY created_at DESC
                """
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

        finally:
            connection.close()

    # ========================================================
    # DELETE DOCUMENT
    # ========================================================

    def delete_document(self, document_id):
        if not document_id:
            return False

        document = self.get_document(
            document_id
        )

        if document is None:
            return False

        stored_filename = document[
            "stored_filename"
        ]

        # ----------------------------------------------------
        # REBUILD SAFE FILE PATH
        # ----------------------------------------------------

        file_path = self._get_safe_file_path(
            stored_filename
        )

        # ----------------------------------------------------
        # DELETE PHYSICAL FILE
        # ----------------------------------------------------

        if os.path.exists(file_path):
            try:
                os.remove(file_path)

            except OSError as error:
                raise RuntimeError(
                    f"Unable to delete document file: {str(error)}"
                ) from error

        # ----------------------------------------------------
        # DELETE DATABASE RECORD
        # ----------------------------------------------------

        connection = self._get_connection()

        try:
            cursor = connection.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (document_id,),
            )

            connection.commit()

            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()