# Yrush_v2.5.py
"""
Yrush v2.5 — Finalized Campus-Tech Dark
- Splash screen (2s)
- Resizable main window
- Delivery option popup (₹5)
- Owner Portal (modal add/edit dialogs, full-screen tables)
- Orders tab: separate Canteen & Suvidha sections + Refresh button
- Toast notifications for user feedback
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.font import Font
import json, os, uuid
from datetime import datetime

# -------------------- CONFIG / THEME --------------------
DATA_FILE = "yrush_data.json"
OWNER_PW = "admin123"
DELIVERY_FEE = 5

THEME = {
    "bg": "#0B0F19",
    "bg2": "#111827",
    "card": "#161B28",
    "accent": "#3B82F6",
    "success": "#10B981",
    "warn": "#F59E0B",
    "danger": "#EF4444",
    "text": "#F9FAFB",
    "muted": "#9CA3AF",
    "shadow": "#05060A",
    "font": "Segoe UI",
    "radius": 10
}

# -------------------- Data Store --------------------
class DataStore:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.db = json.load(f)
                for k in ("canteen_items", "suvidha_items", "orders"):
                    if k not in self.db:
                        self.db[k] = []
                self.save()
            except Exception as e:
                print(f"[Yrush] Data load error: {e}. Creating new DB.")
                self.db = {"canteen_items": [], "suvidha_items": [], "orders": []}
                self.save()
        else:
            self.db = {"canteen_items": [], "suvidha_items": [], "orders": []}
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            except Exception:
                pass
            self.save()

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Yrush] Save error: {e}")

    def __getitem__(self, item):
        return self.db[item]

    def __setitem__(self, key, value):
        self.db[key] = value
        self.save()

# -------------------- Utilities --------------------
def center_window(win, w=600, h=400):
    win.update_idletasks()
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def safe_float(s, fallback=0.0):
    try:
        return float(s)
    except Exception:
        return fallback

def safe_int(s, fallback=0):
    try:
        return int(s)
    except Exception:
        return fallback

# Toast manager
def show_toast(root, message, duration=2200):
    # bottom-right toast
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(bg="#000000")
    # styling frame
    frm = tk.Frame(toast, bg="#0B1220", bd=0, relief="flat")
    frm.pack(fill="both", expand=True)
    lbl = tk.Label(frm, text=message, bg="#0B1220", fg=THEME["text"], font=(THEME["font"], 10))
    lbl.pack(padx=12, pady=8)
    # position: bottom-right of root window
    root.update_idletasks()
    rx = root.winfo_rootx()
    ry = root.winfo_rooty()
    rw = root.winfo_width()
    rh = root.winfo_height()
    x = rx + rw - 320
    y = ry + rh - 90
    toast.geometry(f"300x50+{x}+{y}")
    # fade out after duration
    toast.after(duration, toast.destroy)

# -------------------- Main Application --------------------
class YrushApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.withdraw()  # hide while splash shows
        self.root.title("Yrush — Campus Services")
        # Make resizable
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.data = DataStore(DATA_FILE)
        self._fonts()
        self._style()
        self._show_splash()

    def _fonts(self):
        self.font_h1 = Font(family=THEME["font"], size=28, weight="bold")
        self.font_h2 = Font(family=THEME["font"], size=18, weight="bold")
        self.font_h3 = Font(family=THEME["font"], size=14, weight="bold")
        self.font_b  = Font(family=THEME["font"], size=11)
        self.font_sm = Font(family=THEME["font"], size=9)

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure('TNotebook.Tab', font=(THEME["font"], 10), padding=[12,8])
        style.configure("Treeview", background=THEME["card"], fieldbackground=THEME["card"],
                        foreground=THEME["text"], rowheight=24, font=(THEME["font"], 10))
        style.configure("TCombobox", fieldbackground=THEME["card"], background=THEME["card"],
                        foreground=THEME["text"], font=(THEME["font"], 10))

    # ------------------ Splash Screen ------------------
    def _show_splash(self):
        splash = tk.Toplevel()
        splash.overrideredirect(True)
        splash.configure(bg=THEME["bg"])
        center_window(splash, 600, 320)

        frame = tk.Frame(splash, bg=THEME["bg"])
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Yrush", font=self.font_h1, fg=THEME["accent"], bg=THEME["bg"]).pack(pady=(50,8))
        tk.Label(frame, text="Launching Yrush — Campus Services", font=self.font_b, fg=THEME["muted"], bg=THEME["bg"]).pack()

        bar_holder = tk.Frame(frame, bg=THEME["card"], height=10)
        bar_holder.pack(padx=40, pady=30, fill="x")
        bar_holder.pack_propagate(False)
        bar = tk.Frame(bar_holder, bg=THEME["accent"], width=0, height=10)
        bar.place(relx=0, rely=0)

        duration = 1800
        steps = 40
        delay = duration // steps
        max_w = 520
        def animate(step=0):
            w = int((step/steps) * max_w)
            bar.config(width=max(0, w))
            if step < steps:
                splash.after(delay, lambda: animate(step+1))
        animate(0)

        def end_splash():
            splash.destroy()
            self.root.deiconify()
            self._build_ui()
        splash.after(2000, end_splash)

    # ------------------ Main UI ------------------
    def _build_ui(self):
        self.root.configure(bg=THEME["bg"])
        for w in self.root.winfo_children():
            w.destroy()

        header = tk.Frame(self.root, bg=THEME["card"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        left = tk.Frame(header, bg=THEME["card"])
        left.pack(side="left", padx=24, pady=12)
        tk.Label(left, text="Yrush", fg=THEME["accent"], bg=THEME["card"], font=self.font_h1).pack(anchor="w")
        tk.Label(left, text="Campus Services — Canteen & Suvidha (Stationery & Books)", fg=THEME["muted"], bg=THEME["card"], font=self.font_b).pack(anchor="w")

        right = tk.Frame(header, bg=THEME["card"])
        right.pack(side="right", padx=20)
        owner_btn = tk.Button(right, text="Owner Portal", bg=THEME["accent"], fg="white", bd=0, font=self.font_b, cursor="hand2", command=self._owner_login)
        owner_btn.pack(padx=6, pady=20)

        body = tk.Frame(self.root, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=20)

        cards_frame = tk.Frame(body, bg=THEME["bg"])
        cards_frame.pack(fill="both", expand=True)

        can_fr = tk.Frame(cards_frame, bg=THEME["card"])
        can_fr.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        can_fr.pack_propagate(False)
        tk.Label(can_fr, text="🍔 Canteen", bg=THEME["card"], fg=THEME["text"], font=self.font_h2).pack(anchor="nw", padx=16, pady=(14,4))
        tk.Label(can_fr, text="Pre-order meals, snacks and drinks.", bg=THEME["card"], fg=THEME["muted"], font=self.font_b).pack(anchor="nw", padx=16)
        tk.Button(can_fr, text="Open Canteen →", bg=THEME["accent"], fg="white", bd=0, font=self.font_b, cursor="hand2", command=lambda: CanteenWindow(self)).pack(anchor="sw", side="bottom", pady=16, padx=16)

        suv_fr = tk.Frame(cards_frame, bg=THEME["card"])
        suv_fr.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        suv_fr.pack_propagate(False)
        tk.Label(suv_fr, text="📚 Suvidha (Stationery & Books)", bg=THEME["card"], fg=THEME["text"], font=self.font_h2).pack(anchor="nw", padx=16, pady=(14,4))
        tk.Label(suv_fr, text="Buy notebooks, pens, textbooks and more.", bg=THEME["card"], fg=THEME["muted"], font=self.font_b).pack(anchor="nw", padx=16)
        tk.Button(suv_fr, text="Open Suvidha →", bg=THEME["accent"], fg="white", bd=0, font=self.font_b, cursor="hand2", command=lambda: SuvidhaWindow(self)).pack(anchor="sw", side="bottom", pady=16, padx=16)

    # ------------------ Owner Login Modal ------------------
    def _owner_login(self):
        win = tk.Toplevel(self.root)
        win.title("Owner Login — Yrush")
        win.configure(bg=THEME["bg"])
        win.transient(self.root)
        win.grab_set()
        center_window(win, 420, 260)

        frame = tk.Frame(win, bg=THEME["bg"])
        frame.pack(fill="both", expand=True, padx=26, pady=26)

        tk.Label(frame, text="Owner Access", bg=THEME["bg"], fg=THEME["text"], font=self.font_h2).pack(pady=(6,8))
        tk.Label(frame, text="Enter password", bg=THEME["bg"], fg=THEME["muted"], font=self.font_b).pack()
        pw = ttk.Entry(frame, show="●", width=28, font=self.font_b)
        pw.pack(pady=12)

        def verify():
            if pw.get() == OWNER_PW:
                win.destroy()
                OwnerWindow(self)
            else:
                messagebox.showerror("Access Denied", "Incorrect password.")

        tk.Button(frame, text="Login", bg=THEME["accent"], fg="white", bd=0, font=self.font_b, command=verify).pack(pady=6)
        pw.bind("<Return>", lambda e: verify())
        pw.focus()
        win.wait_window(win)

# -------------------- Canteen Window --------------------
class CanteenWindow:
    def __init__(self, app: YrushApp):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Yrush — Canteen")
        self.win.geometry("1100x750")
        self.win.minsize(900, 650)
        self.win.configure(bg=THEME["bg"])
        self.win.transient(app.root)
        self.cart = {}
        self._build_ui()
        self._load_items()

    def _build_ui(self):
        hdr = tk.Frame(self.win, bg=THEME["card"], height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🍔 Canteen", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h2).pack(side="left", padx=18, pady=18)
        tk.Button(hdr, text="✕", bg=THEME["card"], fg=THEME["muted"], bd=0, command=self.win.destroy).pack(side="right", padx=18)

        body = tk.Frame(self.win, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=14)

        left = tk.Frame(body, bg=THEME["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0,12))

        menu_hdr = tk.Frame(left, bg=THEME["bg"])
        menu_hdr.pack(fill="x", pady=(0,8))
        tk.Label(menu_hdr, text="Menu", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        tk.Label(menu_hdr, text=f"{len(self.app.data['canteen_items'])} items", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b).pack(side="left", padx=12)

        canvas = tk.Canvas(left, bg=THEME["bg"], highlightthickness=0)
        vs = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        self.menu_container = tk.Frame(canvas, bg=THEME["bg"])
        self.menu_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.menu_container, anchor="nw")
        canvas.configure(yscrollcommand=vs.set)
        canvas.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        right = tk.Frame(body, bg=THEME["card"], width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="🛒 Your Cart", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h3).pack(pady=(18,6))
        self.cart_list = tk.Listbox(right, bg=THEME["card"], fg=THEME["text"], bd=0, font=self.app.font_b, height=12, selectbackground=THEME["accent"])
        self.cart_list.pack(fill="both", padx=12, pady=6)
        tk.Button(right, text="Remove Selected", bg=THEME["muted"], fg="white", bd=0, command=self.remove_from_cart).pack(pady=6)
        self.total_lbl = tk.Label(right, text="Total: ₹0", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h2)
        self.total_lbl.pack(pady=12)
        tk.Button(right, text="Place Order", bg=THEME["accent"], fg="white", bd=0, font=self.app.font_b, command=self.place_order).pack(pady=12)

    def _load_items(self):
        for w in self.menu_container.winfo_children():
            w.destroy()
        for item in self.app.data["canteen_items"]:
            self._item_card(item)

    def _item_card(self, item):
        card = tk.Frame(self.menu_container, bg=THEME["card"])
        card.pack(fill="x", pady=8, padx=6)
        left = tk.Frame(card, bg=THEME["card"])
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text=item.get("name",""), bg=THEME["card"], fg=THEME["text"], font=self.app.font_h3).pack(anchor="w")
        tk.Label(left, text=f"₹{item.get('price',0)}", bg=THEME["card"], fg=THEME["accent"], font=self.app.font_b).pack(anchor="w", pady=(6,0))
        status = "Available" if item.get("available", True) else "Not Available"
        color = THEME["success"] if item.get("available", True) else THEME["muted"]
        tk.Label(left, text=status, bg=THEME["card"], fg=color, font=self.app.font_sm).pack(anchor="w", pady=(4,0))

        if item.get("available", True):
            right = tk.Frame(card, bg=THEME["card"])
            right.pack(side="right", padx=8)
            qty_var = tk.IntVar(value=1)
            spin = tk.Spinbox(right, from_=1, to=20, width=4, textvariable=qty_var, font=self.app.font_b)
            spin.pack(side="left", padx=6)
            tk.Button(right, text="Add", bg=THEME["accent"], fg="white", bd=0, command=lambda i=item, q=qty_var: self.add_cart(i, int(q.get()))).pack(side="left")

    def add_cart(self, item, qty):
        if qty <= 0:
            return
        key = item["name"]
        if key in self.cart:
            self.cart[key]["qty"] += qty
        else:
            self.cart[key] = {"item": item, "qty": qty}
        self._update_cart()
        show_toast(self.app.root, f"✅ Added {qty} × {item['name']}")

    def remove_from_cart(self):
        sel = self.cart_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item to remove")
            return
        idx = sel[0]
        name = list(self.cart.keys())[idx]
        del self.cart[name]
        self._update_cart()
        show_toast(self.app.root, "✅ Item removed from cart")

    def _update_cart(self):
        self.cart_list.delete(0, "end")
        total = 0
        for k, v in self.cart.items():
            line_total = v["item"]["price"] * v["qty"]
            total += line_total
            self.cart_list.insert("end", f"{v['item']['name']} × {v['qty']}  —  ₹{line_total}")
        self.total_lbl.config(text=f"Total: ₹{total}")

    def _delivery_modal(self, base_total):
        dlg = tk.Toplevel(self.win)
        dlg.title("Delivery or Pick-up")
        dlg.configure(bg=THEME["bg"])
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.focus_force()
        center_window(dlg, 440, 320)

        tk.Label(dlg, text="Choose Delivery Option", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2).pack(pady=(18,8))
        mode = tk.StringVar(value="pickup")
        rbf = tk.Frame(dlg, bg=THEME["bg"])
        rb1 = ttk.Radiobutton(rbf, text="Pick-up", variable=mode, value="pickup")
        rb2 = ttk.Radiobutton(rbf, text=f"Delivery (+₹{DELIVERY_FEE})", variable=mode, value="delivery")
        rb1.pack(side="left", padx=10); rb2.pack(side="left", padx=10)
        rbf.pack(pady=8)

        info_fr = tk.Frame(dlg, bg=THEME["bg"])
        info_fr.pack(fill="both", expand=True, padx=16, pady=8)

        cls_ent = ttk.Entry(info_fr)
        roll_ent = ttk.Entry(info_fr)
        time_ent = ttk.Entry(info_fr)
        lbl_cls = tk.Label(info_fr, text="Class:", bg=THEME["bg"], fg=THEME["muted"])
        lbl_roll = tk.Label(info_fr, text="Roll No:", bg=THEME["bg"], fg=THEME["muted"])
        lbl_time = tk.Label(info_fr, text="Time (e.g. 12:30 PM):", bg=THEME["bg"], fg=THEME["muted"])

        def show_hide(*a):
            if mode.get() == "delivery":
                lbl_cls.pack(anchor="w", pady=(6,0)); cls_ent.pack(fill="x", pady=(0,4))
                lbl_roll.pack(anchor="w", pady=(6,0)); roll_ent.pack(fill="x", pady=(0,4))
                lbl_time.pack(anchor="w", pady=(6,0)); time_ent.pack(fill="x", pady=(0,4))
            else:
                for w in (lbl_cls, cls_ent, lbl_roll, roll_ent, lbl_time, time_ent):
                    w.pack_forget()
        mode.trace_add("write", lambda *e: show_hide()); show_hide()

        result = {"ok": False, "delivery": False, "info": {}, "fee": 0}
        def confirm():
            if mode.get() == "delivery":
                c = cls_ent.get().strip(); r = roll_ent.get().strip(); t = time_ent.get().strip()
                if not (c and r and t):
                    messagebox.showerror("Missing Info", "Please enter Class, Roll No and Time for delivery.")
                    return
                result.update({"ok": True, "delivery": True, "info": {"class": c, "roll": r, "time": t}, "fee": DELIVERY_FEE})
            else:
                result.update({"ok": True, "delivery": False, "info": {}, "fee": 0})
            dlg.destroy()

        tk.Button(dlg, text="Confirm", bg=THEME["accent"], fg="white", bd=0, command=confirm).pack(pady=10)
        dlg.wait_window()
        return result if result["ok"] else None

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return
        base_total = sum(v["item"]["price"] * v["qty"] for v in self.cart.values())
        modal = self._delivery_modal(base_total)
        if not modal:
            return
        final_total = base_total + modal["fee"]
        oid = str(uuid.uuid4())[:8].upper()
        items = [{"name": v["item"]["name"], "qty": v["qty"], "price": v["item"]["price"]} for v in self.cart.values()]

        order = {
            "id": oid,
            "type": "canteen",
            "items": items,
            "total": final_total,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "delivery": modal["delivery"],
            "delivery_info": modal["info"],
            "delivery_fee": modal["fee"]
        }
        self.app.data["orders"].append(order)
        self.app.data.save()
        show_toast(self.app.root, f"✅ Order placed: {oid}")
        self.cart.clear()
        self._update_cart()

# -------------------- Suvidha Window --------------------
class SuvidhaWindow:
    def __init__(self, app: YrushApp):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Yrush — Suvidha (Stationery & Books)")
        self.win.geometry("1100x750")
        self.win.minsize(900, 650)
        self.win.configure(bg=THEME["bg"])
        self.win.transient(app.root)
        self.cart = {}
        self.cat_var = tk.StringVar(value="All")
        self._build_ui()
        self._load_items()

    def _build_ui(self):
        hdr = tk.Frame(self.win, bg=THEME["card"], height=80)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="📚 Suvidha — Stationery & Book Shop", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h2).pack(side="left", padx=18, pady=18)
        tk.Button(hdr, text="✕", bg=THEME["card"], fg=THEME["muted"], bd=0, command=self.win.destroy).pack(side="right", padx=18)

        body = tk.Frame(self.win, bg=THEME["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=14)

        top = tk.Frame(body, bg=THEME["bg"])
        top.pack(fill="x", pady=(0,8))
        tk.Label(top, text="Filter by Category:", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_b).pack(side="left")
        combo = ttk.Combobox(top, textvariable=self.cat_var, values=["All", "Books", "Notebooks", "Pens", "Other Stationery"], state="readonly", width=22)
        combo.pack(side="left", padx=10)
        combo.bind("<<ComboboxSelected>>", lambda e: self._load_items())

        canvas = tk.Canvas(body, bg=THEME["bg"], highlightthickness=0)
        vs = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        self.container = tk.Frame(canvas, bg=THEME["bg"])
        self.container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.container, anchor="nw")
        canvas.configure(yscrollcommand=vs.set)
        canvas.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        right = tk.Frame(self.win, bg=THEME["card"], width=320)
        right.pack(side="right", fill="y"); right.pack_propagate(False)
        tk.Label(right, text="🛒 Your Cart", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h3).pack(pady=(18,6))
        self.cart_list = tk.Listbox(right, bg=THEME["card"], fg=THEME["text"], bd=0, font=self.app.font_b, height=12, selectbackground=THEME["accent"])
        self.cart_list.pack(fill="both", padx=12, pady=6)
        tk.Button(right, text="Remove Selected", bg=THEME["muted"], fg="white", bd=0, command=self.remove_from_cart).pack(pady=6)
        self.total_lbl = tk.Label(right, text="Total: ₹0", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h2)
        self.total_lbl.pack(pady=12)
        tk.Button(right, text="Place Order", bg=THEME["accent"], fg="white", bd=0, font=self.app.font_b, command=self.place_order).pack(pady=12)

    def _load_items(self):
        for w in self.container.winfo_children():
            w.destroy()
        cat = self.cat_var.get()
        items = [it for it in self.app.data["suvidha_items"] if cat == "All" or it.get("category") == cat]
        if not items:
            tk.Label(self.container, text="No items found.", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_h3).pack(pady=40)
            return
        for item in items:
            self._item_card(item)

    def _item_card(self, item):
        card = tk.Frame(self.container, bg=THEME["card"])
        card.pack(fill="x", pady=8, padx=6)
        left = tk.Frame(card, bg=THEME["card"])
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text=item.get("name",""), bg=THEME["card"], fg=THEME["text"], font=self.app.font_h3).pack(anchor="w")
        tk.Label(left, text=f"₹{item.get('price',0)}", bg=THEME["card"], fg=THEME["accent"], font=self.app.font_b).pack(anchor="w", pady=(6,0))
        tk.Label(left, text=f"Stock: {item.get('stock',0)}", bg=THEME["card"], fg=THEME["muted"], font=self.app.font_sm).pack(anchor="w", pady=(4,0))

        if item.get("stock",0) > 0:
            right = tk.Frame(card, bg=THEME["card"])
            right.pack(side="right", padx=8)
            qty_var = tk.IntVar(value=1)
            spin = tk.Spinbox(right, from_=1, to=item.get("stock",1), width=4, textvariable=qty_var, font=self.app.font_b)
            spin.pack(side="left", padx=6)
            tk.Button(right, text="Add", bg=THEME["accent"], fg="white", bd=0, command=lambda i=item, q=qty_var: self.add_cart(i, int(q.get()))).pack(side="left")

    def add_cart(self, item, qty):
        if qty <= 0 or qty > item.get("stock",0):
            messagebox.showerror("Invalid quantity", "Please enter a valid quantity within stock limits.")
            return
        key = item["name"]
        if key in self.cart:
            self.cart[key]["qty"] += qty
        else:
            self.cart[key] = {"item": item, "qty": qty}
        self._update_cart()
        show_toast(self.app.root, f"✅ Added {qty} × {item['name']}")

    def remove_from_cart(self):
        sel = self.cart_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item to remove")
            return
        idx = sel[0]
        name = list(self.cart.keys())[idx]
        del self.cart[name]
        self._update_cart()
        show_toast(self.app.root, "✅ Item removed from cart")

    def _update_cart(self):
        self.cart_list.delete(0, "end")
        total = 0
        for k, v in self.cart.items():
            line_total = v["item"]["price"] * v["qty"]
            total += line_total
            self.cart_list.insert("end", f"{v['item']['name']} × {v['qty']}  —  ₹{line_total}")
        self.total_lbl.config(text=f"Total: ₹{total}")

    def _delivery_modal(self, base_total):
        dlg = tk.Toplevel(self.win)
        dlg.title("Delivery or Pick-up")
        dlg.configure(bg=THEME["bg"])
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.focus_force()
        center_window(dlg, 440, 320)

        tk.Label(dlg, text="Choose Delivery Option", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2).pack(pady=(18,8))
        mode = tk.StringVar(value="pickup")
        rbf = tk.Frame(dlg, bg=THEME["bg"])
        rb1 = ttk.Radiobutton(rbf, text="Pick-up", variable=mode, value="pickup")
        rb2 = ttk.Radiobutton(rbf, text=f"Delivery (+₹{DELIVERY_FEE})", variable=mode, value="delivery")
        rb1.pack(side="left", padx=10); rb2.pack(side="left", padx=10)
        rbf.pack(pady=8)

        info_fr = tk.Frame(dlg, bg=THEME["bg"])
        info_fr.pack(fill="both", expand=True, padx=16, pady=8)

        cls_ent = ttk.Entry(info_fr)
        roll_ent = ttk.Entry(info_fr)
        time_ent = ttk.Entry(info_fr)
        lbl_cls = tk.Label(info_fr, text="Class:", bg=THEME["bg"], fg=THEME["muted"])
        lbl_roll = tk.Label(info_fr, text="Roll No:", bg=THEME["bg"], fg=THEME["muted"])
        lbl_time = tk.Label(info_fr, text="Time (e.g. 12:30 PM):", bg=THEME["bg"], fg=THEME["muted"])

        def show_hide(*a):
            if mode.get() == "delivery":
                lbl_cls.pack(anchor="w", pady=(6,0)); cls_ent.pack(fill="x", pady=(0,4))
                lbl_roll.pack(anchor="w", pady=(6,0)); roll_ent.pack(fill="x", pady=(0,4))
                lbl_time.pack(anchor="w", pady=(6,0)); time_ent.pack(fill="x", pady=(0,4))
            else:
                for w in (lbl_cls, cls_ent, lbl_roll, roll_ent, lbl_time, time_ent):
                    w.pack_forget()
        mode.trace_add("write", lambda *e: show_hide()); show_hide()

        res = {"ok": False, "delivery": False, "info": {}, "fee": 0}
        def confirm():
            if mode.get() == "delivery":
                c = cls_ent.get().strip(); r = roll_ent.get().strip(); t = time_ent.get().strip()
                if not (c and r and t):
                    messagebox.showerror("Missing Info", "Please enter Class, Roll No and Time for delivery.")
                    return
                res.update({"ok": True, "delivery": True, "info": {"class": c, "roll": r, "time": t}, "fee": DELIVERY_FEE})
            else:
                res.update({"ok": True, "delivery": False, "info": {}, "fee": 0})
            dlg.destroy()

        tk.Button(dlg, text="Confirm", bg=THEME["accent"], fg="white", bd=0, command=confirm).pack(pady=10)
        dlg.wait_window()
        return res if res["ok"] else None

    def place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return
        base_total = sum(v["item"]["price"] * v["qty"] for v in self.cart.values())
        modal = self._delivery_modal(base_total)
        if not modal:
            return
        final_total = base_total + modal["fee"]
        oid = str(uuid.uuid4())[:8].upper()
        items = [{"name": v["item"]["name"], "qty": v["qty"], "price": v["item"]["price"]} for v in self.cart.values()]

        for v in self.cart.values():
            if "stock" in v["item"]:
                v["item"]["stock"] = max(0, v["item"].get("stock",0) - v["qty"])
        self.app.data.save()

        order = {
            "id": oid,
            "type": "suvidha",
            "items": items,
            "total": final_total,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "delivery": modal["delivery"],
            "delivery_info": modal["info"],
            "delivery_fee": modal["fee"]
        }
        self.app.data["orders"].append(order)
        self.app.data.save()
        show_toast(self.app.root, f"✅ Order placed: {oid}")
        self.cart.clear()
        self._update_cart()
        self._load_items()

# -------------------- Owner Window (v2.5) --------------------
class OwnerWindow:
    def __init__(self, app: YrushApp):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title("Yrush — Owner Portal")
        self.win.geometry("1200x820")
        self.win.minsize(1000, 700)
        self.win.configure(bg=THEME["bg"])

        container = tk.Frame(self.win, bg=THEME["bg"])
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=THEME["bg"], highlightthickness=0)
        vs = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=THEME["bg"])
        canvas.create_window((0,0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        style = ttk.Style()
        style.configure('TNotebook.Tab', font=(THEME["font"], 10), padding=[12,8])
        self.nb = ttk.Notebook(self.inner)
        self.nb.pack(fill="both", expand=True, padx=18, pady=18)

        self._dashboard_tab()
        self._canteen_tab()
        self._suvidha_tab()
        self._orders_tab()

    # Dashboard
    def _dashboard_tab(self):
        tab = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(tab, text="  Dashboard  ")

        header = tk.Frame(tab, bg=THEME["bg"])
        header.pack(fill="x", padx=18, pady=(12,8))
        tk.Label(header, text="Owner Dashboard", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2).pack(side="left")

        stats_frame = tk.Frame(tab, bg=THEME["bg"])
        stats_frame.pack(fill="x", padx=18, pady=12)

        total_orders = len(self.app.data["orders"])
        pending = sum(1 for o in self.app.data["orders"] if o.get("status")=="pending")
        completed = sum(1 for o in self.app.data["orders"] if o.get("status")=="completed")

        def stat_card(parent, label, value, color):
            c = tk.Frame(parent, bg=color, padx=14, pady=12)
            c.pack(side="left", padx=12, ipadx=12, ipady=4)
            tk.Label(c, text=str(value), bg=color, fg="white", font=self.app.font_h2).pack()
            tk.Label(c, text=label, bg=color, fg="white", font=self.app.font_b).pack()
        stat_card(stats_frame, "Total Orders", total_orders, THEME["accent"])
        stat_card(stats_frame, "Pending Orders", pending, THEME["warn"])
        stat_card(stats_frame, "Completed", completed, THEME["success"])

        counts_fr = tk.Frame(tab, bg=THEME["bg"])
        counts_fr.pack(fill="x", padx=18, pady=8)
        tk.Label(counts_fr, text=f"Canteen items: {len(self.app.data['canteen_items'])}", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b).pack(side="left", padx=10)
        tk.Label(counts_fr, text=f"Suvidha items: {len(self.app.data['suvidha_items'])}", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b).pack(side="left", padx=10)

    # Canteen Management
    def _canteen_tab(self):
        tab = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(tab, text="  Canteen Management  ")

        add_fr = tk.LabelFrame(tab, text="Add / Edit Item", bg=THEME["bg"], fg=THEME["text"])
        add_fr.pack(fill="x", padx=18, pady=12)
        frm = tk.Frame(add_fr, bg=THEME["bg"])
        frm.pack(padx=12, pady=12, fill="x")

        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=0, sticky="w")
        self.c_ent_name = ttk.Entry(frm, width=30); self.c_ent_name.grid(row=0, column=1, padx=8)
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=2, sticky="w")
        self.c_ent_price = ttk.Entry(frm, width=12); self.c_ent_price.grid(row=0, column=3, padx=8)
        tk.Button(frm, text="➕ Add Item", bg=THEME["accent"], fg="white", bd=0, command=lambda: self._add_canteen_item_modal()).grid(row=0, column=4, padx=8)

        list_fr = tk.Frame(tab, bg=THEME["bg"])
        list_fr.pack(fill="both", expand=True, padx=18, pady=12)
        cols = ("Name", "Price", "Available")
        self.canteen_tree = ttk.Treeview(list_fr, columns=cols, show="headings")
        for c in cols:
            self.canteen_tree.heading(c, text=c)
            self.canteen_tree.column(c, width=300 if c=="Name" else 120, anchor="w")
        self.canteen_tree.grid(row=0, column=0, sticky="nsew")
        v = ttk.Scrollbar(list_fr, orient="vertical", command=self.canteen_tree.yview); v.grid(row=0, column=1, sticky="ns")
        h = ttk.Scrollbar(list_fr, orient="horizontal", command=self.canteen_tree.xview); h.grid(row=1, column=0, sticky="ew")
        self.canteen_tree.configure(yscrollcommand=v.set, xscrollcommand=h.set)
        list_fr.grid_rowconfigure(0, weight=1); list_fr.grid_columnconfigure(0, weight=1)

        btn_fr = tk.Frame(tab, bg=THEME["bg"])
        btn_fr.pack(fill="x", padx=18, pady=8)
        tk.Button(btn_fr, text="✏️ Edit", bg=THEME["muted"], fg="white", bd=0, command=self._edit_canteen_item_modal).pack(side="left", padx=6)
        tk.Button(btn_fr, text="🔄 Toggle Availability", bg=THEME["warn"], fg="white", bd=0, command=self._toggle_canteen).pack(side="left", padx=6)
        tk.Button(btn_fr, text="🗑️ Delete", bg=THEME["danger"], fg="white", bd=0, command=self._del_canteen).pack(side="left", padx=6)

        self._refresh_canteen_tree()

    # Suvidha Management
    def _suvidha_tab(self):
        tab = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(tab, text="  Suvidha Management  ")

        top_lbl = tk.Label(tab, text="Campus Stationery & Book Shop", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2)
        top_lbl.pack(anchor="w", padx=18, pady=(12,4))

        add_fr = tk.LabelFrame(tab, text="Add / Edit Item", bg=THEME["bg"], fg=THEME["text"])
        add_fr.pack(fill="x", padx=18, pady=8)
        frm = tk.Frame(add_fr, bg=THEME["bg"])
        frm.pack(padx=12, pady=12, fill="x")

        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=0, sticky="w")
        self.s_ent_name = ttk.Entry(frm, width=26); self.s_ent_name.grid(row=0, column=1, padx=6)
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=2, sticky="w")
        self.s_ent_price = ttk.Entry(frm, width=10); self.s_ent_price.grid(row=0, column=3, padx=6)
        tk.Label(frm, text="Stock:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=4, sticky="w")
        self.s_ent_stock = ttk.Entry(frm, width=8); self.s_ent_stock.grid(row=0, column=5, padx=6)
        tk.Label(frm, text="Category:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=6, sticky="w")
        self.s_ent_cat = ttk.Combobox(frm, values=["Books","Notebooks","Pens","Other Stationery"], state="readonly", width=18); self.s_ent_cat.grid(row=0, column=7, padx=6); self.s_ent_cat.current(0)
        tk.Button(frm, text="➕ Add Item", bg=THEME["accent"], fg="white", bd=0, command=lambda: self._add_suvidha_item_modal()).grid(row=0, column=8, padx=6)

        list_fr = tk.Frame(tab, bg=THEME["bg"])
        list_fr.pack(fill="both", expand=True, padx=18, pady=8)
        cols = ("Name", "Price", "Stock", "Category")
        self.suvidha_tree = ttk.Treeview(list_fr, columns=cols, show="headings")
        for c in cols:
            self.suvidha_tree.heading(c, text=c)
            self.suvidha_tree.column(c, width=340 if c=="Name" else (120 if c!="Category" else 180), anchor="w")
        self.suvidha_tree.grid(row=0, column=0, sticky="nsew")
        v = ttk.Scrollbar(list_fr, orient="vertical", command=self.suvidha_tree.yview); v.grid(row=0, column=1, sticky="ns")
        h = ttk.Scrollbar(list_fr, orient="horizontal", command=self.suvidha_tree.xview); h.grid(row=1, column=0, sticky="ew")
        self.suvidha_tree.configure(yscrollcommand=v.set, xscrollcommand=h.set)
        list_fr.grid_rowconfigure(0, weight=1); list_fr.grid_columnconfigure(0, weight=1)

        btn_fr = tk.Frame(tab, bg=THEME["bg"]); btn_fr.pack(fill="x", padx=18, pady=8)
        tk.Button(btn_fr, text="✏️ Edit", bg=THEME["muted"], fg="white", bd=0, command=self._edit_suvidha_item_modal).pack(side="left", padx=6)
        tk.Button(btn_fr, text="🧮 Update Stock", bg=THEME["accent"], fg="white", bd=0, command=self._update_stock).pack(side="left", padx=6)
        tk.Button(btn_fr, text="🗑️ Delete", bg=THEME["danger"], fg="white", bd=0, command=self._del_suvidha).pack(side="left", padx=6)

        self._refresh_suvidha_tree()

    # Orders Tab (split sections + refresh)
    def _orders_tab(self):
        tab = tk.Frame(self.nb, bg=THEME["bg"])
        self.nb.add(tab, text="  Orders  ")

        header = tk.Frame(tab, bg=THEME["bg"])
        header.pack(fill="x", padx=18, pady=8)
        tk.Label(header, text="Orders Management", bg=THEME["bg"], fg=THEME["text"], font=self.app.font_h2).pack(side="left")
        refresh_btn = tk.Button(header, text="🔄 Refresh Orders", bg=THEME["accent"], fg="white", bd=0, command=self._refresh_orders_section)
        refresh_btn.pack(side="right")

        # Canteen Orders
        can_label = tk.Label(tab, text="Canteen Orders", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b)
        can_label.pack(anchor="w", padx=18, pady=(12,4))
        self.can_container = tk.Frame(tab, bg=THEME["bg"])
        self.can_container.pack(fill="both", expand=True, padx=18, pady=(0,12))
        self._render_order_section(self.can_container, "canteen")

        # Suvidha Orders
        suv_label = tk.Label(tab, text="Suvidha Orders", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b)
        suv_label.pack(anchor="w", padx=18, pady=(12,4))
        self.suv_container = tk.Frame(tab, bg=THEME["bg"])
        self.suv_container.pack(fill="both", expand=True, padx=18, pady=(0,12))
        self._render_order_section(self.suv_container, "suvidha")

    def _refresh_orders_section(self):
        # reload from disk then re-render both sections
        self.app.data = DataStore(DATA_FILE)  # reload fresh
        self._render_order_section(self.can_container, "canteen")
        self._render_order_section(self.suv_container, "suvidha")
        show_toast(self.app.root, "🔄 Orders refreshed")

    # helper to render orders by type into parent frame
    def _render_order_section(self, parent, otype):
        for w in parent.winfo_children(): w.destroy()
        relevant = [o for o in reversed(self.app.data["orders"]) if o.get("type") == otype]
        if not relevant:
            tk.Label(parent, text="No orders.", bg=THEME["bg"], fg=THEME["muted"], font=self.app.font_b).pack(pady=12)
            return
        for order in relevant:
            card = tk.Frame(parent, bg=THEME["card"], pady=8, padx=10)
            card.pack(fill="x", pady=8)
            top = tk.Frame(card, bg=THEME["card"])
            top.pack(fill="x")
            tk.Label(top, text=f"Order #{order.get('id')}", bg=THEME["card"], fg=THEME["text"], font=self.app.font_h3).pack(side="left")
            status = order.get("status","pending")
            color = THEME["warn"] if status=="pending" else THEME["success"]
            tk.Label(top, text=("⏳ Pending" if status=="pending" else "✓ Completed"), bg=color, fg="white", padx=8).pack(side="right")

            info = tk.Frame(card, bg=THEME["card"])
            info.pack(fill="x", pady=(8,4))
            tk.Label(info, text=f"Time: {order.get('time')}", bg=THEME["card"], fg=THEME["muted"], font=self.app.font_b).pack(side="left", padx=6)
            tk.Label(info, text=f"Total: ₹{order.get('total')}", bg=THEME["card"], fg=THEME["accent"], font=self.app.font_h3).pack(side="right", padx=6)

            if order.get("delivery"):
                d = order.get("delivery_info", {})
                tk.Label(card, text=f"Delivery: Yes ({d.get('class','-')} - Roll {d.get('roll','-')} @ {d.get('time','-')})", bg=THEME["card"], fg=THEME["muted"], font=self.app.font_b).pack(anchor="w", padx=6)

            if order.get("items"):
                items_frame = tk.Frame(card, bg="#0b1220")
                items_frame.pack(fill="x", padx=6, pady=(8,6))
                tk.Label(items_frame, text="Items:", bg="#0b1220", fg=THEME["text"], font=self.app.font_b).pack(anchor="w")
                for it in order["items"]:
                    tk.Label(items_frame, text=f" • {it.get('name')} × {it.get('qty')} — ₹{it.get('price')*it.get('qty')}", bg="#0b1220", fg=THEME["muted"], font=self.app.font_sm).pack(anchor="w", padx=8)

            def make_toggle(o=order):
                def toggle():
                    try:
                        idx = next(i for i, od in enumerate(self.app.data["orders"]) if od.get("id") == o.get("id"))
                        cur = self.app.data["orders"][idx].get("status","pending")
                        self.app.data["orders"][idx]["status"] = "completed" if cur=="pending" else "pending"
                        self.app.data.save()
                        # refresh just the orders sections
                        self._render_order_section(self.can_container, "canteen")
                        self._render_order_section(self.suv_container, "suvidha")
                        show_toast(self.app.root, "✅ Order status updated")
                    except Exception:
                        messagebox.showerror("Error", "Unable to update order.")
                return toggle

            if order.get("status") == "pending":
                tk.Button(card, text="Mark as Completed", bg=THEME["success"], fg="white", bd=0, command=make_toggle()).pack(anchor="e", pady=6)

    # ---------- Canteen CRUD helpers (modal patterns) ----------
    def _refresh_canteen_tree(self):
        for i in self.canteen_tree.get_children(): self.canteen_tree.delete(i)
        for it in self.app.data["canteen_items"]:
            avail = "✓ Yes" if it.get("available", True) else "✗ No"
            self.canteen_tree.insert("", "end", values=(it.get("name",""), f"₹{it.get('price',0)}", avail))

    def _add_canteen_item_modal(self):
        # modal add dialog (ensures it stays on top)
        dlg = tk.Toplevel(self.win)
        dlg.title("Add Canteen Item")
        dlg.configure(bg=THEME["bg"])
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.focus_force()
        center_window(dlg, 480, 200)
        frm = tk.Frame(dlg, bg=THEME["bg"]); frm.pack(padx=16, pady=12, fill="both", expand=True)
        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0, column=0, sticky="w")
        name_ent = ttk.Entry(frm, width=36); name_ent.grid(row=0, column=1, padx=8, pady=6)
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=1, column=0, sticky="w")
        price_ent = ttk.Entry(frm, width=12); price_ent.grid(row=1, column=1, sticky="w", padx=8, pady=6)
        def do_add():
            name = name_ent.get().strip(); price = safe_float(price_ent.get())
            if not name:
                messagebox.showerror("Error", "Name required"); return
            if price <= 0:
                messagebox.showerror("Error", "Price must be > 0"); return
            self.app.data["canteen_items"].append({"name": name, "price": price, "available": True})
            self.app.data.save()
            self._refresh_canteen_tree()
            show_toast(self.app.root, "✅ Canteen item added")
            dlg.destroy()
        tk.Button(frm, text="Add Item", bg=THEME["accent"], fg="white", bd=0, command=do_add).grid(row=2, column=0, columnspan=2, pady=12)
        dlg.wait_window()

    def _get_selected_index_tree(self, tree):
        sel = tree.selection()
        if not sel: return None
        return tree.index(sel[0])

    def _edit_canteen_item_modal(self):
        idx = self._get_selected_index_tree(self.canteen_tree)
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item to edit"); return
        it = self.app.data["canteen_items"][idx]
        dlg = tk.Toplevel(self.win)
        dlg.transient(self.win); dlg.grab_set(); dlg.focus_force()
        dlg.title("Edit Canteen Item"); dlg.configure(bg=THEME["bg"])
        center_window(dlg, 480, 240)
        frm = tk.Frame(dlg, bg=THEME["bg"]); frm.pack(padx=16, pady=12)
        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0,col=0,sticky="w")
        n = ttk.Entry(frm, width=36); n.grid(row=0,col=1,padx=8); n.insert(0, it.get("name",""))
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=1,col=0,sticky="w")
        p = ttk.Entry(frm, width=12); p.grid(row=1,col=1,padx=8); p.insert(0, str(it.get("price",0)))
        def save():
            name = n.get().strip(); price = safe_float(p.get())
            if not name: messagebox.showerror("Error","Name required"); return
            if price <= 0: messagebox.showerror("Error","Price must be > 0"); return
            self.app.data["canteen_items"][idx]["name"]=name; self.app.data["canteen_items"][idx]["price"]=price
            self.app.data.save(); self._refresh_canteen_tree(); show_toast(self.app.root, "✅ Item updated"); dlg.destroy()
        tk.Button(frm, text="Save", bg=THEME["accent"], fg="white", bd=0, command=save).grid(row=2,col=0,colspan=2,pady=12)
        dlg.wait_window()

    def _toggle_canteen(self):
        idx = self._get_selected_index_tree(self.canteen_tree)
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item"); return
        items = self.app.data["canteen_items"]
        if 0 <= idx < len(items):
            items[idx]["available"] = not items[idx].get("available", True)
            self.app.data.save()
            self._refresh_canteen_tree()
            show_toast(self.app.root, "🔄 Availability toggled")
        else:
            messagebox.showerror("Error", "Invalid selection")

    def _del_canteen(self):
        idx = self._get_selected_index_tree(self.canteen_tree)
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item"); return
        items = self.app.data["canteen_items"]
        if 0 <= idx < len(items):
            name = items[idx].get("name","")
            if messagebox.askyesno("Confirm Delete", f"Delete '{name}'?"):
                del items[idx]; self.app.data.save(); self._refresh_canteen_tree(); show_toast(self.app.root, "🗑️ Item deleted")
        else:
            messagebox.showerror("Error", "Invalid selection")

    # ---------- Suvidha CRUD helpers (modal patterns) ----------
    def _refresh_suvidha_tree(self):
        for i in self.suvidha_tree.get_children(): self.suvidha_tree.delete(i)
        for it in self.app.data["suvidha_items"]:
            self.suvidha_tree.insert("", "end", values=(it.get("name",""), f"₹{it.get('price',0)}", it.get("stock",0), it.get("category","")))

    def _add_suvidha_item_modal(self):
        dlg = tk.Toplevel(self.win)
        dlg.title("Add Suvidha Item"); dlg.configure(bg=THEME["bg"])
        dlg.transient(self.win); dlg.grab_set(); dlg.focus_force()
        center_window(dlg, 560, 260)
        frm = tk.Frame(dlg, bg=THEME["bg"]); frm.pack(padx=16, pady=12, fill="both", expand=True)
        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0,col=0,sticky="w")
        n = ttk.Entry(frm, width=36); n.grid(row=0,col=1,padx=8)
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=1,col=0,sticky="w")
        p = ttk.Entry(frm, width=12); p.grid(row=1,col=1,padx=8)
        tk.Label(frm, text="Stock:", bg=THEME["bg"], fg=THEME["text"]).grid(row=2,col=0,sticky="w")
        s = ttk.Entry(frm, width=12); s.grid(row=2,col=1,padx=8)
        tk.Label(frm, text="Category:", bg=THEME["bg"], fg=THEME["text"]).grid(row=3,col=0,sticky="w")
        c = ttk.Combobox(frm, values=["Books","Notebooks","Pens","Other Stationery"], state="readonly", width=24); c.grid(row=3,col=1,padx=8); c.current(0)
        def add():
            name = n.get().strip(); price = safe_float(p.get()); stock = safe_int(s.get()); cat = c.get()
            if not name: messagebox.showerror("Error","Name required"); return
            if price <= 0: messagebox.showerror("Error","Price must be > 0"); return
            if stock < 0: messagebox.showerror("Error","Stock must be >= 0"); return
            self.app.data["suvidha_items"].append({"name": name, "price": price, "stock": stock, "category": cat})
            self.app.data.save(); self._refresh_suvidha_tree(); show_toast(self.app.root, "✅ Suvidha item added"); dlg.destroy()
        tk.Button(frm, text="Add Item", bg=THEME["accent"], fg="white", bd=0, command=add).grid(row=4,column=0,columnspan=2,pady=12)
        dlg.wait_window()

    def _get_selected_index_suvidha(self):
        sel = self.suvidha_tree.selection()
        if not sel: return None
        return self.suvidha_tree.index(sel[0])

    def _edit_suvidha_item_modal(self):
        idx = self._get_selected_index_suvidha()
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item to edit"); return
        it = self.app.data["suvidha_items"][idx]
        dlg = tk.Toplevel(self.win); dlg.transient(self.win); dlg.grab_set(); dlg.focus_force()
        dlg.title("Edit Suvidha Item"); dlg.configure(bg=THEME["bg"])
        center_window(dlg, 560, 300)
        frm = tk.Frame(dlg, bg=THEME["bg"]); frm.pack(padx=16, pady=12)
        tk.Label(frm, text="Name:", bg=THEME["bg"], fg=THEME["text"]).grid(row=0,col=0,sticky="w")
        n = ttk.Entry(frm, width=36); n.grid(row=0,col=1,padx=8); n.insert(0, it.get("name",""))
        tk.Label(frm, text="Price (₹):", bg=THEME["bg"], fg=THEME["text"]).grid(row=1,col=0,sticky="w")
        p = ttk.Entry(frm, width=12); p.grid(row=1,col=1,padx=8); p.insert(0, str(it.get("price",0)))
        tk.Label(frm, text="Stock:", bg=THEME["bg"], fg=THEME["text"]).grid(row=2,col=0,sticky="w")
        s = ttk.Entry(frm, width=12); s.grid(row=2,col=1,padx=8); s.insert(0, str(it.get("stock",0)))
        tk.Label(frm, text="Category:", bg=THEME["bg"], fg=THEME["text"]).grid(row=3,col=0,sticky="w")
        c = ttk.Combobox(frm, values=["Books","Notebooks","Pens","Other Stationery"], state="readonly", width=24); c.grid(row=3,col=1,padx=8)
        try:
            c.current(["Books","Notebooks","Pens","Other Stationery"].index(it.get("category","Books")))
        except Exception:
            c.current(0)
        def save():
            name = n.get().strip(); price = safe_float(p.get()); stock = safe_int(s.get()); cat = c.get()
            if not name: messagebox.showerror("Error","Name required"); return
            if price <= 0: messagebox.showerror("Error","Price must be > 0"); return
            if stock < 0: messagebox.showerror("Error","Stock >= 0"); return
            self.app.data["suvidha_items"][idx].update({"name": name, "price": price, "stock": stock, "category": cat})
            self.app.data.save(); self._refresh_suvidha_tree(); show_toast(self.app.root, "✅ Item updated"); dlg.destroy()
        tk.Button(frm, text="Save", bg=THEME["accent"], fg="white", bd=0, command=save).grid(row=4,col=0,colspan=2,pady=12)
        dlg.wait_window()

    def _update_stock(self):
        idx = self._get_selected_index_suvidha()
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item"); return
        curr = self.app.data["suvidha_items"][idx].get("stock",0)
        name = self.app.data["suvidha_items"][idx].get("name","")
        new = simpledialog.askinteger("Update Stock", f"Item: {name}\nCurrent: {curr}\nEnter new stock:", initialvalue=curr, minvalue=0)
        if new is not None:
            self.app.data["suvidha_items"][idx]["stock"] = new
            self.app.data.save()
            self._refresh_suvidha_tree(); show_toast(self.app.root, "✅ Stock updated")

    def _del_suvidha(self):
        idx = self._get_selected_index_suvidha()
        if idx is None:
            messagebox.showwarning("No Selection", "Select an item"); return
        items = self.app.data["suvidha_items"]
        if 0 <= idx < len(items):
            name = items[idx].get("name","")
            if messagebox.askyesno("Confirm Delete", f"Delete '{name}'?"):
                del items[idx]; self.app.data.save(); self._refresh_suvidha_tree(); show_toast(self.app.root, "🗑️ Item deleted")
        else:
            messagebox.showerror("Error", "Invalid selection")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = YrushApp(root)
    root.mainloop()
