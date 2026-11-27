#M3 Parts Orders (F-01): choose parts, see type/quantity/cost, confirm, email to the supplier.
#DONFRAN_SMTP_HOST, DONFRAN_SMTP_PORT (587), DONFRAN_SMTP_USER, DONFRAN_SMTP_PASSWORD, DONFRAN_SMTP_FROM
#With no DONFRAN_SMTP_HOST set the email is saved as an .eml file instead of being sent.

import os
import smtplib
from datetime import date
from email.message import EmailMessage

from . import M2_Security
from .errors import NotFound, ServiceError, ValidationError

PERMISSION = "M3_Parts_Order"   


def list_parts(db):
    return db.query(
        "SELECT p.id, p.name, p.part_type, p.unit_cost, p.supplier_id, s.name AS supplier "
        "FROM parts p LEFT JOIN suppliers s ON s.id = p.supplier_id ORDER BY p.part_type, p.name")


def price_lines(db, lines):
    #list of (part_id, quantity). Returns rows showing type, quantity and cost (SR-1.3)
    if not lines:
        raise ValidationError("Add at least one part to the order.")
    out = []
    for part_id, qty in lines:
        part = db.get("parts", part_id)
        if part is None:
            raise NotFound("That part no longer exists.")
        if not isinstance(qty, int) or qty <= 0:
            raise ValidationError("Quantity must be a whole number greater than zero.")
        out.append({"part_id": part_id, "name": part["name"], "part_type": part["part_type"],
                    "quantity": qty, "unit_cost": part["unit_cost"],
                    "cost": round(qty * part["unit_cost"], 2), "supplier_id": part["supplier_id"]})
    return out


def create_order(db, user, lines):
    #Save a new order (status Draft) from the chosen parts. Returns the order id.
    M2_Security.require(user, PERMISSION)
    priced = price_lines(db, lines)
    total = round(sum(r["cost"] for r in priced), 2)
    supplier_id = priced[0]["supplier_id"]
    with db.transaction():
        order_id = db.save("parts_orders", {"order_date": date.today().isoformat(), "status": "Draft",
                                            "total": total, "supplier_id": supplier_id, "created_by": user["id"]})
        for r in priced:
            db.save("order_lines", {"order_id": order_id, "part_id": r["part_id"],
                                    "quantity": r["quantity"], "unit_cost": r["unit_cost"]})
    return order_id


def get_order(db, order_id):
    order = db.get("parts_orders", order_id)
    if order is None:
        raise NotFound("Order not found.")
    order["lines"] = db.query(
        "SELECT l.quantity, l.unit_cost, ROUND(l.quantity * l.unit_cost, 2) AS cost, p.name, p.part_type "
        "FROM order_lines l JOIN parts p ON p.id = l.part_id WHERE l.order_id = ?", (order_id,))
    order["supplier"] = db.get("suppliers", order["supplier_id"]) if order["supplier_id"] else None
    return order


def list_orders(db, user):
    M2_Security.require(user, PERMISSION)
    return db.query("SELECT id, order_date, status, total FROM parts_orders ORDER BY id DESC")

def confirm_order(db, user, order_id):
    M2_Security.require(user, PERMISSION)
    order = get_order(db, order_id)
    if order["status"] != "Draft":
        raise ValidationError("Only a draft order can be confirmed.")
    db.save("parts_orders", {"id": order_id, "status": "Confirmed"})

def _order_text(order):
    sup = order["supplier"]
    rows = [f"DonFran Enterprise - Replacement Parts Order #{order['id']:04d}",
            f"Date: {order['order_date']}", f"Supplier: {sup['name']}", ""]
    rows += [f"{l['name']:<28}{l['part_type']:<14}x{l['quantity']:<4}{l['cost']:>10.2f}" for l in order["lines"]]
    rows += ["", f"TOTAL: {order['total']:.2f}"]
    return "\n".join(rows) + "\n"

def build_email(order, sender):
    msg=EmailMessage()
    msg["From"]=sender
    msg["To"] = order["supplier"]["contact"]
    msg["Subject"] = f"DonFran Enterprise - Parts Order #{order['id']:04d}"
    text=_order_text(order)
    msg.set_content("Please find our parts order below and attached.\n\n" + text)
    msg.add_attachment(text.encode("utf-8"), maintype="text", subtype="plain",
                       filename=f"order_{order['id']:04d}.txt")
    return msg

def send_order(db, user, order_id, out_dir="orders"):
    #Email the confirmed order to the supplier (SR-1.4).

    #If SMTP is configured (DONFRAN_SMTP_HOST, _PORT, _USER, _PASSWORD, _FROM) the email is
    #sent, otherwise the email is saved as an .eml file in out_dir so it
    #can be opened and shown. The order is only marked Sent after delivery or saving succeeds.
    
    M2_Security.require(user, PERMISSION) #the SMTP isn't configured to actually send an email
    order=get_order(db, order_id)
    if order["status"]!="Confirmed":
        raise ValidationError("Confirm the order before sending it.")
    if not order["supplier"] or not (order["supplier"].get("contact") or "").strip():
        raise ValidationError("This supplier has no email address on file.")
    host=os.environ.get("DONFRAN_SMTP_HOST")
    sender=os.environ.get("DONFRAN_SMTP_FROM", "donfran@gmail.blahblah")
    msg=build_email(order, sender)
    result={"to": msg["To"], "sent": False, "path": None}
    if host:
        try:
            with smtplib.SMTP(host, int(os.environ.get("DONFRAN_SMTP_PORT", "587")), timeout=20) as smtp:
                smtp.starttls()
                if os.environ.get("DONFRAN_SMTP_USER"):
                    smtp.login(os.environ["DONFRAN_SMTP_USER"], os.environ.get("DONFRAN_SMTP_PASSWORD", ""))
                smtp.send_message(msg)
        except (OSError, smtplib.SMTPException):
            raise ServiceError("The email could not be sent. The order is still confirmed; try again.")
        result["sent"]=True
    else: #this part was written for demonstaring in the demo
        os.makedirs(out_dir, exist_ok=True)
        result["path"]=os.path.join(out_dir, f"order_{order_id:04d}.eml")
        with open(result["path"], "wb") as f:
            f.write(bytes(msg))
    db.save("parts_orders", {"id": order_id, "status": "Sent"})
    return result
