# Integrated-Waste-Collection-and-Business-Management-System
DonFran Enterprise|COMP2140 Introduction to Software Engineering|Group THUR_5-7_G02

This is a desktop application to help DonFran Enterprise run its waste collection business. (It follows our SDS and SRS)
It replaces paper records with one system for parts orders, documents, collection
schedules, truck assignments, collection status and customer contracts.

## Features
| ID | Feature | Module | Who can use it |
|----|---------|--------|----------------|
| F-01 | Parts orders (sent to the supplier by email) | M3_Parts_Order | Admin |
| F-02 | Documents | M4_Document_Management | Owner, Admin |
| F-03 | Collection schedules | M5_Collection_Sched | Owner, Admin |
| F-04 | Truck assignment | M6_Truck_Assignment | Admin |
| F-05 | Collection status | M7_Collection_Status | Admin, Team Leader |
| F-06 | Contracts | M8_Contract_Management | Owner, Admin |

Login, roles and passwords are handled by M2_Security. All database access goes
through M9_Data_Access. The screens are in the `Ui` folder.

## Requirements
- Python 3.11 or newer
- Tkinter; which I believe is done automatically when you install python 
- The database here is SQLite; data access layer would need to be change to point to an actual database(relational) if this was put to real use

## How to run
1. Download or clone this repository and open a terminal in its folder.
2. to start app run: `python main.py`
3. To start again with a fresh dummy database run: `python main.py --reset`

The first run creates `donfran.db` and fills it with dummy data.

## Demo logins
The password for every user was set to (for convenience when testing) `1234`.

| Username | Role |
|----------|------|
| owner | Owner |
| admin | Admin |
| leader1, leader2 | Team Leader |
| side1, side2 | Sidemen |

the system is designed so that each role only sees the menu items it is allowed to use; it still enforces security requirements regardless tho

## Sending order emails
when the email settings is unconfigured a parts order is saved as an `.eml` file in the a folder called `orders`. 
in order to acutually send real emails, set these before running:

    set DONFRAN_SMTP_HOST=smtp.gmail.com
    set DONFRAN_SMTP_PORT=587
    set DONFRAN_SMTP_USER=youraddress@gmail.com
    set DONFRAN_SMTP_PASSWORD=yourapppassword
    set DONFRAN_SMTP_FROM=youraddress@gmail.com
please don't write passwords into the code lol, or commit it to the repository

## Project structure
    main.py                     starts the app
    M2_Security.py              login and role permissions
    M3_Parts_Order.py           F-01
    M4_Document_Management.py   F-02
    M5_Collection_Sched.py      F-03
    M6_Truck_Assignment.py      F-04
    M7_Collection_Status.py     F-05
    M8_Contract_Management.py   F-06
    M9_Data_Access.py           this is the module that interacts with the database; everything else do so through it
    seed.py                     just the dummy users and data
    backup.py                   database backup #function written but not yet implemented in the system
    errors.py                   shared error types
    Ui folder                   contains all the screens for each module

