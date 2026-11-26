
#this is the sample data for the database
#we can remove this after we run it once since it will have the database
from datetime import date, timedelta

from . import M2_Security as security

PASSWORDS="1234" #used a universal password to save us the headache


def seed(db):
    if db.find("users"):
        return False  #already seeded
    d=lambda n: (date.today() + timedelta(days=n)).isoformat()
    pw=security.hash_pswrd(PASSWORDS)
    with db.transaction():
        t1=db.save("trucks", {"name": "Truck 1"})
        t2=db.save("trucks", {"name": "Truck 2"})
        db.save("trucks", {"name": "Truck 3"})
        # Team Leaders and Sidemen crew a truck and only see that truck's collections
        for username, name, role, truck in [
            ("owner", "Owner", "Owner", None), ("admin", "Admin", "Admin", None),
            ("leader1", "Truck 1 Leader", "Team Leader", t1), ("side1", "Truck 1 Sidemen", "Sidemen", t1),
            ("leader2", "Truck 2 Leader", "Team Leader", t2), ("side2", "Truck 2 Sidemen", "Sidemen", t2)]:
            db.save("users", {"username": username, "full_name": name, "password_hash": pw, "role": role, "truck_id": truck})

        s1 = db.save("suppliers", {"name": "Island Truck Parts", "contact": "orders@islandtruckparts.example"})
        s2 = db.save("suppliers", {"name": "Kingston Hydraulics", "contact": "sales@kingstonhydraulics.example"})
        for name, ptype, cost, sup in [
            ("Hydraulic hose 2m", "Hydraulic", 85.50, s2), ("Hydraulic pump seal kit", "Hydraulic", 120.00, s2),
            ("Compactor ram", "Hydraulic", 640.00, s2), ("Rear tyre 295/80", "Tyres", 310.00, s1),
            ("Front tyre 275/70", "Tyres", 275.00, s1), ("Air filter", "Filters", 42.75, s1),
            ("Oil filter", "Filters", 18.90, s1), ("Brake pad set", "Brakes", 96.40, s1),
            ("Tail light assembly", "Electrical", 54.00, s1)]:
            db.save("parts", {"name": name, "part_type": ptype, "unit_cost": cost, "supplier_id": sup})

        names=[("Sunrise Hotel", "876-555-0101"), ("Palm Plaza", "876-555-0102"), ("Harbour View Apartments", "876-555-0103"),
                 ("Green Valley School", "876-555-0104"), ("Market Square Vendors", "876-555-0105")]
        cid= {n: db.save("customers", {"name": n, "contact": c}) for n, c in names}

        def coll(cust, addr, day, start, end, truck=None, status="Scheduled"):
            return db.save("collections", {"customer_id": cid[cust], "address": addr, "date": d(day), "start_time": start,
                                           "end_time": end, "truck_id": truck, "status": status})
        # Truck 1 is booked 09:00-11:00 at Sunrise Hotel. Assigning Truck 1 to the Palm Plaza job
        coll("Sunrise Hotel", "12 Beach Rd", 1, "09:00", "11:00", t1)
        coll("Palm Plaza", "40 Palm Ave", 1, "10:00", "12:00")
        coll("Harbour View Apartments", "7 Harbour St", 1, "13:00", "14:30", t2)
        coll("Green Valley School", "3 School Lane", 2, "08:00", "09:30")
        coll("Market Square Vendors", "Market Sq", 2, "14:00", "16:00", t1)
        coll("Sunrise Hotel", "12 Beach Rd", 3, "09:00", "11:00")
        coll("Palm Plaza", "40 Palm Ave", -1, "10:00", "12:00", t1, "Completed")

        db.save("contracts", {"customer_id": cid["Sunrise Hotel"], "details": "Twice weekly commercial waste collection",
                              "start_date": d(-120), "end_date": d(245)})
        db.save("contracts", {"customer_id": cid["Green Valley School"], "details": "Weekly collection during school terms",
                              "start_date": d(-60), "end_date": d(300)})
    return True
