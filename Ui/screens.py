import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .. import (M6_Truck_Assignment,M3_Parts_Order,M2_Security,)#add you modules here
from .screen_helpers import (confirm, fill_tree, heading, labeled_combo, labeled_entry, make_tree, money, run,
                     selected_id)

def tim_e(c):
    return f"{c['start_time']}-{c['end_time']}"

def collection_row_s(rows):
    return [(c["id"], (c["date"], _time(c), c["customer"], c["address"], c["truck"] or "-",
                       c["status"])) for c in rows]

COLLECTION_COLUMNS = [("date", "Date", 90), ("time", "Time", 100), ("customer", "Customer", 170),
                      ("address", "Address", 150), ("truck", "Truck", 90), ("status", "Status", 90)]

#M6 SCREEEEEENNNNNN
##################################################################################################################################################################
class AssignmentScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.truck_map = {}
        heading(self, "Truck assignment (F-04)").pack(anchor="w")
        ttk.Label(self, text="Select a scheduled collection, then choose a truck. "
                             "A truck cannot be assigned to two different locations at overlapping times.").pack(anchor="w", pady=4)
        frame, self.tree=make_tree(self, COLLECTION_COLUMNS, height=12)
        frame.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        form = ttk.LabelFrame(self, text="Assign", padding=8)
        form.pack(fill="x", pady=8)
        self.truck, self.truck_box = labeled_combo(form, "Truck", 0, [], width=60, want_widget=True)
        ttk.Button(form, text="Assign", command=self.assign).grid(row=1, column=1, sticky="w", pady=6)
        self.refresh()

    def refresh(self, keep=None):
        rows = run(
            M5_Collection_Schedule.list_collections,
            self.app.db,
            self.app.user,
        ) or []
        fill_tree(self.tree,collection_row_s(rows))
        if keep is not None and self.tree.exists(str(keep)):
            self.tree.selection_set(str(keep))

    def on_select(self, _event=None):
        cid=selected_id(self.tree)
        if cid is None:
            return
        opts=run(M6_Truck_Assignment.these_good, self.app.db, self.app.user, cid)
        if opts is None:
            return
        c=M5_Collection_Schedule.get_collection(self.app.db, cid)#working with the assump M5 will have a func to  get collections; remember to rename to actual function

        def label(o):
            return o["name"] if o["available"] else f"{o['name']}  (NOT available: {o['note']})"

        self.truck_map = {label(o): o["id"] for o in opts["trucks"]}
        self.truck_box.configure(values=list(self.truck_map))
        self.truck.set(next((k for k, v in self.truck_map.items() if v==c["truck_id"]), ""))

    def assign(self):
        cid=selected_id(self.tree)
        if cid is None:
            messagebox.showinfo("Choose a collection", "Select a collection in the list first.")
            return
        result=run(M6_Truck_Assignment.assign, self.app.db, self.app.user, cid, self.truck_map.get(self.truck.get())) 
        if result:
            messagebox.showinfo("Assigned", f"{result['truck']} assigned to "
                                            f"{result['customer']} on {result['date']} ({tim_e(result)}).")
            self.refresh(keep=cid)
            self.on_select()
##################################################################################################################################################################
