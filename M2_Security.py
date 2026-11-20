import hashlib
import hmac
import os

ROLES=("Owner", "Admin", "Team Leader", "Sidemen") #Roles within the system
PERMISSION={}#content inside tupe would take the format {"PartOrder": {Admin},} PartOrder being the name of the module for F-01


def hash_pswrd(password: str)-> str:
