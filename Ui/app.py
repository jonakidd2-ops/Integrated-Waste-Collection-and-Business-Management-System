import os
import tkinter as tk
from tkinter import messagebox, ttk

from ..import backup,M2_Security
from ..errors import ServiceError
from .import screens
#from .create_a_py_with_helper_functions that the screens may use import 

#menu text, permission needed, screen class
MENU=[
    ("Parts orders (F-01)", "Module_NAME_HERE", screens.Class_forSCren_here),
    ("Documents (F-02)", "Module_NAME_HERE", screens.Class_forSCren_here),
    ("Collection schedule (F-03)", "Module_NAME_HERE", screens.Class_forSCren_here),
    ("Truck assignment (F-04)", "Module_NAME_HERE", screens.Class_forSCren_here),
    ("Collection status (F-05)", "Module_NAME_HERE", screens.Class_forSCren_here),
    ("Contracts (F-06)", "Module_NAME_HERE", screens.Class_forSCren_here),]


class App(tk.Tk):
    def __init__(self, db, base_dir):
        super().__init__()
        self.db, self.base_dir = db, base_dir
        self.orders_dir = os.path.join(base_dir, "orders")
        self.backup_dir = os.path.join(base_dir, "backups")
        self.user = None
        self.title("DonFran Enterprise - Waste Collection and Business Management")
        self.geometry("1120x700")
        self.minsize(900, 600)
        self.show_login()

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()

    #login
    def show_login(self):
        self.user=None
        self._clear()
        outer=ttk.Frame(self, padding=40)
        outer.place(relx=0.5, rely=0.4, anchor="center")
        ttk.Label(outer, text="DonFran Enterprise", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(outer, text="Waste Collection and Business Management System").grid(row=1, column=0, columnspan=2, pady=(0, 18))
        ttk.Label(outer, text="Username").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(outer, text="Password").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        self.u, self.p = tk.StringVar(), tk.StringVar()
        user_entry = ttk.Entry(outer, textvariable=self.u, width=26)
        user_entry.grid(row=2, column=1, pady=4)
        pw_entry = ttk.Entry(outer, textvariable=self.p, width=26, show="*")
        pw_entry.grid(row=3, column=1, pady=4)
        pw_entry.bind("<Return>", lambda e: self.do_login())
        ttk.Button(outer, text="Log in", command=self.do_login).grid(row=4, column=1, sticky="e", pady=12)
        ttk.Label(outer, foreground="#666",
                  text="Gonna put the users here so we can remember: owner, admin, leader1, side1, leader2, side2 (password: demo123)").grid(
            row=5, column=0, columnspan=2)
        user_entry.focus_set()

    def do_login(self):
        try:
            user=M2_Security.login(self.db, self.u.get(), self.p.get())
        except ServiceError as e:
            messagebox.showerror("Login failed", str(e))
            self.p.set("")
            return
        self.user = user
        self.show_main()

    #main window
    def show_main(self):
        self._clear()
        header = ttk.Frame(self, padding=(10, 6))
        header.pack(fill="x")
        ttk.Label(header, text=f"{self.user['full_name']}  -  {self.user['role']}",
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(header, text="Log out", command=self.show_login).pack(side="right")
        if M2_Security.can(self.user["role"], "backup"):
            ttk.Button(header, text="Run backup now", command=self.run_backup).pack(side="right", padx=6)
        ttk.Separator(self).pack(fill="x")

        body=ttk.Frame(self)
        body.pack(fill="both", expand=True)
        nav=ttk.Frame(body, padding=8)
        nav.pack(side="left", fill="y")
        self.content = ttk.Frame(body)
        self.content.pack(side="left", fill="both", expand=True)
        first=None
        for text, action, cls in MENU:
            if M2_Security.can(self.user["role"], action):
                ttk.Button(nav, text=text, width=30, command=lambda c=cls: self.show_screen(c)).pack(pady=3)
                first = first or cls
        if first:
            self.show_screen(first)

    def show_screen(self, cls):
        for child in self.content.winfo_children():
            child.destroy()
        cls(self.content, self).pack(fill="both", expand=True)
