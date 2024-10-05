import os
import telebot
from telebot.apihelper import ApiException
from flask import Flask
import threading
import logging
import time

# Configure logging to keep track of any issues that occur
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

# Retrieve the bot token and channel ID from environment variables
TOKEN = "7900470468:AAH5k_KcunG52E043Ld1OvruL8ijshcizp8"
CHANNEL_ID = "-1002389759470"  # e.g., "@your_channel_username"

# Check if the token or channel ID is None or contains only whitespace
if not TOKEN:
    raise ValueError("No valid Telegram bot token found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
if not CHANNEL_ID:
    raise ValueError("No valid Telegram channel ID found. Please set the TELEGRAM_CHANNEL_ID environment variable.")

bot = telebot.TeleBot(TOKEN)

# Initialize Flask application
app = Flask(__name__)

@app.route('/')
def home():
    return "I am alive"

def run_flask():
    try:
        app.run(host='0.0.0.0', port=8080)  # Flask runs on port 8080
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

    # Define `username_display` before the try block
    username_display = f"@{username}" if username != "No username" else username

    try:
        # Get user profile photos
        profile_photos = bot.get_user_profile_photos(user_id)

        # If the user has profile photos, send the first one
        if profile_photos.total_count > 0:
            photo_file_id = profile_photos.photos[0][0].file_id
            bot.send_photo(message.chat.id, photo_file_id)
            
            # Send to channel
            bot.send_photo(
                CHANNEL_ID, 
                photo_file_id, 
                caption=f"New user started the bot!\n\nUsername: {username_display}\nUser ID: `{user_id}`", 
                parse_mode='Markdown'
            )

    except ApiException as e:
        logging.warning(f"API Exception when retrieving profile photo for user {user_id}: {e}")
        bot.send_message(message.chat.id, "Couldn't retrieve profile photos. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error for user {user_id}: {e}")
        bot.send_message(message.chat.id, "An unexpected error occurred. Please try again later.")

    # Create the response message with username and user ID
    response_message = f"Username: {username_display}\n\nUser ID:\n`{user_id}`"

    # Send the response message after sending the photo
    try:
        bot.send_message(message.chat.id, response_message, parse_mode='Markdown')
    except ApiException as e:
        logging.warning(f"API Exception when sending message for user {user_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error when sending message for user {user_id}: {e}")

def main():
    try:
        # Start the keep-alive server
        keep_alive()
        # Start polling for the Telegram bot
        logging.info("Bot started. Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)  # Configured for network stability

    except Exception as e:
        logging.error(f"Critical error in main loop: {e}")
        # Attempt to recover after a crash
        time.sleep(5)
        main()  # Restart main loop

if __name__ == "__main__":
    main()
