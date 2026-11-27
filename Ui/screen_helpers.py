#these are just potential functions that may help with the writing of the screens so we don't overpopulate screens
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from ..errors import ServiceError

def run(action, *args, **kwargs):
    """Call a feature module function. Shows the error and returns None if it fails."""
    try:
        return action(*args, **kwargs)
    except ServiceError as e:
        messagebox.showerror("Cannot complete this action", str(e))
    except sqlite3.Error as e:     # storage failure: show an error, never a success message
        messagebox.showerror("Storage error", f"The data could not be saved or read, and nothing was changed.\n({e})")
    return None

def confirm(title, message):
    return messagebox.askyesno(title, message)

def make_tree(parent, columns, height=8):
    """columns: list of (id, heading, width). Returns (frame, tree); rows are keyed by their record id."""
    frame= ttk.Frame(parent)
    tree= ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings", height=height, selectmode="browse")
    for cid, heading, width in columns:
        tree.heading(cid, text=heading)
        tree.column(cid, width=width, anchor="w")
    bar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=bar.set)
    tree.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")
    return frame, tree

def fill_tree(tree, rows):
    """rows: list of (record_id, values). Replaces the table contents."""
    tree.delete(*tree.get_children())
    for rid, values in rows:
        tree.insert("", "end", iid=str(rid), values=values)

def selected_id(tree):
    sel = tree.selection()
    return int(sel[0]) if sel else None

def labeled_entry(parent, text, row, width=28, col=0):
    ttk.Label(parent, text=text).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=2)
    var = tk.StringVar()
    ttk.Entry(parent, textvariable=var, width=width).grid(row=row, column=col + 1, sticky="w", pady=2)
    return var

def labeled_combo(parent, text, row, values, width=26, col=0, want_widget=False):
    ttk.Label(parent, text=text).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=2)
    var = tk.StringVar()
    box = ttk.Combobox(parent, textvariable=var, values=values, width=width, state="readonly")
    box.grid(row=row, column=col + 1, sticky="w", pady=2)
    return (var, box) if want_widget else var

def heading(parent, text):
    return ttk.Label(parent, text=text, font=("Segoe UI", 14, "bold"))

def money(value):
    return f"{value:,.2f}"
