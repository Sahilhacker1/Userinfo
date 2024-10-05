import os
import telebot
from telebot.apihelper import ApiException
from flask import Flask, request
import threading
import logging
import time

# Configure logging to keep track of any issues that occur
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

# Retrieve the bot token and channel ID from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # e.g., "@your_channel_username"

# Check if the token or channel ID is None or contains only whitespace
if not TOKEN:
    raise ValueError("No valid Telegram bot token found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
if not CHANNEL_ID:
    raise ValueError("No valid Telegram channel ID found. Please set the TELEGRAM_CHANNEL_ID environment variable.")

bot = telebot.TeleBot(TOKEN, threaded=True)  # Enable threaded mode to handle multiple users

# Initialize Flask application
app = Flask(__name__)

# Webhook Setup
WEBHOOK_URL_BASE = "https://<your-app-name>.herokuapp.com"
WEBHOOK_URL_PATH = f"/{TOKEN}/"

@app.route('/')
def home():
    return "I am alive"

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

def run_flask():
    try:
        # Run Flask app in threaded mode to handle multiple requests concurrently
        app.run(host='0.0.0.0', port=8080, threaded=True)
    except Exception as e:
        logging.error(f"Error in Flask server: {e}")

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True  # Ensures thread exits when main program does
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    username = user.username if user.username else "No username"
    user_id = user.id
    first_name = user.first_name if user.first_name else "No first name"
    last_name = user.last_name if user.last_name else "No last name"

    # Prepare the response with user details
    response_message = (
        f"Username: @{username if username != 'No username' else 'N/A'}\n"
        f"First Name: {first_name}\n"
        f"Last Name: {last_name}\n"
        f"User ID: `{user_id}`"
    )

    # Send the response message
    try:
        bot.send_message(message.chat.id, response_message, parse_mode='Markdown')
        # Send user details to the specified channel
        bot.send_message(
            CHANNEL_ID,
            f"New user started the bot!\n\nUsername: @{username if username != 'No username' else 'N/A'}\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"User ID: `{user_id}`",
            parse_mode='Markdown'
        )
    except ApiException as e:
        logging.warning(f"API Exception when sending message for user {user_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error when sending message for user {user_id}: {e}")

def main():
    # Start the keep-alive server
    keep_alive()

    # Remove any previous webhook and set the new one
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    logging.info("Webhook set. Bot is now running...")

if __name__ == "__main__":
    main()
