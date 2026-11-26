import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .. import (M6_Truck_Assignment,M3_Parts_Order,M2_Security,M5)#add you modules here
from .screen_helpers import (confirm, fill_tree, heading, labeled_combo, labeled_entry, make_tree, money, run,
                     selected_id)

def tim_e(c):
    return f"{c['start_time']}-{c['end_time']}"

def collection_row_s(rows):
    return [(c["id"], (c["date"], tim_e(c), c["customer"], c["address"], c["truck"] or "-",
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
        self.truck, self.truck_box=labeled_combo(form, "Truck", 0, [], width=60, want_widget=True)
        ttk.Button(form, text="Assign", command=self.assign).grid(row=1, column=1, sticky="w", pady=6)
        self.refresh()

    def refresh(self, keep=None):
        rows=run(M5.list_collections,
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
        c=M5.get_collection(self.app.db, cid)

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
#Screen for M5
##################################################################################################################################################################
class SchedulesScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.customers = {c["name"]: c["id"] for c in M5.list_customers(app.db)}
        heading(self, "Collection schedule (F-03)").pack(anchor="w")
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=6)
        ttk.Label(bar, text="Customer").pack(side="left")
        self.f_customer = tk.StringVar(value="All")
        ttk.Combobox(bar, textvariable=self.f_customer, values=["All"] + list(self.customers), width=24,
                     state="readonly").pack(side="left", padx=6)
        ttk.Label(bar, text="From").pack(side="left")
        self.f_from = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_from, width=11).pack(side="left", padx=6)
        ttk.Label(bar, text="To").pack(side="left")
        self.f_to = tk.StringVar()
        ttk.Entry(bar, textvariable=self.f_to, width=11).pack(side="left", padx=6)
        ttk.Button(bar, text="Filter", command=self.refresh).pack(side="left")
        ttk.Label(bar, text="(dates as YYYY-MM-DD)").pack(side="left", padx=8)
        frame, self.tree = make_tree(self, COLLECTION_COLUMNS, height=10)
        frame.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ttk.LabelFrame(self, text="Collection details", padding=8)
        form.pack(fill="x", pady=8)
        self.customer=labeled_combo(form, "Customer *", 0, list(self.customers))
        self.address=labeled_entry(form, "Address *", 1)
        self.day=labeled_entry(form, "Date * (YYYY-MM-DD)", 0, col=2, width=14)
        self.start=labeled_entry(form, "Start * (HH:MM)", 1, col=2, width=14)
        self.end=labeled_entry(form, "End * (HH:MM)", 2, col=2, width=14)
        row=ttk.Frame(self)
        row.pack(fill="x")
        ttk.Button(row, text="Add as new", command=self.add).pack(side="left")
        ttk.Button(row, text="Update selected", command=self.update).pack(side="left", padx=6)
        ttk.Button(row, text="Delete selected", command=self.delete).pack(side="left")
        ttk.Button(row, text="Clear form", command=self.clear).pack(side="left", padx=6)
        self.refresh()

    def refresh(self):
        cust=self.customers.get(self.f_customer.get())
        rows=run(M5.list_collections, self.app.db, self.app.user, cust, self.f_from.get().strip() or None, self.f_to.get().strip() or None) or []
        fill_tree(self.tree, collection_row_s(rows))

    def on_select(self, _event=None):
        cid = selected_id(self.tree)
        if cid is None:
            return
        c=M5.get_collection(self.app.db, cid)
        self.customer.set(c["customer"])
        self.address.set(c["address"])
        self.day.set(c["date"])
        self.start.set(c["start_time"])
        self.end.set(c["end_time"])

    def _values(self):
        return (self.customers.get(self.customer.get()), self.address.get(), self.day.get().strip(),
                self.start.get().strip(), self.end.get().strip())

    def add(self):
        if run(M5.add_collection, self.app.db, self.app.user, *self._values()) is not None:
            self.clear()
            self.refresh()

    def update(self):
        cid = selected_id(self.tree)
        if cid is None:
            messagebox.showinfo("Choose a collection", "Select a collection in the list first.")
            return
        run(M5.update_collection, self.app.db, self.app.user, cid, *self._values())
        self.refresh()

    def delete(self):
        cid = selected_id(self.tree)
        if cid is None:
            messagebox.showinfo("Choose a collection", "Select a collection in the list first.")
            return
        if confirm("Delete collection", "Delete this collection schedule?"):
            run(M5.delete_collection, self.app.db, self.app.user, cid)
            self.clear()
            self.refresh()

    def clear(self):
        for v in (self.customer, self.address, self.day, self.start, self.end):
            v.set("")
###################################################################################################################################################################
#M3 Screen
###################################################################################################################################################################
#Let me know if something is wrong here
class OrderScreen(ttk.Frame):
    def __init__(self, parent, app):
        super.__init__(parent, padding = 10)
        self.app = app
        parts_dict = {
            "Brake Pads": {"Cost": 7000},
            "Oil Filter": {"Cost": 12000},
            "Air Filter": {"Cost": 5150},
            "Tire": {"Cost": 8000},
            "Headlamp": {"Cost": 6500},
            "Windshield Wiper": {"Cost": 2000},
            "Steering Wheel": {"Cost": 4000}
        }
        part_window = tk.Frame(self, bg="lightblue")
        part_window.pack(fill="both", expand=True)
        tk.Label(part_window, text="Part Name:").grid(row=0, column=0, padx=10, pady=10)
        p_name = ttk.Combobox(part_window)
        p_name['values'] = tuple(parts_dict.keys())
        p_name.current()
        p_name.grid(row=0, column=1, padx=10, pady=10)
        p_name.bind("<<ComboboxSelected>>", self.choice)

        tk.Label(part_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=10)
        p_quantity = tk.Spinbox(part_window, from_=1, to=10)
        p_quantity.grid(row=1, column=1, padx=10, pady=10)

        #Dummy supplier email
        tk.Label(part_window, text="Supplier Email:").grid(row=2, column=0, padx=10, pady=10)
        default = tk.StringVar(value="harrycolesparts@gmail.com")
        supp_email_E = tk.Entry(part_window, textvariable=default)
        supp_email_E.grid(row=2, column=1, padx=10, pady=10)

        order_state = {"counter": 0, "items": {}}
        pending = tk.Label(part_window, text="Pending Order:\nTotal Cost: 0")
        pending.grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(part_window, text="Send Order", width = 10,
                command=lambda: self.send(order_state, supp_email_E.get()),
        ).grid(row=5, column=0, pady=10)
        tk.Button(part_window, text="Add Part", width = 10,
            command=lambda: self.add(
                p_name.get(), p_quantity.get(), parts_dict, order_state, pending
            ),
        ).grid(row=4, column=0, pady=10)
        
        tk.Button(part_window, text="Remove Part", width = 10,
            command=lambda: self.remove(order_state, pending),
        ).grid(row=4, column=1, pady=10)
        #tk.Button(part_window, text="Back", width = 10, command=self.back_Btn).grid(row=5, column=1, pady=10)
        text_widget = tk.Text(part_window, height=10, width=50)
        text_widget.grid(row=7, column=0, rowspan=4, columnspan=2, pady=10)
        tk.Button(part_window, text="View History", command=self.open_file).grid(row=6, column=0, columnspan=2, pady=10)

    def back_Btn(self):
        self.destroy()

    def choice(self, event):
        details = tk.Label(self.part_window, text=f"Name: {event.widget.get()}\nCost: \
{self.parts_dict[event.widget.get()]['Cost']}\n\
*These are speculative prices and may not reflect those\n \
on the invoice sent by the supplier", justify="left")
        details.grid(row=0, column=2, rowspan=2, columnspan=2, pady=10)

    def refresh(self, order_state, pending):
        order_lines, total = run(M3_Parts_Order.order_details, order_state)
        pending.config(
            text=f"Pending Order:\n" + "\n".join(order_lines) + f"\nTotal Cost: {total}"
        )

    def send(self, order_state, supplier_email):
        response = run(M3_Parts_Order.send_order, order_state, supplier_email)
        if response:
            messagebox.showinfo("Order Sent", "Order sent successfully!")
            order_state["counter"] = 0
            order_state["items"] = {}
            self.refresh(order_state, self.pending)
        else:
            messagebox.showerror("Error", "Failed to send order, check supplier email or order details.")

    def add(self, name, quan, parts_dict, order_state, pending):
        try:
            quan = int(quan)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a whole number.")
            return
        if name not in parts_dict or not 1 <= quan <= 10:
            messagebox.showerror("Error", "Select a valid part and enter a quantity from 1 to 10.")
            return
        order_state["counter"] += 1
        part_id = order_state["counter"]
        order_state["items"][part_id] = {
            "part": name,
            "number": quan,
            "price": parts_dict[name]["Cost"],
        }
        self.refresh(order_state, pending)

    def remove(self, order_state, pending):
        items = order_state["items"]
        if not items:
            messagebox.showerror("Error", "No parts to remove.")
            return
        part_id = max(items)
        del items[part_id]
        order_state["counter"] -= 1
        self.refresh(order_state, pending)

    def open_file(self):
        file_path = "sent_orders.txt"
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)

