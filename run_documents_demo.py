"""Standalone Document Management demo.

Uses the real database module.
Does not test the shared login or security module.
"""

from pathlib import Path
import tkinter as tk

from M9_Data_Access import Database
from M4_Document_Management import DocumentManager
from Ui.document_screen import DocumentScreen
from errors import PermissionDenied


def main():
    # Keep demo data outside the Git repository.
    demo_folder = Path.home() / "DonFranDocumentDemo"
    demo_folder.mkdir(exist_ok=True)

    database_path = demo_folder / "documents_demo.db"
    db = Database(str(database_path))

    # This account is for the standalone demo only.
    username = "document_demo_admin"
    users = db.find("users", username=username)

    if users:
        user = users[0]
    else:
        user_id = db.save(
            "users",
            {
                "username": username,
                "full_name": "Document Demo Administrator",
                "password_hash": "DEMO-ONLY-NO-LOGIN",
                "role": "Admin",
            },
        )
        user = db.get("users", user_id)

    def demo_authorize(current_user, action):
        """Temporary checker; replace with shared security.require."""
        if not current_user or action != "documents":
            raise PermissionDenied("Access denied.")

        stored_user = db.get("users", current_user.get("id"))

        if not stored_user or stored_user["role"] != "Admin":
            raise PermissionDenied("Access denied.")

    root = tk.Tk()
    root.title("DonFran — Document Management Demo")
    root.geometry("1050x700")
    root.minsize(850, 600)

    ttk_label = tk.Label(
        root,
        text=(
            "DEMO MODE: Document Management only. "
            "Shared login/security is not connected."
        ),
        bg="#fff3cd",
        fg="#664d03",
        padx=10,
        pady=8,
    )
    ttk_label.pack(fill="x")

    manager = DocumentManager(db, demo_authorize)
    screen = DocumentScreen(root, manager, user)
    screen.pack(fill="both", expand=True)

    def close_demo():
        screen.open_folder.cleanup()
        db.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_demo)
    root.mainloop()


if __name__ == "__main__":
    main()