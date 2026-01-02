#   ____                       _____         _  _ 
#  / ___|___  ___  __ _ _ __  |  ___| __ ___(_)(_)
# | |   / _ \/ __|/ _` | '__| | |_ | '__/ _ \ || |
# | |__|  __/\__ \ (_| | |    |  _|| | |  __/ || |
#  \____\___||___/\__,_|_|    |_|  |_|  \___|_|/ |
#                                            |__/

import sqlite3
import random

DB_PATH = "ATM.db"

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

# --- Schema -----------------------------------------------------------------
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

# --- Helpers ----------------------------------------------------------------
def generate_account_id() -> str:
    while True:
        acc = str(random.randint(10**9, 10**10 - 1))
        cursor.execute("SELECT 1 FROM users WHERE account_id=?", (acc,))
        if cursor.fetchone() is None:
            return acc

def get_user(account_id: str):
    cursor.execute("SELECT * FROM users WHERE account_id=?", (account_id,))
    return cursor.fetchone()

def log_transaction_account(account_id: str, t_type: str, amount: float):
    cursor.execute(
        "INSERT INTO transactions(account_id, t_type, amount) VALUES(?, ?, ?)",
        (account_id, t_type, amount)
    )

def log_transaction_between(creditor_id: str, creditor_name: str,
                            debtor_id: str, debtor_name: str,
                            t_type: str, amount: float):
    cursor.execute("""
        INSERT INTO transactions(
            creditor_id, creditor_name, debtor_id, debtor_name, t_type, amount
        ) VALUES(?, ?, ?, ?, ?, ?)
    """, (creditor_id, creditor_name, debtor_id, debtor_name, t_type, amount))

def input_with_exit(prompt: str):
    """Input with 'q' option to exit."""
    print("Press 'q' to exit")
    value = input(prompt).strip()
    if value.lower() == 'q':
        return None
    return value

