
from . import M2_Security
from . import M5_Collection_Sched
from .errors import NotFound, PermissionDenied, ValidationError

Valid_Status = ("Completed", "Missed", "Canceled")
PERMISSION = "M7_Collection_Status"      


def list_collections(db, user):
    #Collections the user may see (own truck only for a Team Leader). Reuses M5.
    M2_Security.require(user, PERMISSION)
    return M5_Collection_Sched.list_collections(db, user)

def get_collection(db, user, collection_id):
    #One collection with its customer and truck names. Raises NotFound if it does not exist.
    M2_Security.require(user, PERMISSION)
    return M5_Collection_Sched.get_collection(db, collection_id)

def update_status(db, user, collection_id, new_status):
    #Save a new status against that one collection only, and return the updated collection."
    M2_Security.require(user, PERMISSION)

    if isinstance(collection_id, bool) or not isinstance(collection_id, int):
        raise ValidationError("Please select a collection")
    if new_status not in Valid_Status:
        raise ValidationError("Choose Completed, Missed or Canceled.")

    with db.transaction():
        collection = db.get("collections", collection_id)          
        if collection is None:
            raise NotFound("Collection not found.")
        # A Team Leader may only update collections assigned to their own truck.
        if user["role"]=="Team Leader" and collection["truck_id"]!=user["truck_id"]:
            raise PermissionDenied("You can only update collections assigned to your truck.")
        db.save("collections",{"id": collection_id, "status": new_status})

    return M5_Collection_Sched.get_collection(db, collection_id)
