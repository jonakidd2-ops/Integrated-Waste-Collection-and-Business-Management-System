#Screen for M3 Parts Orders (F-01). Only shows data and calls M3_Parts_Order.
import tkinter as tk
from tkinter import messagebox, ttk

from .. import M3_Parts_Order
from .screen_helpers import confirm, fill_tree, heading, make_tree, money, run, selected_id


class PartsOrderScreen(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app, self.lines = app, []
        heading(self, "Request replacement parts (F-01)").grid(row=0, column=0, columnspan=2, sticky="w")

        left = ttk.LabelFrame(self, text="Available parts", padding=6)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=6)
        frame, self.parts_tree = make_tree(left, [("name", "Part", 170), ("type", "Type", 80), ("cost", "Unit cost", 70), ("supplier", "Supplier", 130)], height=9)
        frame.pack(fill="both", expand=True)
        row=ttk.Frame(left)
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text="Quantity").pack(side="left")
        self.qty = tk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.qty, width=6).pack(side="left", padx=6)
        ttk.Button(row, text="Add to order", command=self.add_line).pack(side="left")

        right = ttk.LabelFrame(self, text="Current order", padding=6)
        right.grid(row=1, column=1, sticky="nsew", pady=6)
        frame, self.order_tree = make_tree(right, [("name", "Part", 150), ("type", "Type", 80),
                                                   ("qty", "Qty", 40), ("cost", "Cost", 80)], height=9)
        frame.pack(fill="both", expand=True)
        self.total = tk.StringVar(value="Total: 0.00")
        ttk.Label(right, textvariable=self.total, font=("Segoe UI", 11, "bold")).pack(anchor="e", pady=4)
        row = ttk.Frame(right)
        row.pack(fill="x")
        ttk.Button(row, text="Remove selected", command=self.remove_line).pack(side="left")
        ttk.Button(row, text="Clear", command=self.clear).pack(side="left", padx=6)
        ttk.Button(row, text="Confirm and email to supplier", command=self.send).pack(side="right")

        hist = ttk.LabelFrame(self, text="Previous orders", padding=6)
        hist.grid(row=2, column=0, columnspan=2, sticky="nsew")
        frame, self.hist_tree = make_tree(hist, [("id", "Order", 70), ("date", "Date", 100),
                                                 ("status", "Status", 100), ("total", "Total", 100)], height=5)
        frame.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.refresh()

    def refresh(self):
        db, user = self.app.db, self.app.user
        parts = M3_Parts_Order.list_parts(db)
        fill_tree(self.parts_tree, [(p["id"], (p["name"], p["part_type"], money(p["unit_cost"]), p["supplier"] or ""))
                                    for p in parts])
        orders = run(M3_Parts_Order.list_orders, db, user) or []
        fill_tree(self.hist_tree, [(o["id"], (f"#{o['id']:04d}", o["order_date"], o["status"], money(o["total"])))
                                   for o in orders])
        self.show_order()

    def show_order(self):
        if not self.lines:
            fill_tree(self.order_tree, [])
            self.total.set("Total: 0.00")
            return
        priced =run(M3_Parts_Order.price_lines, self.app.db, self.lines) or []
        fill_tree(self.order_tree, [(r["part_id"], (r["name"], r["part_type"], r["quantity"], money(r["cost"])))
                                    for r in priced])
        self.total.set(f"Total: {money(sum(r['cost'] for r in priced))}")

    def add_line(self):
        part_id=selected_id(self.parts_tree)
        if part_id is None:
            messagebox.showinfo("Choose a part", "Select a part in the list first.")
            return
        try:
            qty=int(self.qty.get())
        except ValueError:
            messagebox.showerror("Quantity", "Quantity must be a whole number greater than zero.")
            return
        if qty <= 0:
            messagebox.showerror("Quantity", "Quantity must be a whole number greater than zero.")
            return
        for i, (pid, q) in enumerate(self.lines):
            if pid== part_id:
                self.lines[i]= (pid, q + qty)
                break
        else:
            self.lines.append((part_id, qty))
        self.show_order()

    def remove_line(self):
        part_id=selected_id(self.order_tree)
        self.lines= [(p, q) for p, q in self.lines if p != part_id]
        self.show_order()

    def clear(self):
        self.lines =[]
        self.show_order()

    def send(self):
        db, user = self.app.db, self.app.user
        priced=run(M3_Parts_Order.price_lines, db, self.lines)
        if priced is None:
            return
        total=sum(r["cost"] for r in priced)
        if not confirm("Confirm order", f"Send an order of {len(priced)} item(s), total {money(total)}, by email to the supplier?"):
            return
        def flow():
            order_id = M3_Parts_Order.create_order(db, user, self.lines)
            M3_Parts_Order.confirm_order(db, user, order_id)
            return order_id, M3_Parts_Order.send_order(db, user, order_id, self.app.orders_dir)

        result=run(flow)
        if result is None:
            return
        r=result[1]
        where=f"emailed to {r['to']}" if r["sent"] else f"saved as an email for {r['to']}\n(this doesn't actually send an email, it needs to be configured): {r['path']}"
        messagebox.showinfo("Order sent", f"Order #{result[0]:04d} {where}")
        self.lines = []
        self.refresh()