# --- Actions ----------------------------------------------------------------
def add_user():
    try:
        name = input_with_exit("Enter your name: ")
        if name is None:
            return
        if not name:
            raise ValueError("Name cannot be empty")
        account_id = generate_account_id()
        cursor.execute("INSERT INTO users(name, account_id) VALUES(?, ?)", (name, account_id))
        db.commit()
        print(f"User added successfully! Account ID: {account_id}")
    except sqlite3.IntegrityError:
        print("Error: Account already exists.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def deposit():
    try:
        account_id = input_with_exit("Enter account ID: ")
        if account_id is None:
            return
        user = get_user(account_id)
        if not user:
            raise LookupError("Account not found!")
        amount_str = input_with_exit("Enter deposit amount: ")
        if amount_str is None:
            return
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        new_balance = user[3] + amount
        cursor.execute("UPDATE users SET balance=? WHERE account_id=?", (new_balance, account_id))
        cursor.execute("INSERT INTO deposit(account_id, amount) VALUES(?, ?)", (account_id, amount))
        log_transaction_account(account_id, "Deposit", amount)
        db.commit()
        print(f"Deposited {amount}. Your balance: {new_balance}")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

def withdraw():
    try:
        account_id = input_with_exit("Enter account ID: ")
        if account_id is None:
            return
        user = get_user(account_id)
        if not user:
            raise LookupError("Account not found!")
        amount_str = input_with_exit("Enter withdraw amount: ")
        if amount_str is None:
            return
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Withdraw must be positive")
        if amount > user[3]:
            raise ValueError(f"Insufficient funds. You only have {user[3]}$")
        new_balance = user[3] - amount
        cursor.execute("UPDATE users SET balance=? WHERE account_id=?", (new_balance, account_id))
        cursor.execute("INSERT INTO withdraw(account_id, amount) VALUES(?, ?)", (account_id, amount))
        log_transaction_account(account_id, "Withdraw", amount)
        db.commit()
        print(f"Withdrawn {amount}. Your balance: {new_balance}")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

def debt():
    try:
        creditor_id = input_with_exit("Enter your (creditor) account_id: ")
        if creditor_id is None:
            return
        creditor_user = get_user(creditor_id)
        if not creditor_user:
            raise LookupError("Creditor account not found!")
        debtor_id = input_with_exit("Enter debtor account_id: ")
        if debtor_id is None:
            return
        debtor_user = get_user(debtor_id)
        if not debtor_user:
            raise LookupError("Debtor account not found!")
        if creditor_id == debtor_id:
            raise ValueError("Creditor and debtor cannot be the same account")
        amount_str = input_with_exit("Enter the amount to be credited: ")
        if amount_str is None:
            return
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Debt amount must be positive")
        if amount > creditor_user[3]:
            raise ValueError(f"Insufficient funds. You only have {creditor_user[3]}$")

        cursor.execute("""
            INSERT INTO debt(creditor_id, creditor_name, debtor_id, debtor_name, amount)
            VALUES(?, ?, ?, ?, ?)
        """, (creditor_id, creditor_user[2], debtor_id, debtor_user[2], amount))

        new_balance_creditor = creditor_user[3] - amount
        new_balance_debtor = debtor_user[3] + amount
        new_creditor = creditor_user[4] + amount
        new_debtor = debtor_user[5] + amount

        cursor.execute("UPDATE users SET balance=?, creditor=? WHERE account_id=?",
                        (new_balance_creditor, new_creditor, creditor_id))
        cursor.execute("UPDATE users SET balance=?, debtor=? WHERE account_id=?",
                        (new_balance_debtor, new_debtor, debtor_id))

        log_transaction_between(creditor_id, creditor_user[2], debtor_id, debtor_user[2], "Debt", amount)
        db.commit()
        print(f"{creditor_user[2]} lent {amount}$ to {debtor_user[2]}")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

def undebt():
    try:
        debtor_id = input_with_exit("Enter your (debtor) account_id: ")
        if debtor_id is None:
            return
        debtor_user = get_user(debtor_id)
        if not debtor_user:
            raise LookupError("Debtor account not found!")
        creditor_id = input_with_exit("Enter creditor account_id: ")
        if creditor_id is None:
            return
        creditor_user = get_user(creditor_id)
        if not creditor_user:
            raise LookupError("Creditor account not found!")
        amount_str = input_with_exit("Enter the amount you want to pay off: ")
        if amount_str is None:
            return
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Repayment amount must be positive")
        if debtor_user[5] == 0:
            raise ValueError("You don't have any debt")
        if amount > debtor_user[5]:
            raise ValueError(f"You only owe {debtor_user[5]}")
        if amount > debtor_user[3]:
            raise ValueError(f"Insufficient funds. You only have {debtor_user[3]}$")

        cursor.execute("""
            INSERT INTO undebt(creditor_id, creditor_name, debtor_id, debtor_name, amount)
            VALUES(?, ?, ?, ?, ?)
        """, (creditor_id, creditor_user[2], debtor_id, debtor_user[2], amount))

        new_balance_debtor = debtor_user[3] - amount
        new_balance_creditor = creditor_user[3] + amount
        new_debtor = debtor_user[5] - amount
        new_creditor = creditor_user[4] - amount

        cursor.execute("UPDATE users SET balance=?, debtor=? WHERE account_id=?",
                        (new_balance_debtor, new_debtor, debtor_id))
        cursor.execute("UPDATE users SET balance=?, creditor=? WHERE account_id=?",
                        (new_balance_creditor, new_creditor, creditor_id))

        log_transaction_between(creditor_id, creditor_user[2], debtor_id, debtor_user[2], "Undebt", amount)
        db.commit()
        print(f"{debtor_user[2]} paid {amount}$ to {creditor_user[2]}")
        remaining_amount = new_debtor
        if remaining_amount == 0:
            print("All debt paid off!")
        else:
            print(f"Remaining amount to pay: {remaining_amount}$")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

def show_details():
    try:
        account_id = input_with_exit("Enter account ID to show details: ")
        if account_id is None:
            return
        user = get_user(account_id)
        if not user:
            raise LookupError("Account not found!")

        print("#" * 50)
        print(f"Account: {user[2]} ({user[1]})")
        print(f"Balance: {user[3]}$")
        print(f"Total Lent (creditor): {user[4]}$")
        print(f"Total Owed (debtor): {user[5]}$")
        print("-" * 50)

        cursor.execute("""
            SELECT date, t_type, account_id, creditor_name, debtor_name, amount
            FROM transactions
            WHERE account_id=? OR creditor_id=? OR debtor_id=?
            ORDER BY date
            LIMIT 10
        """, (account_id, account_id, account_id))
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                date, ttype, acc, c_name, d_name, amt = r
                if ttype in ("Deposit", "Withdraw"):
                    who = f"Account {acc}"
                elif ttype == "Debt":
                    who = f"{c_name} -> {d_name}"
                else:
                    who = f"{d_name} -> {c_name}"
                print(f"[{date}] {ttype:<8} | {who:<25} | {amt}$")
        else:
            print("No transactions found.")
        print("#" * 50)
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

def delete_user():
    try:
        account_id = input_with_exit("Enter account ID to delete: ")
        if account_id is None:
            return
        user = get_user(account_id)
        if not user:
            raise LookupError("Account not found!")
        if user[4] != 0 or user[5] != 0:
            raise ValueError("Cannot delete account with outstanding creditor/debtor amounts. Settle debts first.")
        while True:
            confirm_msg = input("Are you sure? the account will be completely deleted! (y/n): ").strip().lower()
            if confirm_msg == 'y':
                cursor.execute("DELETE FROM users WHERE account_id=?", (account_id,))
                db.commit()
                print("Account deleted successfully.")
                break
            elif confirm_msg == 'n':
                print("Operation has canceled!")
                break
            else:
                print("The option is not available, please try again!")
    except ValueError as ve:
        print(f"Invalid operation: {ve}")
    except LookupError as le:
        print(le)
    except Exception as e:
        print(f"Unexpected error: {e}")

# --- Main Menu --------------------------------------------------------------
def main_menu():
    while True:
        print(f"{'#'*10} Welcome To Our ATM System {'#'*10}")
        print("1. Add Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Debt Money From => To")
        print("5. Undebt Money From => To")
        print("6. Show Details")
        print("7. Delete Account")
        print("8. Exit")
        print("#"*47)

        try:
            number = input("Choose the service number you want, please: ").strip()
            if number == '1':
                add_user()
            elif number == '2':
                deposit()
            elif number == '3':
                withdraw()
            elif number == '4':
                debt()
            elif number == '5':
                undebt()
            elif number == '6':
                show_details()
            elif number == '7':
                delete_user()
            elif number == '8':
                print("Thanks for using\nGood Bye!")
                break
            else:
                print("Choose number only between 1 => 8, please try again.")
        except Exception as e:
            print(f"Unexpected error in menu {e}")

if __name__ == '__main__':
    try:
        main_menu()
    finally:
        db.close()
