"""Graphical interface for F-02: Document Management."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class DocumentScreen(ttk.Frame):
    def __init__(self, parent, manager, user):
        super().__init__(parent, padding=15)

        self.manager = manager
        self.user = user
        self.selected_file = ""

        # Temporary copies are used when opening stored documents.
        self.open_folder = tempfile.TemporaryDirectory(
            prefix="donfran_documents_"
        )

        self.title_value = tk.StringVar()
        self.type_value = tk.StringVar()
        self.description_value = tk.StringVar()
        self.file_value = tk.StringVar(value="No file selected")

        self.search_value = tk.StringVar()
        self.filter_value = tk.StringVar()
        self.status_value = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.build_upload_form()
        self.build_search_controls()
        self.build_document_table()
        self.build_action_buttons()

        self.refresh_documents()

    def build_upload_form(self):
        form = ttk.LabelFrame(
            self, text="Upload a business document", padding=12
        )
        form.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Title *").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(form, textvariable=self.title_value).grid(
            row=0, column=1, sticky="ew", pady=5
        )

        ttk.Label(form, text="Document type *").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Combobox(
            form,
            textvariable=self.type_value,
            values=("Contract", "Invoice", "Licence", "Other"),
        ).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="Description").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(form, textvariable=self.description_value).grid(
            row=2, column=1, sticky="ew", pady=5
        )

        ttk.Button(
            form, text="Choose file *", command=self.choose_file
        ).grid(row=3, column=0, sticky="w", pady=8)

        ttk.Label(
            form, textvariable=self.file_value, wraplength=500
        ).grid(row=3, column=1, sticky="w", pady=8)

        ttk.Button(
            form, text="Upload document", command=self.upload_document
        ).grid(row=4, column=1, sticky="e", pady=5)

    def build_search_controls(self):
        controls = ttk.LabelFrame(
            self, text="Find documents", padding=12
        )
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Title contains").grid(
            row=0, column=0, padx=(0, 8)
        )
        search_entry = ttk.Entry(
            controls, textvariable=self.search_value
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        search_entry.bind(
            "<Return>", lambda event: self.refresh_documents()
        )

        ttk.Label(controls, text="Type").grid(
            row=0, column=2, padx=(0, 8)
        )
        ttk.Combobox(
            controls,
            textvariable=self.filter_value,
            values=("", "Contract", "Invoice", "Licence", "Other"),
            width=16,
        ).grid(row=0, column=3, padx=(0, 10))

        ttk.Button(
            controls, text="Search", command=self.refresh_documents
        ).grid(row=0, column=4, padx=(0, 5))

        ttk.Button(
            controls, text="Show all", command=self.show_all
        ).grid(row=0, column=5)

        ttk.Label(self, textvariable=self.status_value).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

    def build_document_table(self):
        container = ttk.Frame(self)
        container.grid(row=3, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        columns = ("id", "title", "type", "filename", "uploaded")
        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID",
            "title": "Title",
            "type": "Type",
            "filename": "Original filename",
            "uploaded": "Uploaded (UTC)",
        }

        for name, label in headings.items():
            self.table.heading(name, text=label)
            self.table.column(name, width=150, minwidth=60)

        self.table.column("id", width=55, stretch=False)
        self.table.column("title", width=220)

        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def build_action_buttons(self):
        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        ttk.Button(
            actions, text="Open selected", command=self.open_document
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions,
            text="Download selected",
            command=self.download_document,
        ).pack(side="left")

    def choose_file(self):
        selected = filedialog.askopenfilename(
            parent=self,
            title="Choose a business document",
        )

        if selected:
            self.selected_file = selected
            self.file_value.set(Path(selected).name)

    def upload_document(self):
        try:
            document_id = self.manager.upload_document(
                self.user,
                self.selected_file,
                self.title_value.get(),
                self.type_value.get(),
                self.description_value.get(),
            )
        except Exception as exc:
            messagebox.showerror("Upload failed", str(exc), parent=self)
            return

        self.title_value.set("")
        self.type_value.set("")
        self.description_value.set("")
        self.selected_file = ""
        self.file_value.set("No file selected")

        self.show_all()

        messagebox.showinfo(
            "Upload successful",
            f"Document saved successfully. Document ID: {document_id}",
            parent=self,
        )

    def refresh_documents(self):
        # Clear previous results, including after a denied request.
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            documents = self.manager.search_documents(
                self.user,
                title=self.search_value.get(),
                doc_type=self.filter_value.get(),
            )
        except Exception as exc:
            self.status_value.set("Documents could not be loaded.")
            messagebox.showerror(
                "Search failed", str(exc), parent=self
            )
            return

        for document in documents:
            self.table.insert(
                "",
                "end",
                iid=str(document["id"]),
                values=(
                    document["id"],
                    document["title"],
                    document["doc_type"],
                    document["filename"],
                    document["uploaded_at"],
                ),
            )

        if documents:
            self.status_value.set(
                f"{len(documents)} document(s) found."
            )
        else:
            self.status_value.set("No matching documents were found.")

    def show_all(self):
        self.search_value.set("")
        self.filter_value.set("")
        self.refresh_documents()

    def selected_document_id(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showwarning(
                "Select a document",
                "Please select a document from the list.",
                parent=self,
            )
            return None

        return int(selected[0])

    def download_document(self):
        document_id = self.selected_document_id()
        if document_id is None:
            return

        try:
            filename, _ = self.manager.get_document(
                self.user, document_id
            )

            destination = filedialog.asksaveasfilename(
                parent=self,
                title="Download document",
                initialfile=Path(filename).name,
            )

            if not destination:
                return

            if Path(destination).exists():
                confirmed = messagebox.askyesno(
                    "Replace file?",
                    "A file already exists at this location. Replace it?",
                    parent=self,
                )
                if not confirmed:
                    return

            self.manager.download_document(
                self.user, document_id, destination
            )
        except Exception as exc:
            messagebox.showerror(
                "Download failed", str(exc), parent=self
            )
            return

        messagebox.showinfo(
            "Download successful",
            "The document was saved to your selected location.",
            parent=self,
        )

    def open_document(self):
        document_id = self.selected_document_id()
        if document_id is None:
            return

        try:
            filename, content = self.manager.get_document(
                self.user, document_id
            )

            # Keep each document in a separate temporary directory.
            folder = Path(self.open_folder.name) / str(document_id)
            folder.mkdir(exist_ok=True)

            target = folder / Path(filename).name
            target.write_bytes(content)

            if sys.platform == "darwin":
                subprocess.run(["open", str(target)], check=True)
            elif sys.platform == "win32":
                os.startfile(str(target))
            else:
                subprocess.run(["xdg-open", str(target)], check=True)

        except Exception as exc:
            messagebox.showerror(
                "Open failed", str(exc), parent=self
            )