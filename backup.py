
#not immplemented into the system yet; but don't think we need anymore code than this for the implementation
#
import os
import sqlite3
import sys
from datetime import datetime


def run_backup(db_path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    name=f"donfran_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    dest=os.path.join(backup_dir, name)
    src=sqlite3.connect(db_path)
    dst=sqlite3.connect(dest)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return dest


def list_backups(backup_dir):
    if not os.path.isdir(backup_dir):
        return []
    return sorted(f for f in os.listdir(backup_dir) if f.endswith(".db"))


def restore(backup_path, db_path):
    #Replace the live database with a backup. Close the app first.
    src = sqlite3.connect(backup_path)
    dst = sqlite3.connect(db_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()


if __name__ == "__main__":
    here=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(run_backup(os.path.join(here, "donfran.db"), os.path.join(here, "backups")))
