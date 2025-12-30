# billing_cli.py

PRODUCTS = {
    "890101": {"name": "Rice", "price": 50.0},
    "890102": {"name": "Oil", "price": 120.0},
    "890103": {"name": "Sugar", "price": 40.0},
}

GST_RATE = 0.05  # 5% GST

cart = []

def add_item(barcode):
    if barcode not in PRODUCTS:
        print("❌ Product not found!")
        return

    product = PRODUCTS[barcode]

    # Check if item already in cart
    for item in cart:
        if item["barcode"] == barcode:
            item["qty"] += 1
            item["total"] = item["qty"] * item["price"]
            print(f"✔ {product['name']} quantity updated")
            return

    cart.append({
        "barcode": barcode,
        "name": product["name"],
        "price": product["price"],
        "qty": 1,
        "total": product["price"]
    })
    print(f"✔ {product['name']} added to cart")

def calculate_totals():
    subtotal = sum(item["total"] for item in cart)
    gst = subtotal * GST_RATE
    grand_total = subtotal + gst
    return subtotal, gst, grand_total

def print_bill():
    print("\n========== ABC STORE ==========")
    print("Item        Qty   Price   Total")
    print("--------------------------------")
    for item in cart:
        print(f"{item['name']:<10} {item['qty']:<5} {item['price']:<7} {item['total']:.2f}")
    print("--------------------------------")

    subtotal, gst, grand_total = calculate_totals()
    print(f"Subtotal:        {subtotal:.2f}")
    print(f"GST (5%):        {gst:.2f}")
    print(f"Grand Total:     {grand_total:.2f}")
    print("================================")
    print("Thank You! Visit Again 🙏\n")

def main():
    print("🧾 SIMPLE BILLING SYSTEM (CLI)")
    print("Scan barcode or type 'print' to finish, 'exit' to quit\n")

    while True:
        barcode = input("Scan Barcode: ").strip()

        if barcode.lower() == "exit":
            print("Exiting billing system...")
            break

        elif barcode.lower() == "print":
            if not cart:
                print("⚠ Cart is empty!")
            else:
                print_bill()
                cart.clear()
                print("🆕 New bill started\n")

        else:
            add_item(barcode)

if __name__ == "__main__":
    main()
