import hashlib
import hmac
import os
from .errors import AuthError, PermissionDenied #makes the custom exceptions that were in error.py avialable for use where nessary here

ROLES=("Owner", "Admin", "Team Leader", "Sidemen") #Roles within the system
PERMISSIONS={"M6_Truck_Assignment": {"Admin"},"documents": {"Owner", "Admin"},"schedules":{"Owner", "Admin"},
             "view_collections": {"Owner", "Admin", "Team Leader", "Sidemen"}, "M3_Parts_Order": {"Owner", "Admin"}}#content inside tupe would take the format {"PartOrder": {Admin},} PartOrder being the name of the module for F-01
#decide which role can perform whcih action
HASHSTRENGHT= 200_000 #used to detemine # of time hashing is repaeted

#make a normal passwrd into a secure hash before saving it to the databse
def hash_pswrd(pwrd: str)-> str: #incase your wondering what the -->str is, it just mean it's expected to return a string
   r_salt=os.urandom(16)#gens a random 16byt salt, used to make a passwrd unique
   pwd_hash= hashlib.pbkdf2_hmac("sha256",pwrd.encode(), r_salt, HASHSTRENGHT) #gentrerates a passwrd hash from a pswrd bytes
   return f"{r_salt.hex()}${pwd_hash.hex()}" #converts to hexadecimal with $ inbetween
  

def is_pswrd(password: str, stored: str)->bool: ##expected return type booolean
  try:
    r_salt_hex, pwd_hash_hex= stored.split("$")#split the salt and pswrd from a combination saved in the database
    pwd_hash= hashlib.pbkdf2_hmac("sha256",password.encode(), bytes.fromhex(r_salt_hex), HASHSTRENGHT) 
  except ValueError:
    return False
  return hmac.compare_digest(pwd_hash.hex(),pwd_hash_hex) #compares the store hash with the newly generate done

def login(db, username: str, passwrd: str)->dict: #expected return type dictionary
  rows=db.find("users", username=(username or "").strip()) #db is the database con and the others are just as stated
  if not rows or not is_pswrd(passwrd or "", rows[0]["password_hash"]): #check wheather the user exist and wether the passwrd match any stored in password_hash
     raise AuthError("Password or Username is invalid")
  user=rows[0]
  return{"id": user["id"], "username": user["username"], "full_name": user["full_name"],
        "role": user["role"], "truck_id": user["truck_id"]}
  

def can(role: str, action: str)->bool: #just a permission check to ensure that a role can do an acction
  return role in PERMISSIONS.get(action,set())
  #can("Owner", "backup") would return True

def require(user: dict, action: str)->None: #this will likely just raise an exception for Permission Deny
  if not user or not can(user["role"], action):
    raise PermissionDenied("You are not allowed to do this")
  #require(user, "contracts") return Your role is not allowed to do this. if user lack the sufficent permission.
