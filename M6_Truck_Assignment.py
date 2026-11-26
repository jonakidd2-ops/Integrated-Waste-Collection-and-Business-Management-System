from datetime import datetime

from . import M5, M2_Security
from .errors import Conflict, NotFound, ValidationError

CANCELED="Canceled" #varible to help identify a canceled collection; to make sure a canceled collection doesn't cause a conflict


def t_range(a): #range for timne for the collection; this converts it to a datetime object so i can compare them later
    return (datetime.strptime(f"{a['date']} {a['start_time']}", "%Y-%m-%d %H:%M"), datetime.strptime(f"{a['date']} {a['end_time']}", "%Y-%m-%d %H:%M"))
def does_overlap(start, end, startcmp, endcmp): #checks if time ovelaps 
  return start<endcmp and startcmp<end #this also account for if a collection end at a specified time and another begins at that same specified time and doesn't treat that as an overlap
def relevant_col(db,notrk_col):#pulls collections for the same day exclluding the one to be assigned
    return db.query("SELECT * FROM collections WHERE date=? AND id!=?",(notrk_col["date"],notrk_col["id"]))

def clash(col_to_asgn,trks_col,trk_id,trk): #(col to be assigned trk,cols that may be using trk,dic key containing trk id,id of truck to assign)
    clashy=[]#list to store clashes
    col_to_asgn_start,col_to_asgn_end=t_range(col_to_asgn) #range for collection to be assigned
    for d in trks_col: #other collections
        if d[trk_id]!=trk or d["id"]==col_to_asgn["id"] or d["status"]==CANCELED:#skips a collection if it uses a different truck, it is canceled or its the collection being assigned
            continue
        if d["address"]==col_to_asgn["address"]:#skips a col if there at the same adress
            continue
        d_start, d_end=t_range(d)
        if does_overlaps(col_to_asgn_start, col_to_asgn_end, d_start, d_end): #check if the time ovelaps and add it to the list clashes
            clashy.append(d)
    return clashy

def these_good(db,user,collection_id):
    security.require(user,"M6_Truck_Assignment")#checks permissions of user
    col_to_asgn=db.get("collections", collection_id) #get the collection info from database
    out=[]
    if col_to_asgn is None: #makes sure the collection exists
        raise NotFound("Collection does not exist.")
    trks_col=relevant_col(db,col_to_asgn)#making sure we don't bother with irrelevant collections
    for t in db.find("trucks"): #looping trough the trucks
        not_good=clash(col_to_asgn,trks_col,"truck_id",t["id"])#check if clash exist for each truck
        msg=f"busy {not_good[0]['start_time']}-{not_good[0]['end_time']} at {not_good[0]["address"]}" if not_good else "" #tells you why where the confilct exist if i does
        out.append({"id": t["id"], "name": t["name"], "available": not not_good, "note": msg}) 
    return{"trucks": out}

def assign(db, user, collection_id, truck_id):
    security.require(user, "M6_Truck_Assignment")
    if truck_id is None:
        raise ValidationError("Choose a truck.")
    with db.transaction():
        col_to_asgn=db.get("collections", collection_id)
        if col_to_asgn is None:
            raise NotFound("Collection not found.")
        truck = db.get("trucks", truck_id)
        if truck is None:
            raise ValidationError("Choose a valid truck.")
        not_good=clash(col_to_asgn,relevant_col(db, col_to_asgn), "truck_id", truck_id)
        if not_good:
            raise Conflict(f"{truck['name']} is already assigned to {not_good[0]['address']} "
                           f"from {not_good[0]['start_time']} to {not_good[0]['end_time']}.")
        db.save("collections", {"id": collection_id, "truck_id": truck_id})
    return M5.get_collection(db, collection_id)
        
        
        
    


    
