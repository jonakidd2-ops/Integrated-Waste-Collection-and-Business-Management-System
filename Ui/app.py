import os
import tkinter as tk
from tkinter import messagebox, ttk

from ..import backup, security
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
