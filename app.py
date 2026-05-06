"""
Grocery Shop Management System - Tkinter + MySQL single-file app
Save as app.py and run: python app.py
Requires: mysql-connector-python
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

# --- DB config: set these to match your MySQL server ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root123",
    "database": "grocery_db",
}

# --- DB helper functions ---
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("DB Error", f"Cannot connect to database:\n{e}")
        raise

# Worker CRUD
def worker_add(name, designation, salary, hiredate, sex, department):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Worker (name, designation, salary, hireDate, sex, department) VALUES (%s,%s,%s,%s,%s,%s)",
        (name, designation, salary, hiredate, sex, department),
    )
    conn.commit()
    cur.close()
    conn.close()

def worker_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT empID, name, designation, salary, hireDate, sex, department FROM Worker")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def worker_search(emp_id=None, name=None):
    conn = get_connection()
    cur = conn.cursor()
    if emp_id:
        cur.execute("SELECT * FROM Worker WHERE empID=%s", (emp_id,))
    else:
        cur.execute("SELECT * FROM Worker WHERE name LIKE %s", (f"%{name}%",))
    r = cur.fetchall()
    cur.close()
    conn.close()
    return r

def worker_update(empID, name, designation, salary, hiredate, sex, department):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Worker SET name=%s, designation=%s, salary=%s, hireDate=%s, sex=%s, department=%s WHERE empID=%s",
        (name, designation, salary, hiredate, sex, department, empID),
    )
    conn.commit()
    cur.close()
    conn.close()

def worker_delete(empID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Worker WHERE empID=%s", (empID,))
    conn.commit()
    cur.close()
    conn.close()

# Product CRUD
def product_add(name, type_, brand, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Product (name, type, brand, price) VALUES (%s,%s,%s,%s)",
                (name, type_, brand, price))
    conn.commit()
    cur.close()
    conn.close()

def product_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT productID, name, type, brand, price FROM Product")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def product_search(pid=None, name=None):
    conn = get_connection()
    cur = conn.cursor()
    if pid:
        cur.execute("SELECT * FROM Product WHERE productID=%s", (pid,))
    else:
        cur.execute("SELECT * FROM Product WHERE name LIKE %s", (f"%{name}%",))
    r = cur.fetchall()
    cur.close()
    conn.close()
    return r

def product_update(productID, name, type_, brand, price):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Product SET name=%s, type=%s, brand=%s, price=%s WHERE productID=%s",
                (name, type_, brand, price, productID))
    conn.commit()
    cur.close()
    conn.close()

def product_delete(productID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Product WHERE productID=%s", (productID,))
    conn.commit()
    cur.close()
    conn.close()

# Customer CRUD
def customer_add(name, address, email, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Customer (name, address, email, phone) VALUES (%s,%s,%s,%s)",
                (name, address, email, phone))
    conn.commit()
    cur.close()
    conn.close()

def customer_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT customerID, name, address, email, phone FROM Customer")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def customer_search(cid=None, name=None):
    conn = get_connection()
    cur = conn.cursor()
    if cid:
        cur.execute("SELECT * FROM Customer WHERE customerID=%s", (cid,))
    else:
        cur.execute("SELECT * FROM Customer WHERE name LIKE %s", (f"%{name}%",))
    r = cur.fetchall()
    cur.close()
    conn.close()
    return r

def customer_update(customerID, name, address, email, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Customer SET name=%s, address=%s, email=%s, phone=%s WHERE customerID=%s",
                (name, address, email, phone, customerID))
    conn.commit()
    cur.close()
    conn.close()

def customer_delete(customerID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Customer WHERE customerID=%s", (customerID,))
    conn.commit()
    cur.close()
    conn.close()

# Billing
def billing_create(bill_date, customerID, items):
    """
    items: list of dicts: [{'productID': id, 'quantity': q, 'unitPrice': price}, ...]
    returns billID
    """
    conn = get_connection()
    cur = conn.cursor()
    total = sum(item['quantity'] * item['unitPrice'] for item in items)
    cur.execute("INSERT INTO Billing (bill_date, customerID, totalAmount) VALUES (%s,%s,%s)",
                (bill_date, customerID, total))
    billID = cur.lastrowid
    for it in items:
        lineTotal = it['quantity'] * it['unitPrice']
        cur.execute(
            "INSERT INTO BillingItem (billID, productID, quantity, unitPrice, lineTotal) VALUES (%s,%s,%s,%s,%s)",
            (billID, it['productID'], it['quantity'], it['unitPrice'], lineTotal),
        )
    conn.commit()
    cur.close()
    conn.close()
    return billID

def billing_get(billID):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT billID, bill_date, customerID, totalAmount FROM Billing WHERE billID=%s", (billID,))
    bill = cur.fetchone()
    cur.execute("SELECT productID, quantity, unitPrice, lineTotal FROM BillingItem WHERE billID=%s", (billID,))
    items = cur.fetchall()
    cur.close()
    conn.close()
    return bill, items

# --- Tkinter GUI ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grocery Shop Management System")
        self.geometry("700x420")
        self.resizable(False, False)

        self.create_landing()

    def clear_frame(self):
        for w in self.winfo_children():
            w.destroy()

    def create_landing(self):
        self.clear_frame()
        title = tk.Label(self, text="Grocery Shop Management System", font=("Helvetica", 18, "bold"))
        title.pack(pady=20)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        b_worker = tk.Button(frame, text="Worker Details", width=20, command=self.open_worker_menu)
        b_worker.grid(row=0, column=0, padx=10, pady=8)

        b_product = tk.Button(frame, text="Product Details", width=20, command=self.open_product_menu)
        b_product.grid(row=0, column=1, padx=10, pady=8)

        b_customer = tk.Button(frame, text="Customer Details", width=20, command=self.open_customer_menu)
        b_customer.grid(row=1, column=0, padx=10, pady=8)

        b_billing = tk.Button(frame, text="Billing", width=20, command=self.open_billing_menu)
        b_billing.grid(row=1, column=1, padx=10, pady=8)

        b_exit = tk.Button(self, text="Exit", width=10, command=self.quit)
        b_exit.pack(pady=20)

    # ---------- Worker menu ----------
    def open_worker_menu(self):
        self.clear_frame()
        tk.Label(self, text="Worker Module", font=("Helvetica", 16)).pack(pady=10)
        f = tk.Frame(self)
        f.pack(pady=10)
        tk.Button(f, text="Add Worker", width=20, command=self.worker_add_window).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(f, text="List Workers", width=20, command=self.worker_list_window).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(f, text="Search Worker", width=20, command=self.worker_search_window).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(f, text="Update Worker", width=20, command=self.worker_update_window).grid(row=1, column=1, padx=8, pady=8)
        tk.Button(f, text="Delete Worker", width=20, command=self.worker_delete_window).grid(row=2, column=0, padx=8, pady=8)
        tk.Button(self, text="Back", command=self.create_landing).pack(pady=12)

    def worker_add_window(self):
        win = tk.Toplevel(self)
        win.title("Add Worker")
        labels = ["Name", "Designation", "Salary", "Hire Date (YYYY-MM-DD)", "Sex", "Department"]
        entries = {}
        for i, lab in enumerate(labels):
            tk.Label(win, text=lab).grid(row=i, column=0, padx=6, pady=6)
            e = tk.Entry(win, width=30)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries[lab] = e

        def do_add():
            try:
                name = entries["Name"].get()
                designation = entries["Designation"].get()
                salary = float(entries["Salary"].get() or 0)
                hiredate = entries["Hire Date (YYYY-MM-DD)"].get() or None
                sex = entries["Sex"].get()
                department = entries["Department"].get()
                worker_add(name, designation, salary, hiredate, sex, department)
                messagebox.showinfo("Success", "Worker added")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Add", command=do_add).grid(row=len(labels), column=0, pady=8)
        tk.Button(win, text="Close", command=win.destroy).grid(row=len(labels), column=1, pady=8)

    def worker_list_window(self):
        rows = worker_list()
        win = tk.Toplevel(self)
        win.title("List Workers")
        cols = ("empID", "name", "designation", "salary", "hireDate", "sex", "department")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True)

    def worker_search_window(self):
        win = tk.Toplevel(self)
        win.title("Search Worker")
        tk.Label(win, text="Search by ID (leave blank to search by name):").pack(pady=6)
        entry = tk.Entry(win, width=30)
        entry.pack(pady=6)

        def do_search():
            key = entry.get()
            if key.isdigit():
                res = worker_search(emp_id=int(key))
            else:
                res = worker_search(name=key)
            if not res:
                messagebox.showinfo("No results", "No worker found")
                return
            out = "\n".join(str(r) for r in res)
            messagebox.showinfo("Results", out)

        tk.Button(win, text="Search", command=do_search).pack(pady=6)

    def worker_update_window(self):
        win = tk.Toplevel(self)
        win.title("Update Worker")
        tk.Label(win, text="Enter empID to update:").grid(row=0, column=0, padx=6, pady=6)
        id_entry = tk.Entry(win)
        id_entry.grid(row=0, column=1, padx=6, pady=6)

        def load():
            v = id_entry.get()
            if not v.isdigit():
                messagebox.showerror("Error", "empID must be numeric")
                return
            res = worker_search(emp_id=int(v))
            if not res:
                messagebox.showerror("Not found", "No worker with that ID")
                return
            data = res[0]
            form_window(data)

        tk.Button(win, text="Load", command=load).grid(row=0, column=2, padx=6, pady=6)

        def form_window(data):
            f = tk.Toplevel(win)
            f.title("Edit Worker")
            labels = ["Name", "Designation", "Salary", "Hire Date (YYYY-MM-DD)", "Sex", "Department"]
            entries = {}
            for i, lab in enumerate(labels):
                tk.Label(f, text=lab).grid(row=i, column=0, padx=6, pady=6)
                e = tk.Entry(f, width=30)
                e.grid(row=i, column=1, padx=6, pady=6)
                entries[lab] = e
            # data: empID, name, designation, salary, hireDate, sex, department
            empID = data[0]
            entries["Name"].insert(0, data[1] or "")
            entries["Designation"].insert(0, data[2] or "")
            entries["Salary"].insert(0, str(data[3] or ""))
            entries["Hire Date (YYYY-MM-DD)"].insert(0, str(data[4] or ""))
            entries["Sex"].insert(0, data[5] or "")
            entries["Department"].insert(0, data[6] or "")

            def do_update():
                try:
                    name = entries["Name"].get()
                    designation = entries["Designation"].get()
                    salary = float(entries["Salary"].get() or 0)
                    hiredate = entries["Hire Date (YYYY-MM-DD)"].get() or None
                    sex = entries["Sex"].get()
                    department = entries["Department"].get()
                    worker_update(empID, name, designation, salary, hiredate, sex, department)
                    messagebox.showinfo("Success", "Worker updated")
                    f.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            tk.Button(f, text="Update", command=do_update).grid(row=len(labels), column=0, pady=8)
            tk.Button(f, text="Close", command=f.destroy).grid(row=len(labels), column=1, pady=8)

    def worker_delete_window(self):
        v = simpledialog.askstring("Delete Worker", "Enter empID to delete:")
        if not v:
            return
        if not v.isdigit():
            messagebox.showerror("Error", "empID must be numeric")
            return
        if messagebox.askyesno("Confirm", f"Delete worker with empID {v}?"):
            try:
                worker_delete(int(v))
                messagebox.showinfo("Deleted", "Worker deleted")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Product menu ----------
    def open_product_menu(self):
        self.clear_frame()
        tk.Label(self, text="Product Module", font=("Helvetica", 16)).pack(pady=10)
        f = tk.Frame(self)
        f.pack(pady=10)
        tk.Button(f, text="Add Product", width=20, command=self.product_add_window).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(f, text="List Products", width=20, command=self.product_list_window).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(f, text="Search Product", width=20, command=self.product_search_window).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(f, text="Update Product", width=20, command=self.product_update_window).grid(row=1, column=1, padx=8, pady=8)
        tk.Button(f, text="Delete Product", width=20, command=self.product_delete_window).grid(row=2, column=0, padx=8, pady=8)
        tk.Button(self, text="Back", command=self.create_landing).pack(pady=12)

    def product_add_window(self):
        win = tk.Toplevel(self)
        win.title("Add Product")
        labels = ["Name", "Type", "Brand", "Price"]
        entries = {}
        for i, lab in enumerate(labels):
            tk.Label(win, text=lab).grid(row=i, column=0, padx=6, pady=6)
            e = tk.Entry(win, width=30)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries[lab] = e

        def do_add():
            try:
                name = entries["Name"].get()
                type_ = entries["Type"].get()
                brand = entries["Brand"].get()
                price = float(entries["Price"].get() or 0)
                product_add(name, type_, brand, price)
                messagebox.showinfo("Success", "Product added")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Add", command=do_add).grid(row=len(labels), column=0, pady=8)
        tk.Button(win, text="Close", command=win.destroy).grid(row=len(labels), column=1, pady=8)

    def product_list_window(self):
        rows = product_list()
        win = tk.Toplevel(self)
        win.title("List Products")
        cols = ("productID", "name", "type", "brand", "price")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True)

    def product_search_window(self):
        win = tk.Toplevel(self)
        win.title("Search Product")
        tk.Label(win, text="Search by ID (leave blank to search by name):").pack(pady=6)
        entry = tk.Entry(win, width=30)
        entry.pack(pady=6)

        def do_search():
            key = entry.get()
            if key.isdigit():
                res = product_search(pid=int(key))
            else:
                res = product_search(name=key)
            if not res:
                messagebox.showinfo("No results", "No product found")
                return
            out = "\n".join(str(r) for r in res)
            messagebox.showinfo("Results", out)

        tk.Button(win, text="Search", command=do_search).pack(pady=6)

    def product_update_window(self):
        win = tk.Toplevel(self)
        win.title("Update Product")
        tk.Label(win, text="Enter productID to update:").grid(row=0, column=0, padx=6, pady=6)
        id_entry = tk.Entry(win)
        id_entry.grid(row=0, column=1, padx=6, pady=6)

        def load():
            v = id_entry.get()
            if not v.isdigit():
                messagebox.showerror("Error", "productID must be numeric")
                return
            res = product_search(pid=int(v))
            if not res:
                messagebox.showerror("Not found", "No product with that ID")
                return
            data = res[0]
            form_window(data)

        tk.Button(win, text="Load", command=load).grid(row=0, column=2, padx=6, pady=6)

        def form_window(data):
            f = tk.Toplevel(win)
            f.title("Edit Product")
            labels = ["Name", "Type", "Brand", "Price"]
            entries = {}
            for i, lab in enumerate(labels):
                tk.Label(f, text=lab).grid(row=i, column=0, padx=6, pady=6)
                e = tk.Entry(f, width=30)
                e.grid(row=i, column=1, padx=6, pady=6)
                entries[lab] = e
            productID = data[0]
            entries["Name"].insert(0, data[1] or "")
            entries["Type"].insert(0, data[2] or "")
            entries["Brand"].insert(0, data[3] or "")
            entries["Price"].insert(0, str(data[4] or ""))

            def do_update():
                try:
                    name = entries["Name"].get()
                    type_ = entries["Type"].get()
                    brand = entries["Brand"].get()
                    price = float(entries["Price"].get() or 0)
                    product_update(productID, name, type_, brand, price)
                    messagebox.showinfo("Success", "Product updated")
                    f.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            tk.Button(f, text="Update", command=do_update).grid(row=len(labels), column=0, pady=8)
            tk.Button(f, text="Close", command=f.destroy).grid(row=len(labels), column=1, pady=8)

    def product_delete_window(self):
        v = simpledialog.askstring("Delete Product", "Enter productID to delete:")
        if not v:
            return
        if not v.isdigit():
            messagebox.showerror("Error", "productID must be numeric")
            return
        if messagebox.askyesno("Confirm", f"Delete product with productID {v}?"):
            try:
                product_delete(int(v))
                messagebox.showinfo("Deleted", "Product deleted")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Customer menu ----------
    def open_customer_menu(self):
        self.clear_frame()
        tk.Label(self, text="Customer Module", font=("Helvetica", 16)).pack(pady=10)
        f = tk.Frame(self)
        f.pack(pady=10)
        tk.Button(f, text="Add Customer", width=20, command=self.customer_add_window).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(f, text="List Customers", width=20, command=self.customer_list_window).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(f, text="Search Customer", width=20, command=self.customer_search_window).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(f, text="Update Customer", width=20, command=self.customer_update_window).grid(row=1, column=1, padx=8, pady=8)
        tk.Button(f, text="Delete Customer", width=20, command=self.customer_delete_window).grid(row=2, column=0, padx=8, pady=8)
        tk.Button(self, text="Back", command=self.create_landing).pack(pady=12)

    def customer_add_window(self):
        win = tk.Toplevel(self)
        win.title("Add Customer")
        labels = ["Name", "Address", "Email", "Phone"]
        entries = {}
        for i, lab in enumerate(labels):
            tk.Label(win, text=lab).grid(row=i, column=0, padx=6, pady=6)
            e = tk.Entry(win, width=40)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries[lab] = e

        def do_add():
            try:
                name = entries["Name"].get()
                address = entries["Address"].get()
                email = entries["Email"].get()
                phone = entries["Phone"].get()
                customer_add(name, address, email, phone)
                messagebox.showinfo("Success", "Customer added")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Add", command=do_add).grid(row=len(labels), column=0, pady=8)
        tk.Button(win, text="Close", command=win.destroy).grid(row=len(labels), column=1, pady=8)

    def customer_list_window(self):
        rows = customer_list()
        win = tk.Toplevel(self)
        win.title("List Customers")
        cols = ("customerID", "name", "address", "email", "phone")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.pack(fill="both", expand=True)

    def customer_search_window(self):
        win = tk.Toplevel(self)
        win.title("Search Customer")
        tk.Label(win, text="Search by ID (leave blank to search by name):").pack(pady=6)
        entry = tk.Entry(win, width=30)
        entry.pack(pady=6)

        def do_search():
            key = entry.get()
            if key.isdigit():
                res = customer_search(cid=int(key))
            else:
                res = customer_search(name=key)
            if not res:
                messagebox.showinfo("No results", "No customer found")
                return
            out = "\n".join(str(r) for r in res)
            messagebox.showinfo("Results", out)

        tk.Button(win, text="Search", command=do_search).pack(pady=6)

    def customer_update_window(self):
        win = tk.Toplevel(self)
        win.title("Update Customer")
        tk.Label(win, text="Enter customerID to update:").grid(row=0, column=0, padx=6, pady=6)
        id_entry = tk.Entry(win)
        id_entry.grid(row=0, column=1, padx=6, pady=6)

        def load():
            v = id_entry.get()
            if not v.isdigit():
                messagebox.showerror("Error", "customerID must be numeric")
                return
            res = customer_search(cid=int(v))
            if not res:
                messagebox.showerror("Not found", "No customer with that ID")
                return
            data = res[0]
            form_window(data)

        tk.Button(win, text="Load", command=load).grid(row=0, column=2, padx=6, pady=6)

        def form_window(data):
            f = tk.Toplevel(win)
            f.title("Edit Customer")
            labels = ["Name", "Address", "Email", "Phone"]
            entries = {}
            for i, lab in enumerate(labels):
                tk.Label(f, text=lab).grid(row=i, column=0, padx=6, pady=6)
                e = tk.Entry(f, width=40)
                e.grid(row=i, column=1, padx=6, pady=6)
                entries[lab] = e
            customerID = data[0]
            entries["Name"].insert(0, data[1] or "")
            entries["Address"].insert(0, data[2] or "")
            entries["Email"].insert(0, data[3] or "")
            entries["Phone"].insert(0, data[4] or "")

            def do_update():
                try:
                    name = entries["Name"].get()
                    address = entries["Address"].get()
                    email = entries["Email"].get()
                    phone = entries["Phone"].get()
                    customer_update(customerID, name, address, email, phone)
                    messagebox.showinfo("Success", "Customer updated")
                    f.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            tk.Button(f, text="Update", command=do_update).grid(row=len(labels), column=0, pady=8)
            tk.Button(f, text="Close", command=f.destroy).grid(row=len(labels), column=1, pady=8)

    def customer_delete_window(self):
        v = simpledialog.askstring("Delete Customer", "Enter customerID to delete:")
        if not v:
            return
        if not v.isdigit():
            messagebox.showerror("Error", "customerID must be numeric")
            return
        if messagebox.askyesno("Confirm", f"Delete customer with customerID {v}?"):
            try:
                customer_delete(int(v))
                messagebox.showinfo("Deleted", "Customer deleted")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ---------- Billing menu ----------
    def open_billing_menu(self):
        self.clear_frame()
        tk.Label(self, text="Billing Module", font=("Helvetica", 16)).pack(pady=10)
        f = tk.Frame(self)
        f.pack(pady=10)
        tk.Button(f, text="Create Bill", width=20, command=self.billing_create_window).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(f, text="View Bill", width=20, command=self.billing_view_window).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(self, text="Back", command=self.create_landing).pack(pady=12)

    def billing_create_window(self):
        win = tk.Toplevel(self)
        win.title("Create Bill")

        # Customer selection
        tk.Label(win, text="Select Customer (ID):").grid(row=0, column=0, padx=6, pady=6)
        custs = customer_list()
        cust_map = {str(c[0]) + " - " + c[1]: c[0] for c in custs}
        cust_combo = ttk.Combobox(win, values=list(cust_map.keys()), width=40)
        cust_combo.grid(row=0, column=1, padx=6, pady=6)

        # products area
        tk.Label(win, text="Products (Select and add quantity):").grid(row=1, column=0, columnspan=2)
        prod_rows = product_list()
        prod_map = {f"{p[0]} - {p[1]} (₹{p[4]})": (p[0], p[4]) for p in prod_rows}
        prod_combo = ttk.Combobox(win, values=list(prod_map.keys()), width=50)
        prod_combo.grid(row=2, column=0, padx=6, pady=6, columnspan=2)

        qty_label = tk.Label(win, text="Qty")
        qty_label.grid(row=3, column=0, padx=6, pady=6)
        qty_entry = tk.Entry(win, width=10)
        qty_entry.grid(row=3, column=1, padx=6, pady=6, sticky='w')

        items = []  # list of dicts

        tree_cols = ("productID", "name", "qty", "unitPrice", "lineTotal")
        tree = ttk.Treeview(win, columns=tree_cols, show="headings", height=6)
        for c in tree_cols:
            tree.heading(c, text=c)
        tree.grid(row=4, column=0, columnspan=2, padx=6, pady=6)

        total_var = tk.DoubleVar(value=0.0)
        tk.Label(win, text="Total:").grid(row=5, column=0, sticky="e")
        tk.Label(win, textvariable=total_var).grid(row=5, column=1, sticky="w")

        def add_item():
            sel = prod_combo.get()
            if not sel or sel not in prod_map:
                messagebox.showerror("Error", "Select valid product")
                return
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    raise ValueError("qty > 0")
            except Exception:
                messagebox.showerror("Error", "Enter valid quantity")
                return
            pid, unitPrice = prod_map[sel]
            # avoid merging duplicate lines for simplicity; just add new line
            lineTotal = unitPrice * qty
            items.append({"productID": pid, "quantity": qty, "unitPrice": unitPrice, "name": sel})
            tree.insert("", "end", values=(pid, sel.split(" - ", 1)[1].split(" (", 1)[0], qty, unitPrice, lineTotal))
            total_var.set(sum(it['quantity'] * it['unitPrice'] for it in items))

        def remove_selected():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            tree.delete(sel[0])
            items.pop(idx)
            total_var.set(sum(it['quantity'] * it['unitPrice'] for it in items))

        def save_bill():
            if not cust_combo.get():
                messagebox.showerror("Error", "Select customer")
                return
            if not items:
                messagebox.showerror("Error", "Add at least one item")
                return
            cust_id = cust_map[cust_combo.get()]
            bill_date = date.today().isoformat()
            try:
                billID = billing_create(bill_date, cust_id, items)
                messagebox.showinfo("Saved", f"Bill saved. billID = {billID}")
                win.destroy()
                self.show_bill(billID)
            except Exception as e:
                messagebox.showerror("Error saving bill", str(e))

        tk.Button(win, text="Add Item", command=add_item).grid(row=2, column=2, padx=6)
        tk.Button(win, text="Remove Selected", command=remove_selected).grid(row=4, column=2, padx=6)
        tk.Button(win, text="Save Bill", command=save_bill).grid(row=6, column=0, pady=8)
        tk.Button(win, text="Close", command=win.destroy).grid(row=6, column=1, pady=8)

    def billing_view_window(self):
        win = tk.Toplevel(self)
        win.title("View Bill")
        tk.Label(win, text="Enter billID:").grid(row=0, column=0, padx=6, pady=6)
        e = tk.Entry(win)
        e.grid(row=0, column=1, padx=6, pady=6)

        def do_view():
            bid = e.get()
            if not bid.isdigit():
                messagebox.showerror("Error", "Enter valid numeric billID")
                return
            bill, items = billing_get(int(bid))
            if not bill:
                messagebox.showerror("Not found", "Bill not found")
                return
            text = f"BillID: {bill[0]}\nDate: {bill[1]}\nCustomerID: {bill[2]}\nTotal: {bill[3]}\n\nItems:\n"
            for it in items:
                text += f"ProductID: {it[0]} | Qty: {it[1]} | Unit: {it[2]} | LineTotal: {it[3]}\n"
            messagebox.showinfo("Bill", text)

        tk.Button(win, text="View", command=do_view).grid(row=1, column=0, columnspan=2, pady=6)

    def show_bill(self, billID):
        bill, items = billing_get(billID)
        if not bill:
            messagebox.showerror("Error", "Bill not found")
            return
        win = tk.Toplevel(self)
        win.title(f"Bill #{billID}")
        txt = tk.Text(win, width=80, height=25)
        txt.pack()
        # fetch customer name
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM Customer WHERE customerID=%s", (bill[2],))
        cname = cur.fetchone()
        cur.close()
        conn.close()
        cname = cname[0] if cname else "Unknown"
        txt.insert("end", f"Bill ID: {bill[0]}\nDate: {bill[1]}\nCustomer: {cname} (ID: {bill[2]})\n\n")
        txt.insert("end", "Items:\n")
        txt.insert("end", f"{'ProductID':<10}{'Qty':>6}{'Unit':>12}{'LineTotal':>15}\n")
        for it in items:
            txt.insert("end", f"{it[0]:<10}{it[1]:>6}{it[2]:>12.2f}{it[3]:>15.2f}\n")
        txt.insert("end", f"\nTotal: {bill[3]:.2f}\n")

if __name__ == "__main__":
    # Basic check: try connecting to DB and show message if database missing
    try:
        conn = get_connection()
        conn.close()
    except Exception as e:
        print("Database connection failed. Please check DB_CONFIG and ensure the database/tables created.")
    app = App()
    app.mainloop()
