#Screen for M8 Contract Management (F-06).
#it shows data and calls ContractManagement
import tkinter as tk
from tkinter import messagebox, ttk

from ..M8_Contract_Management import ContractManagement
from .screen_helpers import fill_tree, heading, labeled_combo, labeled_entry, make_tree, run, selected_id


class ContractsScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app= app
        self.m8= ContractManagement(app.db)           # M8 receives the M9 Database object
        self.customers= {}
        heading(self, "Contracts (F-06)").pack(anchor="w")

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=6)
        ttk.Label(bar, text="Search customer or details").pack(side="left")
        self.q =tk.StringVar()
        ttk.Entry(bar, textvariable=self.q, width=28).pack(side="left", padx=6)
        ttk.Button(bar, text="Search", command=self.refresh).pack(side="left")

        frame, self.tree= make_tree(self, [("customer", "Customer", 170), ("details", "Details", 280),
                                            ("start", "Start", 90), ("end", "End", 90), ("doc", "Document", 80)],
                                     height=9)
        frame.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        cust=ttk.LabelFrame(self, text="New customer (a contract needs an existing customer)", padding=8)
        cust.pack(fill="x", pady=(8, 0))
        self.new_name= labeled_entry(cust, "Customer name *", 0)
        self.new_contact=labeled_entry(cust, "Contact info", 1)
        ttk.Button(cust, text="Add customer", command=self.add_customer).grid(row=0, column=2, rowspan=2, padx=12)

        form = ttk.LabelFrame(self, text="Contract details", padding=8)
        form.pack(fill="x", pady=8)
        self.customer, self.customer_box = labeled_combo(form, "Customer *", 0, [], want_widget=True)
        self.details= labeled_entry(form, "Contract details *", 1, width=44)
        self.start= labeled_entry(form, "Start date * (YYYY-MM-DD)", 0, col=2, width=14)
        self.end= labeled_entry(form, "End date * (YYYY-MM-DD)", 1, col=2, width=14)
        self.doc= labeled_entry(form, "Document id (optional)", 2, col=2, width=14)

        row = ttk.Frame(self)
        row.pack(fill="x")
        ttk.Button(row, text="Save as new contract", command=self.save_new).pack(side="left")
        ttk.Button(row, text="Update selected", command=self.update).pack(side="left", padx=6)
        ttk.Button(row, text="Clear form", command=self.clear).pack(side="left")
        self.load_customers()
        self.refresh()

    def load_customers(self):
        rows=run(self.m8.list_customers, self.app.user) or []
        self.customers = {c["name"]: c["id"] for c in rows}
        self.customer_box.configure(values=list(self.customers))

    def refresh(self):
        rows=run(self.m8.find_contracts, self.app.user, self.q.get()) or []
        fill_tree(self.tree, [(k["id"], (k["customer_name"], k["details"], k["start_date"], k["end_date"],
                                         f"DOC-{k['document_id']:04d}" if k["document_id"] else "-"))for k in rows])

    def on_select(self, _event=None):
        kid=selected_id(self.tree)
        if kid is None:
            return
        k=run(self.m8.get_contract, self.app.user, kid)
        if k is None:
            return
        self.customer.set(k["customer_name"])
        self.details.set(k["details"])
        self.start.set(k["start_date"])
        self.end.set(k["end_date"])
        self.doc.set(str(k["document_id"] or ""))

    def add_customer(self):
        name=self.new_name.get()
        if run(self.m8.create_customer, self.app.user, name, self.new_contact.get()) is not None:
            self.load_customers()
            self.customer.set(name.strip())
            self.new_name.set("")
            self.new_contact.set("")
    def _values(self):
        raw=self.doc.get().strip()
        if raw and not raw.isdigit():
            messagebox.showerror("Document id", "The document id must be a number (or left empty).")
            return None
        return (self.customer.get(), self.details.get(), self.start.get().strip(), self.end.get().strip(),
                int(raw) if raw else None)
    def save_new(self):
        vals=self._values()
        if vals and run(self.m8.create_contract, self.app.user, *vals) is not None:
            self.clear()
            self.refresh()
    def update(self):
        kid=selected_id(self.tree)
        if kid is None:
            messagebox.showinfo("Choose a contract", "Select a contract in the list first.")
            return
        vals=self._values()
        if vals:
            run(self.m8.update_contract, self.app.user, kid, *vals)
            self.refresh()
    def clear(self):
        for v in (self.customer, self.details, self.start, self.end, self.doc):
            v.set("")
