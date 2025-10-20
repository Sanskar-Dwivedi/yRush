# Yrush_v3.8.py
"""
Yrush v3.8 – Enhanced Edition
- Added Pickup option alongside Delivery for both Canteen & Suvidha
- Refresh buttons in Canteen/Suvidha Orders tabs
- Dropdown for Suvidha categories (Books, Manuals, Stationery, Lab Equipment, Others)
- Order status management (Pending -> Preparing -> Ready -> Completed)
- Enhanced UI with status badges, better spacing, and visual improvements
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.font import Font
import json, os, uuid
from datetime import datetime

# -------------------- Config / Theme --------------------
DATA_FILE = "yrush_data.json"
OWNER_PW = "admin123"
DELIVERY_FEE = 5.0

THEME = {
    "bg": "#F9FAFB",
    "card": "#FFFFFF",
    "accent": "#2563EB",
    "success": "#10B981",
    "warn": "#F59E0B",
    "danger": "#EF4444",
    "text": "#111827",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "font": "Segoe UI"
}

SUVIDHA_CATEGORIES = ["Books", "Manuals", "Stationery", "Lab Equipment", "Others"]

# -------------------- Data Store --------------------
class DataStore:
    def __init__(self, path):
        self.path = path
        self.db = {"canteen_items": [], "suvidha_items": [], "orders": []}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k in ("canteen_items", "suvidha_items", "orders"):
                        self.db[k] = data.get(k, [])
            else:
                self.db["canteen_items"] = [
                    {"name": "Veg Burger", "price": 40.0, "available": True},
                    {"name": "Tea", "price": 10.0, "available": True},
                    {"name": "Samosa", "price": 15.0, "available": True},
                    {"name": "Coffee", "price": 12.0, "available": True},
                ]
                self.db["suvidha_items"] = [
                    {"name": "Notebook A4", "price": 60.0, "stock": 12, "category": "Stationery"},
                    {"name": "Blue Pen", "price": 8.0, "stock": 50, "category": "Stationery"},
                    {"name": "Physics Manual", "price": 150.0, "stock": 8, "category": "Manuals"},
                    {"name": "Graph Paper", "price": 30.0, "stock": 25, "category": "Stationery"},
                ]
                self._save()
        except Exception as e:
            print("Data load error:", e)

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Data save error:", e)

    def save(self):
        self._save()

    def __getitem__(self, key):
        return self.db.get(key, [])

    def append_order(self, order):
        self.db["orders"].append(order)
        self._save()
    
    def update_order_status(self, order_id, new_status):
        for order in self.db["orders"]:
            if order.get("id") == order_id:
                order["status"] = new_status
                self._save()
                return True
        return False

# -------------------- Utils --------------------
def center_window(win, w=520, h=360):
    win.update_idletasks()
    ws, hs = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = max(0, (ws - w)//2), max(0, (hs - h)//2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def safe_to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def show_toast(root, msg, duration=1800, bg=THEME["accent"]):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    frm = tk.Frame(toast, bg=bg, bd=1, relief="solid")
    frm.pack(fill="both", expand=True)
    tk.Label(frm, text=msg, bg=bg, fg="white", font=(THEME["font"], 10, "bold")).pack(padx=16, pady=10)
    root.update_idletasks()
    x = root.winfo_rootx() + root.winfo_width() - 380
    y = root.winfo_rooty() + root.winfo_height() - 100
    toast.geometry(f"+{x}+{y}")
    toast.after(duration, toast.destroy)

def create_badge(parent, text, bg_color):
    badge = tk.Label(parent, text=text, bg=bg_color, fg="white", 
                    font=(THEME["font"], 9, "bold"), padx=8, pady=2)
    return badge

# -------------------- Main App --------------------
class YrushApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yrush v3.8 – Campus Services")
        self.root.configure(bg=THEME["bg"])
        self.data = DataStore(DATA_FILE)
        self._fonts()
        self._build_main_ui()

    def _fonts(self):
        self.font_h1 = Font(family=THEME["font"], size=26, weight="bold")
        self.font_h2 = Font(family=THEME["font"], size=16, weight="bold")
        self.font_b  = Font(family=THEME["font"], size=11)

    def _build_main_ui(self):
        # Header with shadow effect
        header = tk.Frame(self.root, bg=THEME["card"], bd=0, relief="flat")
        header.pack(fill="x", padx=0, pady=0)
        
        inner_header = tk.Frame(header, bg=THEME["card"])
        inner_header.pack(fill="x", padx=20, pady=16)
        
        title_frame = tk.Frame(inner_header, bg=THEME["card"])
        title_frame.pack(side="left")
        tk.Label(title_frame, text="🎓 Yrush", fg=THEME["accent"], bg=THEME["card"], 
                font=self.font_h1).pack(side="left")
        tk.Label(title_frame, text="Campus Services Hub", fg=THEME["muted"], bg=THEME["card"], 
                font=(THEME["font"], 10)).pack(side="left", padx=12)
        
        tk.Button(inner_header, text="🔐 Owner Portal", bg=THEME["accent"], fg="white", 
                 bd=0, font=self.font_b, padx=16, pady=8, cursor="hand2",
                 command=self._owner_login).pack(side="right")

        # Shadow line
        tk.Frame(self.root, bg=THEME["border"], height=1).pack(fill="x")

        # Main body
        body = tk.Frame(self.root, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=40, pady=40)

        # Welcome message
        tk.Label(body, text="What would you like to order today?", 
                bg=THEME["bg"], fg=THEME["text"], 
                font=(THEME["font"], 14)).pack(pady=(0, 30))

        # Service cards
        services_frame = tk.Frame(body, bg=THEME["bg"])
        services_frame.pack(fill="both", expand=True)

        # Canteen card
        can_card = tk.Frame(services_frame, bg=THEME["card"], bd=1, relief="solid", 
                           highlightbackground=THEME["border"], highlightthickness=1)
        can_card.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(can_card, text="🍽️", bg=THEME["card"], font=(THEME["font"], 48)).pack(pady=(20, 10))
        tk.Label(can_card, text="Canteen", bg=THEME["card"], fg=THEME["text"], 
                font=self.font_h2).pack()
        tk.Label(can_card, text="Order delicious food\nPickup or Delivery available", 
                bg=THEME["card"], fg=THEME["muted"], 
                font=(THEME["font"], 9), justify="center").pack(pady=10)
        tk.Button(can_card, text="Open Canteen →", bg=THEME["accent"], fg="white", 
                 bd=0, font=self.font_b, padx=20, pady=10, cursor="hand2",
                 command=self._open_canteen).pack(pady=(10, 20))

        # Suvidha card
        suv_card = tk.Frame(services_frame, bg=THEME["card"], bd=1, relief="solid",
                           highlightbackground=THEME["border"], highlightthickness=1)
        suv_card.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(suv_card, text="📚", bg=THEME["card"], font=(THEME["font"], 48)).pack(pady=(20, 10))
        tk.Label(suv_card, text="Suvidha Store", bg=THEME["card"], fg=THEME["text"], 
                font=self.font_h2).pack()
        tk.Label(suv_card, text="Books, stationery & more\nPickup or Delivery available", 
                bg=THEME["card"], fg=THEME["muted"], 
                font=(THEME["font"], 9), justify="center").pack(pady=10)
        tk.Button(suv_card, text="Open Suvidha →", bg=THEME["accent"], fg="white", 
                 bd=0, font=self.font_b, padx=20, pady=10, cursor="hand2",
                 command=self._open_suvidha).pack(pady=(10, 20))

    def _owner_login(self):
        pw = simpledialog.askstring("Owner Login", "Enter password:", show="*")
        if pw == OWNER_PW:
            OwnerWindow(self)
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    def _open_canteen(self):
        try:
            CanteenWindow(self)
        except Exception as e:
            messagebox.showerror("Error", f"Canteen failed: {e}")

    def _open_suvidha(self):
        try:
            SuvidhaWindow(self)
        except Exception as e:
            messagebox.showerror("Error", f"Suvidha failed: {e}")

# -------------------- Canteen --------------------
class CanteenWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Canteen – Yrush")
        self.win.configure(bg=THEME["bg"])
        center_window(self.win, 750, 580)

        # Header
        header = tk.Frame(self.win, bg=THEME["card"])
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="🍽️ Canteen Menu", bg=THEME["card"], fg=THEME["text"], 
                font=app.font_h2).pack(side="left", padx=20, pady=16)
        tk.Frame(self.win, bg=THEME["border"], height=1).pack(fill="x")

        self.cart = []
        
        # Scrollable list
        canvas_frame = tk.Frame(self.win, bg=THEME["bg"])
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=12)
        
        canvas = tk.Canvas(canvas_frame, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        list_fr = tk.Frame(canvas, bg=THEME["bg"])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=list_fr, anchor="nw")
        
        for it in app.data["canteen_items"]:
            row = tk.Frame(list_fr, bg=THEME["card"], bd=1, relief="solid")
            row.pack(fill="x", pady=6, ipady=8, ipadx=12)
            
            tk.Label(row, text=it.get("name",""), bg=THEME["card"], fg=THEME["text"], 
                    font=(THEME["font"], 11, "bold")).pack(side="left", padx=8)
            tk.Label(row, text=f"₹{it.get('price',0)}", bg=THEME["card"], 
                    fg=THEME["accent"], font=(THEME["font"], 11, "bold")).pack(side="left", padx=12)
            
            if it.get("available", True):
                create_badge(row, "Available", THEME["success"]).pack(side="left", padx=8)
                tk.Button(row, text="+ Add to Cart", bg=THEME["accent"], fg="white", 
                         bd=0, cursor="hand2", padx=12, pady=4,
                         command=lambda i=it:self._add(i)).pack(side="right", padx=8)
            else:
                create_badge(row, "Unavailable", THEME["muted"]).pack(side="left", padx=8)

        list_fr.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Cart footer
        tk.Frame(self.win, bg=THEME["border"], height=1).pack(fill="x")
        cart_fr = tk.Frame(self.win, bg=THEME["card"])
        cart_fr.pack(fill="x", padx=0, pady=0)
        
        inner_cart = tk.Frame(cart_fr, bg=THEME["card"])
        inner_cart.pack(fill="x", padx=20, pady=16)
        
        self.total_lbl = tk.Label(inner_cart, text="Total: ₹0.00", bg=THEME["card"], 
                                 fg=THEME["text"], font=(THEME["font"], 12, "bold"))
        self.total_lbl.pack(side="left")
        
        tk.Button(inner_cart, text="🛒 Place Order", bg=THEME["success"], fg="white", 
                 bd=0, font=app.font_b, padx=20, pady=10, cursor="hand2",
                 command=self._place_order).pack(side="right")

    def _add(self, item):
        self.cart.append(item)
        show_toast(self.app.root, f"✓ Added {item.get('name')}", bg=THEME["success"])
        self._update_total()

    def _update_total(self):
        total = sum(i.get("price",0) for i in self.cart)
        self.total_lbl.config(text=f"Cart Total: ₹{total:.2f} ({len(self.cart)} items)")

    def _place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add items to cart first")
            return
        self.win.destroy()  # Close the canteen window first
        OrderTypeDialog(self.app, self.cart, order_type="canteen")

# -------------------- Suvidha --------------------
class SuvidhaWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Suvidha – Yrush")
        self.win.configure(bg=THEME["bg"])
        center_window(self.win, 780, 600)

        # Header
        header = tk.Frame(self.win, bg=THEME["card"])
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="📚 Suvidha Store", bg=THEME["card"], fg=THEME["text"], 
                font=app.font_h2).pack(side="left", padx=20, pady=16)
        tk.Frame(self.win, bg=THEME["border"], height=1).pack(fill="x")

        self.cart = []
        
        # Scrollable list
        canvas_frame = tk.Frame(self.win, bg=THEME["bg"])
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=12)
        
        canvas = tk.Canvas(canvas_frame, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        list_fr = tk.Frame(canvas, bg=THEME["bg"])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=list_fr, anchor="nw")
        
        for it in app.data["suvidha_items"]:
            row = tk.Frame(list_fr, bg=THEME["card"], bd=1, relief="solid")
            row.pack(fill="x", pady=6, ipady=8, ipadx=12)
            
            left_section = tk.Frame(row, bg=THEME["card"])
            left_section.pack(side="left", fill="x", expand=True)
            
            tk.Label(left_section, text=it.get("name",""), bg=THEME["card"], 
                    fg=THEME["text"], font=(THEME["font"], 11, "bold")).pack(side="left", padx=8)
            tk.Label(left_section, text=f"₹{it.get('price',0)}", bg=THEME["card"], 
                    fg=THEME["accent"], font=(THEME["font"], 11, "bold")).pack(side="left", padx=12)
            
            stock = it.get("stock", 0)
            category = it.get("category", "Others")
            create_badge(left_section, category, THEME["warn"]).pack(side="left", padx=4)
            
            if stock > 0:
                create_badge(left_section, f"Stock: {stock}", THEME["success"]).pack(side="left", padx=4)
                tk.Button(row, text="+ Add to Cart", bg=THEME["accent"], fg="white", 
                         bd=0, cursor="hand2", padx=12, pady=4,
                         command=lambda i=it:self._add(i)).pack(side="right", padx=8)
            else:
                create_badge(left_section, "Out of Stock", THEME["danger"]).pack(side="left", padx=4)

        list_fr.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Cart footer
        tk.Frame(self.win, bg=THEME["border"], height=1).pack(fill="x")
        cart_fr = tk.Frame(self.win, bg=THEME["card"])
        cart_fr.pack(fill="x", padx=0, pady=0)
        
        inner_cart = tk.Frame(cart_fr, bg=THEME["card"])
        inner_cart.pack(fill="x", padx=20, pady=16)
        
        self.total_lbl = tk.Label(inner_cart, text="Total: ₹0.00", bg=THEME["card"], 
                                 fg=THEME["text"], font=(THEME["font"], 12, "bold"))
        self.total_lbl.pack(side="left")
        
        tk.Button(inner_cart, text="🛒 Place Order", bg=THEME["success"], fg="white", 
                 bd=0, font=app.font_b, padx=20, pady=10, cursor="hand2",
                 command=self._place_order).pack(side="right")

    def _add(self, item):
        if item.get("stock",0) <= 0:
            messagebox.showwarning("Out of Stock", "This item is currently unavailable")
            return
        self.cart.append(item)
        show_toast(self.app.root, f"✓ Added {item.get('name')}", bg=THEME["success"])
        self._update_total()

    def _update_total(self):
        total = sum(i.get("price",0) for i in self.cart)
        self.total_lbl.config(text=f"Cart Total: ₹{total:.2f} ({len(self.cart)} items)")

    def _place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Please add items to cart first")
            return
        self.win.destroy()  # Close the suvidha window first
        OrderTypeDialog(self.app, self.cart, order_type="suvidha")

# -------------------- Order Type Dialog (Pickup/Delivery) --------------------
class OrderTypeDialog:
    def __init__(self, app, cart, order_type="canteen"):
        self.app, self.cart, self.order_type = app, cart, order_type
        self.win = tk.Toplevel(app.root)
        self.win.title("Order Type")
        self.win.configure(bg=THEME["bg"])
        self.win.transient(app.root)
        self.win.grab_set()
        center_window(self.win, 620, 400)
        
        tk.Label(self.win, text="Choose Order Type", bg=THEME["bg"],
                 fg=THEME["text"], font=app.font_h2).pack(pady=20)
        
        # Container for cards (side by side)
        cards_container = tk.Frame(self.win, bg=THEME["bg"])
        cards_container.pack(fill="x", expand=True, padx=40, pady=20)
        
        # ---- Pickup Card ----
        pickup_card = tk.Frame(cards_container, bg=THEME["card"], bd=2, relief="solid",
                               highlightbackground=THEME["border"], highlightthickness=1)
        pickup_card.pack(side="left", fill="both", expand=True, padx=8)
        
        tk.Label(pickup_card, text="🏃 Pickup", bg=THEME["card"], fg=THEME["text"],
                 font=(THEME["font"], 14, "bold")).pack(pady=(20, 8))
        tk.Label(pickup_card, text="Collect from counter", bg=THEME["card"],
                 fg=THEME["muted"], font=(THEME["font"], 10)).pack()
        tk.Label(pickup_card, text="No extra charge", bg=THEME["card"],
                 fg=THEME["muted"], font=(THEME["font"], 10)).pack(pady=(0, 12))
        tk.Button(pickup_card, text="Select Pickup →", bg=THEME["accent"], fg="white",
                  bd=0, font=(THEME["font"], 11, "bold"), padx=20, pady=10,
                  cursor="hand2", command=self._pickup).pack(pady=(0, 20))
        

        
        # Delivery option
        delivery_card = tk.Frame(cards_container, bg=THEME["card"], bd=2, relief="solid", highlightbackground=THEME["border"], highlightthickness=1)
        delivery_card.pack(fill="both", expand=True, pady=10)
        
        tk.Label(delivery_card, text="🚚 Delivery", bg=THEME["card"], fg=THEME["text"], 
                font=(THEME["font"], 14, "bold")).pack(pady=(20, 8))
        tk.Label(delivery_card, text="Delivered to your class", 
                bg=THEME["card"], fg=THEME["muted"], 
                font=(THEME["font"], 10)).pack()
        tk.Label(delivery_card, text=f"+₹{DELIVERY_FEE} delivery fee", 
                bg=THEME["card"], fg=THEME["muted"], 
                font=(THEME["font"], 10)).pack(pady=(0, 12))
        tk.Button(delivery_card, text="Select Delivery →", bg=THEME["success"], fg="white", 
                 bd=0, font=(THEME["font"], 11, "bold"), padx=24, pady=12, cursor="hand2",
                 command=self._delivery).pack(pady=(0, 20))

    def _pickup(self):
        self.win.destroy()
        PaymentDialog(self.app, self.cart, self.order_type, delivery_type="pickup")

    def _delivery(self):
        self.win.destroy()
        PaymentDialog(self.app, self.cart, self.order_type, delivery_type="delivery")

# -------------------- Payment Dialog --------------------
class PaymentDialog:
    def __init__(self, app, cart, order_type="canteen", delivery_type="pickup"):
        self.app, self.cart, self.order_type = app, cart, order_type
        self.delivery_type = delivery_type
        self.win = tk.Toplevel(app.root)
        self.win.title("Payment Method")
        self.win.configure(bg=THEME["bg"])
        self.win.transient(app.root)
        self.win.grab_set()
        center_window(self.win, 450, 340)
        
        tk.Label(self.win, text="Choose Payment Method", bg=THEME["bg"], 
                fg=THEME["text"], font=app.font_h2).pack(pady=20)
        
        # Calculate total
        subtotal = sum(i.get("price",0) for i in cart)
        delivery_fee = DELIVERY_FEE if delivery_type == "delivery" else 0
        total = subtotal + delivery_fee
        
        # Show breakdown
        breakdown_frame = tk.Frame(self.win, bg=THEME["card"], bd=1, relief="solid")
        breakdown_frame.pack(fill="x", padx=40, pady=12)
        tk.Label(breakdown_frame, text=f"Subtotal: ₹{subtotal:.2f}", bg=THEME["card"], 
                fg=THEME["muted"], font=(THEME["font"], 9)).pack(anchor="w", padx=12, pady=2)
        if delivery_fee > 0:
            tk.Label(breakdown_frame, text=f"Delivery Fee: ₹{delivery_fee:.2f}", 
                    bg=THEME["card"], fg=THEME["muted"], 
                    font=(THEME["font"], 9)).pack(anchor="w", padx=12, pady=2)
        tk.Label(breakdown_frame, text=f"Total: ₹{total:.2f}", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 11, "bold")).pack(anchor="w", padx=12, pady=4)
        
        tk.Button(self.win, text="💳 UPI Payment (Scan QR)", bg=THEME["accent"], 
                 fg="white", bd=0, font=app.font_b, width=30, pady=10, cursor="hand2",
                 command=self._upi).pack(pady=8)
        tk.Button(self.win, text="💵 Cash Payment", bg=THEME["success"], fg="white", 
                 bd=0, font=app.font_b, width=30, pady=10, cursor="hand2",
                 command=self._cash).pack(pady=8)
        tk.Button(self.win, text="Cancel", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, font=app.font_b, cursor="hand2",
                 command=self.win.destroy).pack(pady=6)

    def _upi(self):
        UPIQRWindow(self.app, self.cart, self.order_type, self.delivery_type, parent=self.win)

    def _cash(self):
        self.win.destroy()
        if self.delivery_type == "delivery":
            DeliveryDetailsWindow(self.app, self.cart, self.order_type, "Cash")
        else:
            self._confirm_and_save("Cash", None)

    def _confirm_and_save(self, method, delivery_info):
        subtotal = sum(i.get("price",0) for i in self.cart)
        delivery_fee = DELIVERY_FEE if self.delivery_type == "delivery" else 0
        total = subtotal + delivery_fee
        
        oid = str(uuid.uuid4())[:8].upper()
        order = {
            "id": oid, 
            "type": self.order_type, 
            "items": [i.get("name") for i in self.cart],
            "total": total, 
            "payment_method": method, 
            "delivery_type": self.delivery_type,
            "delivery_info": delivery_info,
            "status": "Pending",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.app.data.append_order(order)
        show_toast(self.app.root, f"✓ Order placed successfully!\nOrder ID: {oid}", bg=THEME["success"])

# -------------------- UPI QR Window --------------------
class UPIQRWindow:
    def __init__(self, app, cart, order_type, delivery_type, parent=None):
        self.app, self.cart, self.order_type = app, cart, order_type
        self.delivery_type = delivery_type
        self.win = tk.Toplevel(parent if parent else app.root)
        self.win.title("UPI Payment")
        self.win.configure(bg=THEME["bg"])
        self.win.transient(parent if parent else app.root)
        self.win.grab_set()
        center_window(self.win, 400, 460)
        
        tk.Label(self.win, text="Scan QR to Pay", bg=THEME["bg"], 
                fg=THEME["text"], font=app.font_h2).pack(pady=16)
        
        # QR placeholder
        qr_frame = tk.Frame(self.win, bg="#E5E7EB", bd=2, relief="solid")
        qr_frame.pack(pady=12)
        qr = tk.Label(qr_frame, text="📱\n\nQR CODE\nPLACEHOLDER\n\nScan with any UPI app", 
                     bg="#E5E7EB", fg=THEME["muted"], width=28, height=12, 
                     font=(THEME["font"], 10), justify="center")
        qr.pack(padx=20, pady=20)
        
        # Amount display
        subtotal = sum(i.get("price",0) for i in cart)
        delivery_fee = DELIVERY_FEE if delivery_type == "delivery" else 0
        total = subtotal + delivery_fee
        
        amount_frame = tk.Frame(self.win, bg=THEME["card"], bd=1, relief="solid")
        amount_frame.pack(fill="x", padx=40, pady=12)
        tk.Label(amount_frame, text=f"Amount to Pay: ₹{total:.2f}", bg=THEME["card"], 
                fg=THEME["accent"], font=(THEME["font"], 12, "bold")).pack(pady=10)
        
        tk.Button(self.win, text="✓ I've Paid - Confirm", bg=THEME["success"], 
                 fg="white", bd=0, font=app.font_b, width=26, pady=10, cursor="hand2",
                 command=self._confirm).pack(pady=8)
        tk.Button(self.win, text="Cancel", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, cursor="hand2", command=self.win.destroy).pack(pady=6)

    def _confirm(self):
        self.win.destroy()
        if self.delivery_type == "delivery":
            DeliveryDetailsWindow(self.app, self.cart, self.order_type, "UPI")
        else:
            # For pickup, finalize order
            subtotal = sum(i.get("price",0) for i in self.cart)
            total = subtotal
            oid = str(uuid.uuid4())[:8].upper()
            order = {
                "id": oid, 
                "type": self.order_type, 
                "items": [i.get("name") for i in self.cart],
                "total": total, 
                "payment_method": "UPI", 
                "delivery_type": "pickup",
                "delivery_info": None,
                "status": "Pending",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.app.data.append_order(order)
            show_toast(self.app.root, f"✓ Order placed successfully!\nOrder ID: {oid}", bg=THEME["success"])

# -------------------- Delivery Details Window --------------------
class DeliveryDetailsWindow:
    def __init__(self, app, cart, order_type, payment_method):
        self.app, self.cart, self.order_type = app, cart, order_type
        self.payment_method = payment_method
        self.win = tk.Toplevel(app.root)
        self.win.title("Delivery Details")
        self.win.transient(app.root)
        self.win.grab_set()
        self.win.configure(bg=THEME["bg"])
        center_window(self.win, 480, 380)
        
        tk.Label(self.win, text="📍 Delivery Information", bg=THEME["bg"], 
                fg=THEME["text"], font=app.font_h2).pack(pady=16)
        
        tk.Label(self.win, text="Please provide your delivery details", 
                bg=THEME["bg"], fg=THEME["muted"], 
                font=(THEME["font"], 9)).pack(pady=(0, 12))
        
        # Form
        frm = tk.Frame(self.win, bg=THEME["card"], bd=1, relief="solid")
        frm.pack(padx=40, pady=8, fill="both", expand=True)
        
        inner_frm = tk.Frame(frm, bg=THEME["card"])
        inner_frm.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(inner_frm, text="Class / Department:", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.cls = ttk.Entry(inner_frm, font=(THEME["font"], 10))
        self.cls.pack(fill="x", pady=(0, 12))
        
        tk.Label(inner_frm, text="Roll Number:", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.roll = ttk.Entry(inner_frm, font=(THEME["font"], 10))
        self.roll.pack(fill="x", pady=(0, 12))
        
        tk.Label(inner_frm, text="Preferred Delivery Time:", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 10, "bold")).pack(anchor="w", pady=(0, 4))
        tk.Label(inner_frm, text="(e.g., 12:30 PM, After 3rd period)", 
                bg=THEME["card"], fg=THEME["muted"], 
                font=(THEME["font"], 8)).pack(anchor="w")
        self.time = ttk.Entry(inner_frm, font=(THEME["font"], 10))
        self.time.pack(fill="x", pady=(4, 0))
        
        tk.Button(self.win, text="✓ Confirm Order", bg=THEME["success"], 
                 fg="white", bd=0, font=app.font_b, width=26, pady=10, cursor="hand2",
                 command=self._confirm).pack(pady=16)

    def _confirm(self):
        if not (self.cls.get().strip() and self.roll.get().strip() and self.time.get().strip()):
            messagebox.showerror("Incomplete", "Please fill all delivery fields")
            return
        
        subtotal = sum(i.get("price",0) for i in self.cart)
        total = subtotal + DELIVERY_FEE
        oid = str(uuid.uuid4())[:8].upper()
        
        delivery_info = {
            "class": self.cls.get().strip(), 
            "roll": self.roll.get().strip(), 
            "time": self.time.get().strip()
        }
        
        order = {
            "id": oid, 
            "type": self.order_type, 
            "items": [i.get("name") for i in self.cart],
            "total": total, 
            "payment_method": self.payment_method,
            "delivery_type": "delivery",
            "delivery_info": delivery_info,
            "status": "Pending",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.app.data.append_order(order)
        show_toast(self.app.root, f"✓ Order placed successfully!\nOrder ID: {oid}\nDelivery to: {delivery_info['class']}", 
                  bg=THEME["success"], duration=2500)
        self.win.destroy()

# -------------------- Owner Window --------------------
class OwnerWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Owner Portal – Yrush")
        self.win.configure(bg=THEME["bg"])
        center_window(self.win, 1000, 650)
        
        # Header
        header = tk.Frame(self.win, bg=THEME["card"])
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="🔐 Owner Portal", bg=THEME["card"], 
                fg=THEME["accent"], font=app.font_h1).pack(side="left", padx=20, pady=16)
        tk.Frame(self.win, bg=THEME["border"], height=1).pack(fill="x")
        
        self.nb = ttk.Notebook(self.win)
        self.nb.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabs = {}
        self._build_tabs()

    def _build_tabs(self):
        self.tabs["dash"] = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(self.tabs["dash"], text="📊 Dashboard")
        
        self.tabs["cm"] = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(self.tabs["cm"], text="🍽️ Canteen Menu")
        
        self.tabs["sm"] = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(self.tabs["sm"], text="📚 Suvidha Inventory")
        
        self.tabs["co"] = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(self.tabs["co"], text="🧾 Canteen Orders")
        
        self.tabs["so"] = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(self.tabs["so"], text="📦 Suvidha Orders")
        
        self._populate_dash()
        self._populate_canteen()
        self._populate_suvidha()
        self._populate_orders()

    def _populate_dash(self):
        t = self.tabs["dash"]
        tk.Label(t, text="Dashboard Overview", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(anchor="w", padx=20, pady=16)
        
        # Stats cards
        stats_frame = tk.Frame(t, bg=THEME["bg"])
        stats_frame.pack(fill="x", padx=20, pady=12)
        
        total_orders = len(self.app.data['orders'])
        canteen_orders = len([o for o in self.app.data['orders'] if o.get('type') == 'canteen'])
        suvidha_orders = len([o for o in self.app.data['orders'] if o.get('type') == 'suvidha'])
        
        # Total orders card
        card1 = tk.Frame(stats_frame, bg=THEME["card"], bd=1, relief="solid")
        card1.pack(side="left", fill="both", expand=True, padx=6, ipadx=20, ipady=16)
        tk.Label(card1, text=str(total_orders), bg=THEME["card"], 
                fg=THEME["accent"], font=(THEME["font"], 32, "bold")).pack()
        tk.Label(card1, text="Total Orders", bg=THEME["card"], 
                fg=THEME["muted"], font=(THEME["font"], 10)).pack()
        
        # Canteen orders card
        card2 = tk.Frame(stats_frame, bg=THEME["card"], bd=1, relief="solid")
        card2.pack(side="left", fill="both", expand=True, padx=6, ipadx=20, ipady=16)
        tk.Label(card2, text=str(canteen_orders), bg=THEME["card"], 
                fg=THEME["success"], font=(THEME["font"], 32, "bold")).pack()
        tk.Label(card2, text="Canteen Orders", bg=THEME["card"], 
                fg=THEME["muted"], font=(THEME["font"], 10)).pack()
        
        # Suvidha orders card
        card3 = tk.Frame(stats_frame, bg=THEME["card"], bd=1, relief="solid")
        card3.pack(side="left", fill="both", expand=True, padx=6, ipadx=20, ipady=16)
        tk.Label(card3, text=str(suvidha_orders), bg=THEME["card"], 
                fg=THEME["warn"], font=(THEME["font"], 32, "bold")).pack()
        tk.Label(card3, text="Suvidha Orders", bg=THEME["card"], 
                fg=THEME["muted"], font=(THEME["font"], 10)).pack()

    def _populate_canteen(self):
        t = self.tabs["cm"]
        
        header_frame = tk.Frame(t, bg=THEME["bg"])
        header_frame.pack(fill="x", padx=20, pady=16)
        tk.Label(header_frame, text="Canteen Menu Items", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        
        btn_frame = tk.Frame(header_frame, bg=THEME["bg"])
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="➕ Add Item", bg=THEME["accent"], fg="white", 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=lambda:self._add_item("canteen")).pack(side="left", padx=4)
        tk.Button(btn_frame, text="🔄 Refresh", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=self._refresh_canteen).pack(side="left", padx=4)
        
        # Tree view
        tree_frame = tk.Frame(t, bg=THEME["card"], bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.c_tree = ttk.Treeview(tree_frame, columns=("name","price","avail"), 
                                   show="headings", height=15)
        self.c_tree.heading("name", text="Item Name")
        self.c_tree.heading("price", text="Price (₹)")
        self.c_tree.heading("avail", text="Available")
        
        self.c_tree.column("name", width=300)
        self.c_tree.column("price", width=100)
        self.c_tree.column("avail", width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.c_tree.yview)
        self.c_tree.configure(yscrollcommand=scrollbar.set)
        
        self.c_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self._refresh_canteen()

    def _refresh_canteen(self):
        for i in self.c_tree.get_children():
            self.c_tree.delete(i)
        for it in self.app.data["canteen_items"]:
            self.c_tree.insert("", "end", values=(
                it.get("name"), 
                f"₹{it.get('price'):.2f}", 
                "✓ Yes" if it.get("available", True) else "✗ No"
            ))

    def _populate_suvidha(self):
        t = self.tabs["sm"]
        
        header_frame = tk.Frame(t, bg=THEME["bg"])
        header_frame.pack(fill="x", padx=20, pady=16)
        tk.Label(header_frame, text="Suvidha Store Inventory", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        
        btn_frame = tk.Frame(header_frame, bg=THEME["bg"])
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="➕ Add Item", bg=THEME["accent"], fg="white", 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=lambda:self._add_item("suvidha")).pack(side="left", padx=4)
        tk.Button(btn_frame, text="🔄 Refresh", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=self._refresh_suvidha).pack(side="left", padx=4)
        
        # Tree view
        tree_frame = tk.Frame(t, bg=THEME["card"], bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.s_tree = ttk.Treeview(tree_frame, columns=("name","price","stock","cat"), 
                                   show="headings", height=15)
        self.s_tree.heading("name", text="Item Name")
        self.s_tree.heading("price", text="Price (₹)")
        self.s_tree.heading("stock", text="Stock")
        self.s_tree.heading("cat", text="Category")
        
        self.s_tree.column("name", width=250)
        self.s_tree.column("price", width=100)
        self.s_tree.column("stock", width=80)
        self.s_tree.column("cat", width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.s_tree.yview)
        self.s_tree.configure(yscrollcommand=scrollbar.set)
        
        self.s_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self._refresh_suvidha()

    def _refresh_suvidha(self):
        for i in self.s_tree.get_children():
            self.s_tree.delete(i)
        for it in self.app.data["suvidha_items"]:
            self.s_tree.insert("", "end", values=(
                it.get("name"), 
                f"₹{it.get('price'):.2f}", 
                it.get("stock", 0), 
                it.get("category", "Others")
            ))

    def _populate_orders(self):
        # Canteen Orders
        t1 = self.tabs["co"]
        
        header1 = tk.Frame(t1, bg=THEME["bg"])
        header1.pack(fill="x", padx=20, pady=16)
        tk.Label(header1, text="Canteen Orders", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        tk.Button(header1, text="🔄 Refresh", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=lambda: self._refresh_orders("canteen")).pack(side="right")
        
        self.co_frame = tk.Frame(t1, bg=THEME["bg"])
        self.co_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Suvidha Orders
        t2 = self.tabs["so"]
        
        header2 = tk.Frame(t2, bg=THEME["bg"])
        header2.pack(fill="x", padx=20, pady=16)
        tk.Label(header2, text="Suvidha Orders", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        tk.Button(header2, text="🔄 Refresh", bg=THEME["card"], fg=THEME["muted"], 
                 bd=0, padx=12, pady=6, cursor="hand2",
                 command=lambda: self._refresh_orders("suvidha")).pack(side="right")
        
        self.so_frame = tk.Frame(t2, bg=THEME["bg"])
        self.so_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._refresh_orders("canteen")
        self._refresh_orders("suvidha")

    def _refresh_orders(self, order_type):
        # Clear existing widgets
        target_frame = self.co_frame if order_type == "canteen" else self.so_frame
        for widget in target_frame.winfo_children():
            widget.destroy()
        
        # Canvas with scrollbar
        canvas = tk.Canvas(target_frame, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(target_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=THEME["bg"])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        orders = [o for o in self.app.data["orders"] if o.get("type") == order_type]
        
        if not orders:
            tk.Label(scroll_frame, text="No orders yet", bg=THEME["bg"], 
                    fg=THEME["muted"], font=(THEME["font"], 11)).pack(pady=40)
        else:
            for o in reversed(orders):  # Show latest first
                order_card = tk.Frame(scroll_frame, bg=THEME["card"], bd=1, relief="solid")
                order_card.pack(fill="x", pady=8, padx=4)
                
                # Order header
                header = tk.Frame(order_card, bg=THEME["card"])
                header.pack(fill="x", padx=16, pady=(12, 8))
                
                tk.Label(header, text=f"Order #{o.get('id')}", bg=THEME["card"], 
                        fg=THEME["text"], font=(THEME["font"], 11, "bold")).pack(side="left")
                
                status = o.get("status", "Pending")
                status_colors = {
                    "Pending": THEME["warn"],
                    "Preparing": THEME["accent"],
                    "Ready": THEME["success"],
                    "Completed": THEME["muted"]
                }
                create_badge(header, status, status_colors.get(status, THEME["muted"])).pack(side="left", padx=8)
                
                tk.Label(header, text=f"₹{o.get('total'):.2f}", bg=THEME["card"], 
                        fg=THEME["accent"], font=(THEME["font"], 11, "bold")).pack(side="right")
                
                # Order details
                details = tk.Frame(order_card, bg=THEME["card"])
                details.pack(fill="x", padx=16, pady=8)
                
                tk.Label(details, text=f"Items: {', '.join(o.get('items', []))}", 
                        bg=THEME["card"], fg=THEME["muted"], 
                        font=(THEME["font"], 9)).pack(anchor="w")
                tk.Label(details, text=f"Payment: {o.get('payment_method')} | Type: {o.get('delivery_type', 'N/A').title()}", 
                        bg=THEME["card"], fg=THEME["muted"], 
                        font=(THEME["font"], 9)).pack(anchor="w")
                
                if o.get('delivery_info'):
                    info = o.get('delivery_info')
                    tk.Label(details, text=f"Delivery: {info.get('class')} | Roll: {info.get('roll')} | Time: {info.get('time')}", 
                            bg=THEME["card"], fg=THEME["muted"], 
                            font=(THEME["font"], 9)).pack(anchor="w")
                
                tk.Label(details, text=f"Time: {o.get('time')}", 
                        bg=THEME["card"], fg=THEME["muted"], 
                        font=(THEME["font"], 8)).pack(anchor="w")
                
                # Action buttons
                if status != "Completed":
                    btn_frame = tk.Frame(order_card, bg=THEME["card"])
                    btn_frame.pack(fill="x", padx=16, pady=(4, 12))
                    
                    if status == "Pending":
                        tk.Button(btn_frame, text="▶ Start Preparing", bg=THEME["accent"], 
                                fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                                command=lambda oid=o.get('id'): self._update_status(oid, "Preparing", order_type)).pack(side="left", padx=4)
                    elif status == "Preparing":
                        tk.Button(btn_frame, text="✓ Mark Ready", bg=THEME["success"], 
                                fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                                command=lambda oid=o.get('id'): self._update_status(oid, "Ready", order_type)).pack(side="left", padx=4)
                    elif status == "Ready":
                        tk.Button(btn_frame, text="✓ Complete Order", bg=THEME["success"], 
                                fg="white", bd=0, padx=10, pady=4, cursor="hand2",
                                command=lambda oid=o.get('id'): self._update_status(oid, "Completed", order_type)).pack(side="left", padx=4)
        
        scroll_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def _update_status(self, order_id, new_status, order_type):
        if self.app.data.update_order_status(order_id, new_status):
            show_toast(self.app.root, f"✓ Order {order_id} marked as {new_status}", bg=THEME["success"])
            self._refresh_orders(order_type)
        else:
            messagebox.showerror("Error", "Failed to update order status")

    def _add_item(self, kind):
        dlg = tk.Toplevel(self.win)
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.title(f"Add {kind.title()} Item")
        dlg.configure(bg=THEME["bg"])
        center_window(dlg, 480, 360)
        
        tk.Label(dlg, text=f"Add New {kind.title()} Item", bg=THEME["bg"], 
                fg=THEME["text"], font=self.app.font_h2).pack(pady=16)
        
        frm = tk.Frame(dlg, bg=THEME["card"], bd=1, relief="solid")
        frm.pack(padx=40, pady=8, fill="both", expand=True)
        
        inner_frm = tk.Frame(frm, bg=THEME["card"])
        inner_frm.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(inner_frm, text="Item Name:", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        name_ent = ttk.Entry(inner_frm, font=(THEME["font"], 10))
        name_ent.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))
        
        tk.Label(inner_frm, text="Price (₹):", bg=THEME["card"], 
                fg=THEME["text"], font=(THEME["font"], 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        price_ent = ttk.Entry(inner_frm, font=(THEME["font"], 10))
        price_ent.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))
        
        if kind == "suvidha":
            tk.Label(inner_frm, text="Stock:", bg=THEME["card"], 
                    fg=THEME["text"], font=(THEME["font"], 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
            stock_ent = ttk.Entry(inner_frm, font=(THEME["font"], 10))
            stock_ent.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))
            
            tk.Label(inner_frm, text="Category:", bg=THEME["card"], 
                    fg=THEME["text"], font=(THEME["font"], 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
            cat_var = tk.StringVar(value=SUVIDHA_CATEGORIES[0])
            cat_dropdown = ttk.Combobox(inner_frm, textvariable=cat_var, 
                                       values=SUVIDHA_CATEGORIES, 
                                       state="readonly", font=(THEME["font"], 10))
            cat_dropdown.grid(row=3, column=1, sticky="ew", pady=4, padx=(8, 0))
        
        inner_frm.columnconfigure(1, weight=1)
        
        def do_add():
            name = name_ent.get().strip()
            price = safe_to_float(price_ent.get())
            if not name or price <= 0:
                messagebox.showerror("Invalid Input", "Please enter valid name and price")
                return
            
            if kind == "canteen":
                self.app.data.db["canteen_items"].append({
                    "name": name, 
                    "price": price, 
                    "available": True
                })
                self.app.data.save()
                self._refresh_canteen()
            else:
                stock = safe_to_float(stock_ent.get())
                cat = cat_var.get()
                self.app.data.db["suvidha_items"].append({
                    "name": name, 
                    "price": price, 
                    "stock": int(stock), 
                    "category": cat
                })
                self.app.data.save()
                self._refresh_suvidha()
            
            dlg.destroy()
            show_toast(self.app.root, f"✓ Added {name}", bg=THEME["success"])
        
        tk.Button(dlg, text="➕ Add Item", bg=THEME["accent"], fg="white", 
                 bd=0, font=self.app.font_b, padx=20, pady=10, cursor="hand2",
                 command=do_add).pack(pady=16)

# -------------------- Run App --------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x580")
    app = YrushApp(root)
    root.mainloop()