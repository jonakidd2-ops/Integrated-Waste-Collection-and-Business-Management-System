"""F-02: Document Management.

Handles uploading, searching and retrieving business documents.
The graphical interface will call these methods.
"""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

try:
    from .errors import ValidationError, NotFound, ServiceError
except ImportError:
    from errors import ValidationError, NotFound, ServiceError


class DocumentManager:
    def __init__(self, db, authorize):
        """Receive the database and the application's permission checker.

        authorize(user, "documents") must raise PermissionDenied when
        the user is not allowed to manage documents.
        """
        if not callable(authorize):
            raise TypeError("A permission-checking function is required.")

        self.db = db
        self.authorize = authorize

    def upload_document(
        self, user, file_path, title, doc_type, description=""
    ):
        """Validate and save a document. Return its unique document ID."""
        self.authorize(user, "documents")

        title = (title or "").strip()
        doc_type = (doc_type or "").strip()
        description = (description or "").strip()

        if not file_path:
            raise ValidationError("Please select a document.")

        if not title:
            raise ValidationError("Please enter a document title.")

        if not doc_type:
            raise ValidationError("Please enter a document type.")

        path = Path(file_path)

        try:
            if not path.is_file():
                raise ValidationError(
                    "The selected file does not exist or is not a file."
                )

            content = path.read_bytes()
        except OSError as exc:
            raise ServiceError(
                "The selected document could not be read."
            ) from exc

        details = {
            "title": title,
            "doc_type": doc_type,
            "description": description,
            "filename": path.name,
            "uploaded_by": user["id"],
            "uploaded_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
        }

        try:
            with self.db.transaction():
                document_id = self.db.store_file(content, details)
        except sqlite3.Error as exc:
            raise ServiceError(
                "The document could not be saved. Please try again."
            ) from exc

        return document_id

    def search_documents(self, user, title="", doc_type=""):
        """Return document details matching the title and type.

        File contents are excluded from search results.
        An empty search returns all documents the feature permits access to.
        """
        self.authorize(user, "documents")

        title = (title or "").strip()
        doc_type = (doc_type or "").strip()

        sql = """
            SELECT id, title, doc_type, description, filename,
                   uploaded_by, uploaded_at
            FROM documents
            WHERE 1 = 1
        """
        params = []

        if title:
            # Treat %, _ and backslashes as literal search characters.
            escaped_title = (
                title.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            sql += " AND title LIKE ? ESCAPE '\\'"
            params.append(f"%{escaped_title}%")

        if doc_type:
            sql += " AND doc_type = ?"
            params.append(doc_type)

        sql += " ORDER BY id DESC"

        try:
            return self.db.query(sql, tuple(params))
        except sqlite3.Error as exc:
            raise ServiceError(
                "Documents could not be searched. Please try again."
            ) from exc

    def get_document(self, user, document_id):
        """Return the saved filename and original file contents."""
        self.authorize(user, "documents")

        if (
            isinstance(document_id, bool)
            or not isinstance(document_id, int)
            or document_id <= 0
        ):
            raise ValidationError("Please select a valid document.")

        try:
            document = self.db.get_file(document_id)
        except sqlite3.Error as exc:
            raise ServiceError(
                "The document could not be retrieved."
            ) from exc

        if document is None:
            raise NotFound("The selected document does not exist.")

        return document

    def download_document(self, user, document_id, destination):
        """Save a retrieved document to a user-selected destination.

        The interface must confirm before replacing an existing file.
        """
        filename, content = self.get_document(user, document_id)

        if not destination:
            raise ValidationError("Please choose a save location.")

        destination = Path(destination)

        if destination.is_dir():
            raise ValidationError(
                "Please choose a destination filename."
            )

        try:
            destination.write_bytes(content)
        except OSError as exc:
            raise ServiceError(
                "The document could not be downloaded."
            ) from exc

        return str(destination)