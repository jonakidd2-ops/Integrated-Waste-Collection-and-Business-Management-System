#Parts ordering module
#GUI is already embedded into this program (albeit it's a placeholder at present), 
#but I imagine it'll be moved to a dedicated GUI handler once that's sorted to adhere 
#to the architecture design. After that the primary function will be send_order(). 
#TODO I plan on improving the layout for the email order soon.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import tkinter as tk
from tkinter import ttk
from tkinter import *

#TODO Makes the details of each part appear when selected from the Combobox
def choice(event):
    pass

def part_window(window):
    #parts_file = open("parts_list.txt", "r")  #Source file to populate the order screen
    #while True:
    #    if not parts_file:
    #        break
    #Creates the part selection window
    part_window = tk.Toplevel(window, bg="lightblue")
    part_window.title("Parts Ordering System")
    part_window.geometry("800x400")

    #Labels and widgets to compose order
    tk.Label(part_window, text="Part Name:").grid(row=0, column=0, padx=10, pady=10)
    p_name = ttk.Combobox(part_window)
    #TODO Temporary values, will be populated using names from parts list
    p_name['values'] = ("Brake Pads", "Oil Filter", "Air Filter", "Tire", "Headlamp")
    p_name.current(0)
    p_name.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(part_window, text="Quantity:").grid(row=1, column=0, padx=10, pady=10)
    p_quantity = tk.Spinbox(part_window, from_=1, to=10)
    p_quantity.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(part_window, text="Supplier Email:").grid(row=2, column=0, padx=10, pady=10)
    #Dummy supplier email: harrycolesparts@gmail.com
    #Dummy supplier password: nicep@rts
    default = tk.StringVar(value="harrycolesparts@gmail.com")
    supp_email_E = tk.Entry(part_window, textvariable=default, state="readonly")
    supp_email_E.grid(row=2, column=1, padx=10, pady=10)

    #Sends the order to a specified supplier via gmail.
    #TODO Will be called with name, quantity and supplier email as parameters in the future.
    def send_order():
        part_name = p_name.get()
        quantity = p_quantity.get()
        supplier_email = supp_email_E.get()

        if not part_name or not quantity or not supplier_email:
            tk.messagebox.showerror("Error", "All fields are required.")
            return

        #Creates email
        #Sender email is a burner email used for demonstrative purposes and does not
        #contain any personal information, password is donfran18
        msg = MIMEMultipart()
        msg['From'] = "dfenterprise15@gmail.com"
        msg['To'] = supplier_email
        msg['Subject'] = f"Part Order: {part_name}"

        body = f"Part Name: {part_name}\nQuantity: {quantity}"
        msg.attach(MIMEText(body, 'plain'))

        #Sends email using provided gmail address through smtp
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        #The password applied must be an app password for the email to be sent, not the account password.
        server.login("dfenterprise15@gmail.com", "hvvswirxnptruslz")
        text = msg.as_string()
        server.sendmail("dfenterprise15@gmail.com", supplier_email, text)
        server.quit()

    #Creates the button to send the order
    tk.Button(part_window, text="Send Order", command=send_order).grid(row=3, column=0, columnspan=2, pady=10)

#For testing purposes, main will be called by a separate program in the finished software
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("300x200")

    tk.Button(root, text="Order Parts", command=lambda: part_window(root)).pack(pady=20)

    root.mainloop()