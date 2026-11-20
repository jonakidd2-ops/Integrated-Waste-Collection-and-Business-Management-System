import hashlib
import hmac
import os
from .errors import AuthError, PermissionDenied #makes the custom exceptions that were in error.py avialable for use where nessary here

ROLES=("Owner", "Admin", "Team Leader", "Sidemen") #Roles within the system
PERMISSION={}#content inside tupe would take the format {"PartOrder": {Admin},} PartOrder being the name of the module for F-01


def hash_pswrd(password: str)-> str: #incase your wondering what the -->str is, it just mean it's expected to return a string


def is_pswrd(password: str, store: str)->bool: ##expected return type booolean

def login(db, username: str, password: str)->dict: #expected return type dictionary

def can(role: str, action: str)->bool:

def require(user: dict, action: str)-->None #this will likely just raise an exception for Permission Deny
