from datetime import datetime

from . import schedule_module_HERE, security
from .errors import Conflict, NotFound, ValidationError

CANCELED="Canceled" #varible for a canceled collection

def t_range(a): #range for timne for the collection
    return (datetime.strptime(f"{a['date']} {c['start_time']}", "%Y-%m-%d %H:%M"), datetime.strptime(f"{a['date']} {c['end_time']}", "%Y-%m-%d %H:%M"))
def does_overlap(start, end, startcmp, endcmp): #checks if time ovelaps 
  return end<startcmp and endcmp>startcmp
