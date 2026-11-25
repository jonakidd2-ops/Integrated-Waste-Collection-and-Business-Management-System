import tempfile
import unittest
from pathlib import Path

from M9_Data_Access import Database
from M4_Document_Management import DocumentManager
from errors import PermissionDenied, ValidationError, NotFound, ServiceError


def test_permission_check(user, action):
    """Temporary permission policy for these tests only."""
    if not user or user.get("role") != "Admin":
        raise PermissionDenied("Access denied.")


class DocumentManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.database_path = self.folder / "test.db"
        self.db = Database(str(self.database_path))

        user_id = self.db.save("users", {
            "username": "test_admin",
            "full_name": "Test Administrator",
            "password_hash": "not-used-for-these-tests",
            "role": "Admin",
        })

        self.user = {"id": user_id, "role": "Admin"}
        self.manager = DocumentManager(self.db, test_permission_check)

        self.source = self.folder / "sample.txt"
        self.content = b"DonFran document management test."
        self.source.write_bytes(self.content)

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def upload(self, title="Truck Licence", doc_type="Licence"):
        return self.manager.upload_document(
            self.user, str(self.source), title, doc_type
        )

    def test_upload_and_download(self):
        document_id = self.upload()
        destination = self.folder / "downloaded.txt"

        self.manager.download_document(
            self.user, document_id, str(destination)
        )

        self.assertEqual(destination.read_bytes(), self.content)
        record = self.db.get("documents", document_id)
        self.assertEqual(record["title"], "Truck Licence")
        self.assertEqual(record["description"], "")

    def test_missing_required_information(self):
        cases = [
            ("", "Title", "Licence"),
            (str(self.source), "", "Licence"),
            (str(self.source), "Title", ""),
        ]

        for file_path, title, doc_type in cases:
            with self.subTest(title=title, doc_type=doc_type):
                with self.assertRaises(ValidationError):
                    self.manager.upload_document(
                        self.user, file_path, title, doc_type
                    )

        self.assertEqual(self.db.find("documents"), [])

    def test_missing_file(self):
        with self.assertRaises(ValidationError):
            self.manager.upload_document(
                self.user,
                str(self.folder / "missing.txt"),
                "Missing Document",
                "Other",
            )

    def test_unique_ids_and_persistent_storage(self):
        first_id = self.upload()
        second_id = self.upload()

        self.assertNotEqual(first_id, second_id)

        self.db.close()
        self.db = Database(str(self.database_path))
        self.manager = DocumentManager(self.db, test_permission_check)

        filename, content = self.manager.get_document(
            self.user, first_id
        )

        self.assertEqual(filename, "sample.txt")
        self.assertEqual(content, self.content)
        self.assertEqual(
            self.db.get("documents", first_id)["title"],
            "Truck Licence",
        )

    def test_search_and_type_filter(self):
        expected_id = self.upload("Truck Licence", "Licence")
        self.upload("Truck Contract", "Contract")
        self.upload("Office Licence", "Licence")

        results = self.manager.search_documents(
            self.user, title="Truck", doc_type="Licence"
        )

        self.assertEqual([row["id"] for row in results], [expected_id])
        self.assertNotIn("content", results[0])

    def test_no_search_results(self):
        self.upload()
        results = self.manager.search_documents(
            self.user, title="Nonexistent Document"
        )
        self.assertEqual(results, [])

    def test_unauthorized_access(self):
        document_id = self.upload()
        denied_user = {"id": self.user["id"], "role": "Sidemen"}
        destination = self.folder / "forbidden.txt"

        operations = [
            lambda: self.manager.upload_document(
                denied_user, str(self.source), "Title", "Licence"
            ),
            lambda: self.manager.search_documents(denied_user),
            lambda: self.manager.get_document(denied_user, document_id),
            lambda: self.manager.download_document(
                denied_user, document_id, str(destination)
            ),
        ]

        for operation in operations:
            with self.assertRaises(PermissionDenied):
                operation()

        self.assertFalse(destination.exists())
        self.assertEqual(len(self.db.find("documents")), 1)

    def test_nonexistent_document(self):
        with self.assertRaises(NotFound):
            self.manager.get_document(self.user, 99999)

    def test_storage_failure(self):
        self.db.close()

        with self.assertRaises(ServiceError):
            self.upload()


if __name__ == "__main__":
    unittest.main(verbosity=2)