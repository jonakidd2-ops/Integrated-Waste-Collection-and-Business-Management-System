from datetime import datetime
from . import M2_Security
from .errors import NotFound, ValidationError

SELECT=("SELECT c.id, c.customer_id, cu.name AS customer, c.address, c.date, c.start_time, c.end_time, "
           "c.status, c.truck_id, t.name AS truck "
           "FROM collections c JOIN customers cu ON cu.id = c.customer_id "
           "LEFT JOIN trucks t ON t.id = c.truck_id")


def check_fields(address, day, start, end):
    address=(address or "").strip()
    if not address:
        raise ValidationError("Enter the collection address.")
    try:
        datetime.strptime(day, "%Y-%m-%d")
        s=datetime.strptime(start, "%H:%M")
        e=datetime.strptime(end, "%H:%M")
    except (TypeError, ValueError):
        raise ValidationError("Use the date format YYYY-MM-DD and the time format HH:MM.")
    if e<=s:
        raise ValidationError("The end time must be after the start time.")
    return address

def list_customers(db):
    return db.find("customers")

def add_collection(db, user, customer_id, address, day, start, end):
    M2_Security.require(user, "schedules")
    address=check_fields(address, day, start, end)
    if db.get("customers", customer_id) is None:
        raise ValidationError("Choose a customer.")
    return db.save("collections", {"customer_id": customer_id, "address": address, "date": day,
                                   "start_time": start, "end_time": end, "status": "Scheduled"})

def update_collection(db, user, collection_id, customer_id, address, day, start, end):
    M2_Security.require(user, "schedules")
    if db.get("collections", collection_id) is None:
        raise NotFound("Collection not found.")
    address = check_fields(address, day, start, end)
    if db.get("customers",customer_id) is None:
        raise ValidationError("Choose a customer.")
    db.save("collections",{"id": collection_id, "customer_id": customer_id, "address": address,
                            "date": day, "start_time": start, "end_time": end})

def delete_collection(db, user, collection_id):  #The UI will be the one asks the user to confirm before calling this.
    M2_Security.require(user, "schedules")
    if db.get("collections", collection_id) is None:
        raise NotFound("Collection not found.")
    db.remove("collections", collection_id)

def get_collection(db, collection_id):
    rows=db.query(SELECT+ " WHERE c.id = ?", (collection_id,))
    if not rows:
        raise NotFound("Collection not found.")
    return rows[0]

def list_collections(db, user, customer_id=None, date_from=None, date_to=None):
    M2_Security.require(user,"view_collections")
    conds,params=[],[]
    if user["role"] in ("Team Leader","Sidemen"):
        conds.append("c.truck_id = ?")
        params.append(user["truck_id"])
    if customer_id:
        conds.append("c.customer_id = ?")
        params.append(customer_id)
    if date_from:
        conds.append("c.date >= ?")
        params.append(date_from)
    if date_to:
        conds.append("c.date <= ?")
        params.append(date_to)
    sql=SELECT + (" WHERE " + " AND ".join(conds) if conds else "") + " ORDER BY c.date, c.start_time"
    return db.query(sql, tuple(params))
  ##Go through it a tell me wha you think
