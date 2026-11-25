

from . import M2_Security as security 
from .errors import NotFound, PermissionDenied , AuthError, ValidationError


Valid_Status=("Completed", "Missed", "Canceled")
ACTION="M7_Collection_Status"

def get_collection(db,user):

    security.require(user, ACTION)

    return db.find("collection_status")

#SR-5.0.1 and SR-5.0.2

def update_status(db, user, collection_id, new_status):

    security.require(user, ACTION)



    if collection_id is None or collection_id=="":
        raise ValidationError("Please select a collection")

    if new_status not in Valid_Status:
        raise ValidationError("Invalid status.")


    with db.transaction():

        collection=db.get("collection_status", collection_id)

        if collection is None:
            raise NotFound("Collection not found.")

        db.save("collections", {
            "id": collection_id,
            "status": new_status
        })

        updated=db.get("collection_status", collection_id)

    return updated


def get_collection(db,user, collection_id):

    security.require(user, ACTION)

    collection=db.get("collection_status", collection_id)

    if collection is None:
        raise NotFound("Collection not found.")

    return collection


         