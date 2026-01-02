import sqlite3
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_PATH = "ATM.db"
db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

# --- Database schema ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    balance REAL DEFAULT 0.0,
    creditor REAL DEFAULT 0.0,
    debtor REAL DEFAULT 0.0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deposit(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    amount REAL DEFAULT 0,
    date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraw(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL,
    amount REAL DEFAULT 0,
    date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS debt(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creditor_id TEXT NOT NULL,
    creditor_name TEXT NOT NULL,
    debtor_id TEXT NOT NULL,
    debtor_name TEXT NOT NULL,
    amount REAL DEFAULT 0.0,
    date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS undebt(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creditor_id TEXT NOT NULL,
    creditor_name TEXT NOT NULL,
    debtor_id TEXT NOT NULL,
    debtor_name TEXT NOT NULL,
    amount REAL DEFAULT 0.0,
    date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT DEFAULT NULL,
    creditor_id TEXT DEFAULT NULL,
    creditor_name TEXT DEFAULT NULL,
    debtor_id TEXT DEFAULT NULL,
    debtor_name TEXT DEFAULT NULL,
    t_type TEXT NOT NULL,
    amount REAL NOT NULL,
    date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
)
""")
db.commit()

# --- Helpers ---
def generate_account_id():
    while True:
        acc = str(random.randint(10**9, 10**10 - 1))
        cursor.execute("SELECT 1 FROM users WHERE account_id=?", (acc,))
        if cursor.fetchone() is None:
            return acc

def get_user(account_id):
    cursor.execute("SELECT * FROM users WHERE account_id=?", (account_id,))
    return cursor.fetchone()

def log_transaction_account(account_id, t_type, amount):
    cursor.execute(
        "INSERT INTO transactions(account_id, t_type, amount) VALUES(?, ?, ?)",
        (account_id, t_type, amount)
    )

def log_transaction_between(creditor_id, creditor_name, debtor_id, debtor_name, t_type, amount):
    cursor.execute("""
        INSERT INTO transactions(
            creditor_id, creditor_name, debtor_id, debtor_name, t_type, amount
        ) VALUES(?, ?, ?, ?, ?, ?)
    """, (creditor_id, creditor_name, debtor_id, debtor_name, t_type, amount))


# --- GUI Actions ---
def gui_add_user():
    try:
        name = simpledialog.askstring("Add Account", "Enter your name:")
        if not name:
            return
        account_id = generate_account_id()
        cursor.execute("INSERT INTO users(name, account_id) VALUES(?, ?)", (name, account_id))
        db.commit()
        messagebox.showinfo("Success", f"Account added!\nID: {account_id}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_deposit():
    try:
        account_id = simpledialog.askstring("Deposit", "Enter account ID:")
        if not account_id:
            return
        user = get_user(account_id)
        if not user:
            messagebox.showerror("Error", "Account not found!")
            return
        amount = simpledialog.askfloat("Deposit", "Enter deposit amount:")
        if amount <= 0:
            messagebox.showerror("Error", "Deposit must be positive!")
            return
        new_balance = user[3] + amount
        cursor.execute("UPDATE users SET balance=? WHERE account_id=?", (new_balance, account_id))
        cursor.execute("INSERT INTO deposit(account_id, amount) VALUES(?, ?)", (account_id, amount))
        log_transaction_account(account_id, "Deposit", amount)
        db.commit()
        messagebox.showinfo("Success", f"Deposited {amount}$\nNew Balance: {new_balance}$")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_withdraw():
    try:
        account_id = simpledialog.askstring("Withdraw", "Enter account ID:")
        if not account_id:
            return
        user = get_user(account_id)
        if not user:
            messagebox.showerror("Error", "Account not found!")
            return
        amount = simpledialog.askfloat("Withdraw", "Enter withdraw amount:")
        if amount <= 0:
            messagebox.showerror("Error", "Withdraw must be positive!")
            return
        if amount > user[3]:
            messagebox.showerror("Error", f"Insufficient funds! Balance: {user[3]}$")
            return
        new_balance = user[3] - amount
        cursor.execute("UPDATE users SET balance=? WHERE account_id=?", (new_balance, account_id))
        cursor.execute("INSERT INTO withdraw(account_id, amount) VALUES(?, ?)", (account_id, amount))
        log_transaction_account(account_id, "Withdraw", amount)
        db.commit()
        messagebox.showinfo("Success", f"Withdrawn {amount}$\nNew Balance: {new_balance}$")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_debt():
    try:
        creditor_id = simpledialog.askstring("Debt", "Enter your (creditor) account ID:")
        if not creditor_id:
            return
        creditor_user = get_user(creditor_id)
        if not creditor_user:
            messagebox.showerror("Error", "Creditor account not found!")
            return
        debtor_id = simpledialog.askstring("Debt", "Enter debtor account ID:")
        if not debtor_id:
            return
        debtor_user = get_user(debtor_id)
        if not debtor_user:
            messagebox.showerror("Error", "Debtor account not found!")
            return
        if creditor_id == debtor_id:
            messagebox.showerror("Error", "Creditor and debtor cannot be the same!")
            return
        amount = simpledialog.askfloat("Debt", "Enter amount to lend:")
        if amount <= 0 or amount > creditor_user[3]:
            messagebox.showerror("Error", "Invalid amount!")
            return
        # Update balances
        cursor.execute("UPDATE users SET balance=?, creditor=? WHERE account_id=?",
                       (creditor_user[3]-amount, creditor_user[4]+amount, creditor_id))
        cursor.execute("UPDATE users SET balance=?, debtor=? WHERE account_id=?",
                       (debtor_user[3]+amount, debtor_user[5]+amount, debtor_id))
        cursor.execute("INSERT INTO debt(creditor_id, creditor_name, debtor_id, debtor_name, amount) VALUES(?, ?, ?, ?, ?)",
                       (creditor_id, creditor_user[2], debtor_id, debtor_user[2], amount))
        log_transaction_between(creditor_id, creditor_user[2], debtor_id, debtor_user[2], "Debt", amount)
        db.commit()
        messagebox.showinfo("Success", f"{creditor_user[2]} lent {amount}$ to {debtor_user[2]}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_undebt():
    try:
        debtor_id = simpledialog.askstring("Repay Debt", "Enter your (debtor) account ID:")
        if not debtor_id:
            return
        debtor_user = get_user(debtor_id)
        if not debtor_user:
            messagebox.showerror("Error", "Debtor account not found!")
            return
        creditor_id = simpledialog.askstring("Repay Debt", "Enter creditor account ID:")
        if not creditor_id:
            return
        creditor_user = get_user(creditor_id)
        if not creditor_user:
            messagebox.showerror("Error", "Creditor account not found!")
            return
        amount = simpledialog.askfloat("Repay Debt", "Enter amount to pay:")
        if amount <= 0 or amount > debtor_user[5] or amount > debtor_user[3]:
            messagebox.showerror("Error", "Invalid repayment amount!")
            return
        # Update balances
        cursor.execute("UPDATE users SET balance=?, debtor=? WHERE account_id=?",
                       (debtor_user[3]-amount, debtor_user[5]-amount, debtor_id))
        cursor.execute("UPDATE users SET balance=?, creditor=? WHERE account_id=?",
                       (creditor_user[3]+amount, creditor_user[4]-amount, creditor_id))
        cursor.execute("INSERT INTO undebt(creditor_id, creditor_name, debtor_id, debtor_name, amount) VALUES(?, ?, ?, ?, ?)",
                       (creditor_id, creditor_user[2], debtor_id, debtor_user[2], amount))
        log_transaction_between(creditor_id, creditor_user[2], debtor_id, debtor_user[2], "Undebt", amount)
        db.commit()
        messagebox.showinfo("Success", f"{debtor_user[2]} paid {amount}$ to {creditor_user[2]}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_show_details():
    try:
        account_id = simpledialog.askstring("Account Details", "Enter account ID:")
        if not account_id:
            return
        user = get_user(account_id)
        if not user:
            messagebox.showerror("Error", "Account not found!")
            return
        cursor.execute("SELECT date, t_type, account_id, creditor_name, debtor_name, amount FROM transactions WHERE account_id=? OR creditor_id=? OR debtor_id=? ORDER BY date LIMIT 10",
                       (account_id, account_id, account_id))
        transactions = cursor.fetchall()
        details = f"Account: {user[2]} ({user[1]})\nBalance: {user[3]}$\nTotal Lent: {user[4]}$\nTotal Owed: {user[5]}$\n\nLast 10 transactions:\n"
        for t in transactions:
            date, t_type, acc, c_name, d_name, amt = t
            if t_type in ("Deposit", "Withdraw"):
                who = f"Account {acc}"
            elif t_type == "Debt":
                who = f"{c_name} -> {d_name}"
            else:
                who = f"{d_name} -> {c_name}"
            details += f"[{date}] {t_type:<8} | {who:<25} | {amt}$\n"
        messagebox.showinfo("Account Details", details)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def gui_delete_user():
    try:
        account_id = simpledialog.askstring("Delete Account", "Enter account ID:")
        if not account_id:
            return
        user = get_user(account_id)
        if not user:
            messagebox.showerror("Error", "Account not found!")
            return
        if user[4] != 0 or user[5] != 0:
            messagebox.showerror("Error", "Settle debts first!")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this account?")
        if confirm:
            cursor.execute("DELETE FROM users WHERE account_id=?", (account_id,))
            db.commit()
            messagebox.showinfo("Success", "Account deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# --- Run GUI ---
def run_gui():
    root = tk.Tk()
    root.title("ATM System")
    root.geometry("450x550")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 14), padding=10)
    style.configure("Header.TLabel", font=("Arial", 20, "bold"))

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(expand=True, fill="both")

    ttk.Label(main_frame, text="ATM System", style="Header.TLabel").pack(pady=15)
    ttk.Button(main_frame, text="Add Account", command=gui_add_user).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Deposit Money", command=gui_deposit).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Withdraw Money", command=gui_withdraw).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Debt Money (Lend)", command=gui_debt).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Undebt Money (Pay)", command=gui_undebt).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Show Account Details", command=gui_show_details).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Delete Account", command=gui_delete_user).pack(fill='x', pady=7)
    ttk.Button(main_frame, text="Exit", command=root.destroy).pack(fill='x', pady=15)

    root.mainloop()


if __name__ == "__main__":
    try:
        run_gui()
    finally:
        db.close()
