"""DonFran Enterprise Waste Collection and Business Management System entry point.
    python main.py            start the app (creates donfran.db and the demo data on the first run)
    python main.py --reset    used tto reset the database for the demo;technically delete and redo like a blank entry;"""


import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = "donfran"
DB_FILE = os.path.join(HERE, "donfran.db")


def load_package():
    """Make this folder importable as the package 'donfran'."""
    spec = importlib.util.spec_from_file_location(
        PACKAGE, os.path.join(HERE, "__init__.py"), submodule_search_locations=[HERE])
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE] = module
    spec.loader.exec_module(module)


def main():
    try:
        import tkinter  # noqa: F401
    except ImportError:
        sys.exit("Tkinter is not installed.")

    load_package()
    from donfran import seed
    from donfran.M9_Data_Access import Database
    from donfran.Ui.app import App

    if "--reset" in sys.argv and os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db= Database(DB_FILE)      # M9 is the only module that opens the database
    seed.seed(db)               # adds the demo users, trucks, customers and collections once
    app = App(db, HERE)         # M1 is the login window, then the menu for the user's role
    try:
        app.mainloop()
    finally:
        db.close()


if __name__ == "__main__":
    main()
