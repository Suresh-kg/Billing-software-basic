import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "billing.db"
GST_RATE = 0.05

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_date TEXT,
        subtotal REAL,
        gst REAL,
        total REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        product_name TEXT,
        price REAL,
        quantity INTEGER,
        total REAL
    )
    """)

    # Sample products
    products = [
        ("101", "Rice", 50),
        ("102", "Oil", 120),
        ("103", "Sugar", 40),
        ("104", "Milk", 30)
    ]

    cur.executemany(
        "INSERT OR IGNORE INTO products VALUES (?, ?, ?)",
        products
    )

    conn.commit()
    conn.close()

# ---------------- BILLING LOGIC ----------------
cart = []

def get_product(barcode):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, price FROM products WHERE barcode=?", (barcode,))
    row = cur.fetchone()
    conn.close()
    return row

def add_item():
    barcode = barcode_entry.get().strip()
    if not barcode:
        return

    product = get_product(barcode)
    if not product:
        messagebox.showerror("Error", "Product not found")
        return

    name, price = product

    for item in cart:
        if item["barcode"] == barcode:
            item["qty"] += 1
            item["total"] = item["qty"] * item["price"]
            refresh_table()
            calculate_total()
            barcode_entry.delete(0, END)
            return

    cart.append({
        "barcode": barcode,
        "name": name,
        "price": price,
        "qty": 1,
        "total": price
    })

    refresh_table()
    calculate_total()
    barcode_entry.delete(0, END)

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    for item in cart:
        tree.insert("", END, values=(
            item["name"],
            item["qty"],
            item["price"],
            item["total"]
        ))

def calculate_total():
    subtotal = sum(i["total"] for i in cart)
    gst = subtotal * GST_RATE
    total = subtotal + gst

    subtotal_var.set(f"{subtotal:.2f}")
    gst_var.set(f"{gst:.2f}")
    total_var.set(f"{total:.2f}")

def save_and_show_bill():
    if not cart:
        messagebox.showwarning("Warning", "Cart is empty")
        return

    subtotal = float(subtotal_var.get())
    gst = float(gst_var.get())
    total = float(total_var.get())

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    bill_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO bills (bill_date, subtotal, gst, total) VALUES (?, ?, ?, ?)",
        (bill_date, subtotal, gst, total)
    )

    bill_id = cur.lastrowid

    for item in cart:
        cur.execute("""
        INSERT INTO bill_items
        (bill_id, product_name, price, quantity, total)
        VALUES (?, ?, ?, ?, ?)
        """, (bill_id, item["name"], item["price"], item["qty"], item["total"]))

    conn.commit()
    conn.close()

    show_bill(bill_id, bill_date, subtotal, gst, total)
    cart.clear()
    refresh_table()
    calculate_total()

def show_bill(bill_id, date, subtotal, gst, total):
    receipt.delete("1.0", END)

    receipt.insert(END, "        ABC STORE\n")
    receipt.insert(END, "------------------------------\n")

    for item in cart:
        receipt.insert(
            END,
            f"{item['name']}  {item['qty']} x {item['price']} = {item['total']}\n"
        )

    receipt.insert(END, "------------------------------\n")
    receipt.insert(END, f"Subtotal: {subtotal:.2f}\n")
    receipt.insert(END, f"GST (5%): {gst:.2f}\n")
    receipt.insert(END, f"TOTAL: {total:.2f}\n")
    receipt.insert(END, "------------------------------\n")
    receipt.insert(END, f"Bill No: {bill_id}\n")
    receipt.insert(END, f"Date: {date}\n")
    receipt.insert(END, "\nThank You! Visit Again 🙏")

# ---------------- GUI ----------------
init_db()

root = Tk()
root.title("Billing Software")
root.geometry("800x500")

# Barcode Input
Label(root, text="Barcode").place(x=20, y=20)
barcode_entry = Entry(root, width=20)
barcode_entry.place(x=80, y=20)
barcode_entry.focus()

Button(root, text="Add Item", command=add_item).place(x=220, y=17)

# Table
columns = ("Name", "Qty", "Price", "Total")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.place(x=20, y=60, width=400, height=250)

for col in columns:
    tree.heading(col, text=col)

# Totals
subtotal_var = StringVar(value="0.00")
gst_var = StringVar(value="0.00")
total_var = StringVar(value="0.00")

Label(root, text="Subtotal").place(x=20, y=330)
Label(root, textvariable=subtotal_var).place(x=100, y=330)

Label(root, text="GST").place(x=20, y=360)
Label(root, textvariable=gst_var).place(x=100, y=360)

Label(root, text="Total").place(x=20, y=390)
Label(root, textvariable=total_var).place(x=100, y=390)

Button(root, text="Print / Show Bill", width=20, command=save_and_show_bill)\
    .place(x=250, y=360)

# Receipt Area
receipt = Text(root, width=40, height=25)
receipt.place(x=450, y=20)

root.mainloop()
