import os
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext

PASSWORD_FILE = "password.txt"
KEY_FILE = "keys.json"
LOG_FILE = "log.txt"

# -----------------------------
# PASSWORD SYSTEM
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_password():
    if not os.path.exists(PASSWORD_FILE):
        pwd = simpledialog.askstring("Set Password", "Set new password:", show='*')
        if pwd:
            with open(PASSWORD_FILE, "w") as f:
                f.write(hash_password(pwd))
            messagebox.showinfo("Password", "Password set successfully ✅")

def verify_password_gui():
    def forgot_password():
        if messagebox.askyesno("Forgot Password?", "Do you want to reset your password?"):
            if os.path.exists(PASSWORD_FILE):
                os.remove(PASSWORD_FILE)
            messagebox.showinfo("Reset Password", "Password reset. Please set a new password.")
            setup_password()
            top.destroy()

    while True:
        top = tk.Toplevel()
        top.title("Login")
        top.geometry("350x150")
        tk.Label(top, text="Enter password:").pack(pady=10)
        pwd_entry = tk.Entry(top, show='*', width=25)
        pwd_entry.pack(pady=5)

        result = {'success': False}

        def submit():
            entered = pwd_entry.get()
            if not os.path.exists(PASSWORD_FILE):
                messagebox.showinfo("Password", "No password set. Setting new password.")
                setup_password()
                result['success'] = True
            else:
                with open(PASSWORD_FILE, "r") as f:
                    stored = f.read()
                if stored == hash_password(entered):
                    messagebox.showinfo("Access Granted", "Access Granted ✅")
                    result['success'] = True
                else:
                    messagebox.showerror("Access Denied", "Wrong password ❌")
            top.destroy()

        tk.Button(top, text="Submit", width=12, command=submit, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(top, text="Forgot Password?", width=15, command=forgot_password, bg="#F44336", fg="white").pack(pady=5)

        top.grab_set()
        top.wait_window()
        if result['success']:
            return True

# -----------------------------
# LOGGING
# -----------------------------
def log_action(action):
    with open(LOG_FILE, "a") as f:
        f.write(action + "\n")
    status_label.config(text=action)

# -----------------------------
# KEY STORAGE
# -----------------------------
def save_key(name, key, nonce, tag):
    data = {}
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data = json.load(f)

    data[name] = {
        "key": key.hex(),
        "nonce": nonce.hex(),
        "tag": tag.hex()
    }

    with open(KEY_FILE, "w") as f:
        json.dump(data, f)

def load_key(name):
    with open(KEY_FILE, "r") as f:
        data = json.load(f)
    item = data[name]
    return bytes.fromhex(item["key"]), bytes.fromhex(item["nonce"]), bytes.fromhex(item["tag"])

# -----------------------------
# MESSAGE ENCRYPTION
# -----------------------------
def show_encrypted_message(text):
    top = tk.Toplevel()
    top.title("Encrypted Message")
    tk.Label(top, text="Encrypted message:").pack(pady=5)
    txt = scrolledtext.ScrolledText(top, height=10, width=60)
    txt.pack(padx=10, pady=5)
    txt.insert(tk.END, text)
    txt.config(state="disabled")

    def copy_to_clipboard():
        top.clipboard_clear()
        top.clipboard_append(text)
        messagebox.showinfo("Copied", "Encrypted message copied to clipboard ✅")

    tk.Button(top, text="Copy to Clipboard", bg="#4CAF50", fg="white",
              command=copy_to_clipboard).pack(pady=5)

def encrypt_message():
    msg = simpledialog.askstring("Encrypt Message", "Enter message:")
    if not msg:
        return
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode())
    save_key("message", key, cipher.nonce, tag)
    show_encrypted_message(ciphertext.hex())
    log_action("Message Encrypted ✅")

def decrypt_message():
    try:
        key, nonce, tag = load_key("message")
        ciphertext_hex = simpledialog.askstring("Decrypt Message", "Paste encrypted message:")
        if not ciphertext_hex:
            return
        ciphertext = bytes.fromhex(ciphertext_hex)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        message = cipher.decrypt_and_verify(ciphertext, tag)
        messagebox.showinfo("Decrypted Message", f"Decrypted message:\n{message.decode()}")
        log_action("Message Decrypted ✅")
    except:
        messagebox.showerror("Error", "Tampering detected or wrong input ❌")
        log_action("Failed Decryption ❌")

# -----------------------------
# FILE ENCRYPTION (FIXED)
# -----------------------------
def encrypt_file():
    filename = filedialog.askopenfilename(title="Select file to encrypt")
    if not filename:
        return

    with open(filename, "rb") as f:
        data = f.read()

    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    enc_file = filename + ".enc"

    with open(enc_file, "wb") as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)

    data_store = {}
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            data_store = json.load(f)

    data_store[enc_file] = {
        "key": key.hex(),
        "nonce": cipher.nonce.hex(),
        "tag": tag.hex(),
        "original_name": filename
    }

    with open(KEY_FILE, "w") as f:
        json.dump(data_store, f)

    messagebox.showinfo("File Encrypted", f"File encrypted as:\n{enc_file}")
    log_action(f"File Encrypted ✅: {os.path.basename(filename)}")

# -----------------------------
# FILE DECRYPTION (FIXED)
# -----------------------------
def decrypt_file():
    filename = filedialog.askopenfilename(title="Select encrypted file")
    if not filename:
        return

    try:
        with open(KEY_FILE, "r") as f:
            data_store = json.load(f)

        if filename not in data_store:
            raise Exception("No key found for this file!")

        item = data_store[filename]
        key = bytes.fromhex(item["key"])
        original_name = item.get("original_name", "decrypted_file")

        with open(filename, "rb") as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

        output_file = original_name

        with open(output_file, "wb") as f:
            f.write(decrypted_data)

        messagebox.showinfo("File Decrypted", f"File decrypted as:\n{output_file}")
        log_action(f"File Decrypted ✅: {os.path.basename(output_file)}")

    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed ❌\n{str(e)}")
        log_action("Failed File Decryption ❌")

# -----------------------------
# MAIN GUI
# -----------------------------
root = tk.Tk()
root.title("CyberSec Encryption Tool")
root.geometry("500x400")

status_label = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

def main_gui():
    setup_password()
    if not verify_password_gui():
        root.destroy()
        return

    tk.Button(root, text="Encrypt Message", width=30, bg="#4CAF50", fg="white",
              command=encrypt_message).pack(pady=10)
    tk.Button(root, text="Decrypt Message", width=30, bg="#2196F3", fg="white",
              command=decrypt_message).pack(pady=10)
    tk.Button(root, text="Encrypt File", width=30, bg="#FF9800", fg="white",
              command=encrypt_file).pack(pady=10)
    tk.Button(root, text="Decrypt File", width=30, bg="#9C27B0", fg="white",
              command=decrypt_file).pack(pady=10)
    tk.Button(root, text="Exit", width=30, bg="#F44336", fg="white",
              command=root.destroy).pack(pady=10)

main_gui()
root.mainloop()