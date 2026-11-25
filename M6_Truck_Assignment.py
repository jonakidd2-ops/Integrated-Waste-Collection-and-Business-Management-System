from datetime import datetime

from . import schedule_module_HERE, security
from .errors import Conflict, NotFound, ValidationError

CANCELED="Canceled" #varible to help identify a canceled collection; to make sure a canceled collection doesn't cause a conflict


def t_range(a): #range for timne for the collection; this converts it to a datetime object so i can compare them later
    return (datetime.strptime(f"{a['date']} {a['start_time']}", "%Y-%m-%d %H:%M"), datetime.strptime(f"{a['date']} {a['end_time']}", "%Y-%m-%d %H:%M"))
def does_overlap(start, end, startcmp, endcmp): #checks if time ovelaps 
  return end<startcmp and endcmp>startcmp #this also account for if a collection end at a specified time and another begins at that same specified time and doesn't treat that as an overlap
def relevant_col(db,notrk_col):
    return db.query("SELECT * FROM collections WHERE date=? AND id!=?",(notrk_col["date"],notrk_col["id"]))#pulls collections for the same day exclluding the one to be assigned

def clash(notrk_col,trks_col,trk_id,val):
    clashy=[]
    notrk_col_start,notrk_col_end=t_range(notrk_col)
    for d in trks_col:
        if d[trk_id]!=val or d["id"]==notrk_col["id"] or d["status"]==CANCELED:
            continue
        if d["address"]==notrk_col["address"]:
            continue
        d_start, d_end=t_range(d)
        if does_overlaps(notrk_col_start, notrk_col_end, d_start, d_end):
            clashy.append(d)
    return clashy


    
