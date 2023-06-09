import os
import sqlite3 
from cryptography.fernet import Fernet

key_filename = 'key.key'
if not os.path.isfile(key_filename):
    key = Fernet.generate_key()
    with open(key_filename, 'wb') as key_file:
        key_file.write(key)
else:
    with open(key_filename, 'rb') as key_file:
        key = key_file.read()

cipher_suite = Fernet(key)

try: 
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
except sqlite3.OperationalError:
    print("""----------------------\n no database found \n----------------------""")

def add_password():
    user_name = input("give username: ")
    password = input("give password: ")

    encrypted_password = cipher_suite.encrypt(password.encode())

    c.execute("CREATE TABLE IF NOT EXISTS info (user_name TEXT, password TEXT)")

    c.execute("INSERT INTO info (user_name, password) VALUES (?, ?)", (user_name, encrypted_password))
    conn.commit()

    print("""----------------------\n password added successfully \n----------------------""")

def view_pass():
    c.execute("CREATE TABLE IF NOT EXISTS info (user_name TEXT, password TEXT)")
    c.execute("SELECT * FROM info")
    passwords = c.fetchall()


    if len(passwords) > 0:
        print()
        for password in passwords:
            decrypted_password = None
            if password[1]:
                decrypted_password = cipher_suite.decrypt(password[1]).decode()
            print(f"username: {password[0]}, password: {decrypted_password}")
    else:
        print("""----------------------\n no passwords found. \n----------------------""")


def search_pass():
    user_name = input("enter username of the account: ")
    c.execute("CREATE TABLE IF NOT EXISTS info (user_name TEXT, password TEXT)")
    c.execute("SELECT * FROM info WHERE user_name=?", (user_name,))
    password = c.fetchone()

    if password:
        decrypted_password = cipher_suite.decrypt(password[1]).decode()
        print(f"password of account given: {decrypted_password}")
    else:
        print("""----------------------\n Username not found. \n----------------------""")


def delete_pass():
    user_name = input("username of password to delete: ")
    c.execute("CREATE TABLE IF NOT EXISTS info (user_name TEXT, password TEXT)")
    c.execute("SELECT * FROM info WHERE user_name=?", (user_name,))
    result = c.fetchone()
    if not result:
        print("""----------------------\n username does not exist \n----------------------""")
        return
    else:
        c.execute("DELETE FROM info WHERE user_name=?", (user_name,))
        conn.commit()
        print("""----------------------\n Password deleted successfully. \n----------------------""")

def update_pass():
    user_name = input("username of password you want to change: ")
    c.execute("CREATE TABLE IF NOT EXISTS info (user_name TEXT, password TEXT)")
    c.execute("SELECT * FROM info WHERE user_name=?", (user_name,))
    existing_username = c.fetchone()

    if not existing_username:
        print("""----------------------\n username does not exist \n ----------------------""")
        return

    username = input("enter the new username (press enter to skip): ")
    password = input("enter the new password (press enter to skip): ")


    if username: 
        c.execute("UPDATE info SET user_name=? WHERE user_name=?", (user_name, user_name))

    if password:
        encrypted_password = cipher_suite.encrypt(password.encode())
        c.execute("UPDATE info SET password=? WHERE user_name=?", (encrypted_password, user_name))

    conn.commit()
    print("""----------------------\n password updated successfully \n----------------------""")



while True:
    print("what would you like to do? ")
    print("1 - add new password")
    print("2 - access all passwords")
    print("3 - search specific password")
    print("4 - delete a password")
    print("5 - update a password")
    print("6 - exit")

    choice = input("your selected option?  ")

    if choice == "1":
        add_password()

    elif choice == "2":
        view_pass()

    elif choice == "3":
        search_pass()

    elif choice == "4":
        delete_pass()

    elif choice == "5":
        update_pass()

    elif choice == "6":
        break

    else: 
        print("invalid choice")

conn.commit()

conn.close()