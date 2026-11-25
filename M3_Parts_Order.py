#Part ordering module

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import *

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

def refresh(order_state, pending):
    order_lines, total = order_details(order_state)
    pending.config(
        text=f"Pending Order:\n" + "\n".join(order_lines) + f"\nTotal Cost: {total}"
    )

#Adds a part to the order, checking for valid input and updating the order state
def add(name, quan, parts_dict, order_state, pending):
    try:
        quan = int(quan)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a whole number.")
        return
    if name not in parts_dict or not 1 <= quan <= 10:
        messagebox.showerror("Error", "Select a valid part and enter a quantity from 1 to 10.")
        return
    order_state["counter"] += 1
    part_id = order_state["counter"]
    order_state["items"][part_id] = {
        "part": name,
        "number": quan,
        "price": parts_dict[name]["Cost"],
    }
    refresh(order_state, pending)

def remove(order_state, pending):
    items = order_state["items"]
    if not items:
        messagebox.showerror("Error", "No parts to remove.")
        return
    part_id = max(items)
    del items[part_id]
    order_state["counter"] -= 1
    refresh(order_state, pending)

def send_order(order_state, supplier_email):
    if not order_state["items"]:
        messagebox.showerror("Error", "Add at least one part to the pending order.")
        return
    if not supplier_email:
        messagebox.showerror("Error", "Supplier email is required.")
        return
    order_lines, total = order_details(order_state)

    #Creates email
    #Sender email is a burner email used for demonstrative purposes and does not
    #contain any personal information, password is donfran18
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
        messagebox.showerror("Error", "Could not send email, check supplier address.")
    else:
        messagebox.showinfo("Success", "Order sent successfully!")
    finally:
        server.quit()
    with open("sent_orders.txt", "a") as f:
        f.write(f"Order-DF{order_ID} sent to {supplier_email} at {dt.replace(second=0, microsecond=0)}\n")
        f.write("\n".join(order_lines) + "\n\n")

def part_window(window):
    window.withdraw()
    parts_dict = {
        "Brake Pads": {"Cost": 7000},
        "Oil Filter": {"Cost": 12000},
        "Air Filter": {"Cost": 5150},
        "Tire": {"Cost": 8000},
        "Headlamp": {"Cost": 6500},
        "Windshield Wiper": {"Cost": 2000},
        "Steering Wheel": {"Cost": 4000}
    }

    def back_Btn():
        window.deiconify()  #Show the main window again
        part_window.destroy()

    #Creates the part selection window
    part_window = tk.Toplevel(window, bg="lightblue")
    part_window.title("Parts Ordering System")
    part_window.geometry("600x350")

    #Makes the details of each part appear when selected from the Combobox
    def choice(event):
        details = tk.Label(part_window, text=f"Name: {event.widget.get()}\nCost: \
{parts_dict[event.widget.get()]['Cost']}\n\
*These are speculative prices and may not reflect those\n \
on the invoice sent by the supplier", justify="left")
        details.grid(row=0, column=2, rowspan=2, columnspan=2, pady=10)
    #Labels and widgets to compose order
    tk.Label(part_window, text="Part Name:").grid(row=0, column=0, padx=10, pady=10)
    p_name = ttk.Combobox(part_window)
    p_name['values'] = tuple(parts_dict.keys())
    p_name.current()
    p_name.grid(row=0, column=1, padx=10, pady=10)
    p_name.bind("<<ComboboxSelected>>", choice)

    tk.Label(part_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=10)
    p_quantity = tk.Spinbox(part_window, from_=1, to=10)
    p_quantity.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(part_window, text="Supplier Email:").grid(row=2, column=0, padx=10, pady=10)
    #Dummy supplier email: harrycolesparts@gmail.com
    #Dummy supplier password: nicep@rts
    default = tk.StringVar(value="harrycolesparts@gmail.com")
    supp_email_E = tk.Entry(part_window, textvariable=default)
    supp_email_E.grid(row=2, column=1, padx=10, pady=10)

    order_state = {"counter": 0, "items": {}}
    pending = tk.Label(part_window, text="Pending Order:\nTotal Cost: 0")
    pending.grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(part_window, text="Send Order", width = 10,
              command=lambda: send_order(order_state, supp_email_E.get()),
    ).grid(row=5, column=0, pady=10)
    tk.Button(part_window, text="Add Part", width = 10,
        command=lambda: add(
            p_name.get(), p_quantity.get(), parts_dict, order_state, pending
        ),
    ).grid(row=4, column=0, pady=10)
    tk.Button(part_window, text="Remove Part", width = 10,
        command=lambda: remove(order_state, pending),
    ).grid(row=4, column=1, pady=10)
    tk.Button(part_window, text="Back", width = 10, command=back_Btn).grid(row=5, column=1, pady=10)

#For testing purposes, main will be called by a separate program in the finished software
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("300x200")

    tk.Button(root, text="Order Parts", command=lambda: part_window(root)).pack(pady=20)

    root.mainloop()