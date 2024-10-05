import os
import telebot
from telebot.apihelper import ApiException

# Retrieve the bot token and channel ID from environment variables
TOKEN = "7900470468:AAH5k_KcunG52E043Ld1OvruL8ijshcizp8"
CHANNEL_ID = "-1002389759470"  # e.g., "@your_channel_username"

# Check if the token or channel ID is None or contains only whitespace
if TOKEN is None or not TOKEN.strip():
    raise ValueError("No valid Telegram bot token found. Please set the TELEGRAM_BOT_TOKEN environment variable.")

if CHANNEL_ID is None or not CHANNEL_ID.strip():
    raise ValueError("No valid Telegram channel ID found. Please set the TELEGRAM_CHANNEL_ID environment variable.")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    username = user.username if user.username else "No username"
    user_id = user.id

    try:
        # Get user profile photos
        profile_photos = bot.get_user_profile_photos(user_id)

        # If the user has profile photos, send the first one
        if profile_photos.total_count > 0:
            photo_file_id = profile_photos.photos[0][0].file_id
            bot.send_photo(message.chat.id, photo_file_id)

            # Send profile photo, username, and user ID to the specified channel
            if username != "No username":
                username_display = f"@{username}"
            else:
                username_display = username
            
            # Send to channel
            bot.send_photo(
                CHANNEL_ID, 
                photo_file_id, 
                caption=f"New user started the bot!\n\nUsername: {username_display}\nUser ID: `{user_id}`", 
                parse_mode='Markdown'
            )

    except ApiException as e:
        bot.send_message(message.chat.id, "Couldn't retrieve profile photos.")
        return  # Exit if unable to get profile photo

    # Create the response message with username and user ID
    response_message = f"Username: {username_display}\n\nUser ID:\n`{user_id}`"

    # Send the response message after sending the photo
    bot.send_message(message.chat.id, response_message, parse_mode='Markdown')

# Polling loop to keep the bot running
bot.infinity_polling()
