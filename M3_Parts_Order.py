#Part ordering module

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime

from random import randint

#order_state is a dictionary that keeps track of the current order comprising
#a counter and a dictionary with the parts currently in the pending order
def order_details(order_state):
    items = order_state["items"]
    order_lines = [
        f"{part_id} {part['part']} x{part['number']}"
        for part_id, part in items.items()
    ]
    total = sum(part["price"] * part["number"] for part in items.values())
    return order_lines, total

#Dummy supplier email: harrycolesparts@gmail.com
#Dummy supplier password: nicep@rts
def send_order(order_state, supplier_email):
    if not order_state["items"]:
        return False
    if not supplier_email:
        return False
    order_lines, total = order_details(order_state)

    #Creates email
    #Sender email is a burner email used for demonstrative purposes and does not
    #contain any personal information, password is donfran18. 2-step authentication
    #must be enabled however for emails to be sent
    order_ID = randint(1000, 9999)
    msg = MIMEMultipart()
    msg['From'] = "dfenterprise15@gmail.com"
    msg['To'] = supplier_email
    msg['Subject'] = "Part Order from DonFran Enterprise - DF" + str(order_ID)
    dt = datetime.now()

    body = (
        "\t\t\t\tPART ORDER\n"
        "------------------------------------------------------------------------------\n"
        + "\n".join(order_lines)
        + "\n------------------------------------------------------------------------------\n"
        f"DonFran Enterprise\t\t{dt.replace(second=0, microsecond=0)}"
    )
    msg.attach(MIMEText(body, 'plain'))

    #Sends email using provided gmail address through smtp
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    #The password applied must be an app password for the email to be sent, not the account password.
    server.login("dfenterprise15@gmail.com", "hvvswirxnptruslz")
    try:
        server.sendmail("dfenterprise15@gmail.com", supplier_email, msg.as_string())
    except Exception:
        server.quit()
        return False
    finally:
        server.quit()
    with open("sent_orders.txt", "a") as f:
        f.write(f"Order-DF{order_ID} sent to {supplier_email} at {dt.replace(second=0, microsecond=0)}\n")
        f.write("\n".join(order_lines) + "\n\n")
    return True
