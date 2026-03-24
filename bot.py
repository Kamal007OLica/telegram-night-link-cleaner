import os
import re
from datetime import datetime, time, timedelta

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

# Simple URL regex
URL_REGEX = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|wa\.me/\S+)",
    re.IGNORECASE,
)

# Night window in IST: 22:00 to 06:00
NIGHT_START = time(22, 0)  # 22:00
NIGHT_END = time(6, 0)     # 06:00


def is_night_now_ist() -> bool:
    """
    Returns True if current time in IST is between 22:00 and 06:00.
    Uses UTC on server and converts to IST (UTC+5:30).
    """
    now_utc = datetime.utcnow()
    ist = now_utc + timedelta(hours=5, minutes=30)
    current_t = ist.time()
    return NIGHT_START <= current_t or current_t < NIGHT_END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Vanakkam! 10 PM – 6 AM (IST) time-la group-la links varumbodhu naan auto delete panra bot. "
        "6 AM – 10 PM varaikkum links allowed. Users ban aagama messages mattum delete panren."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    # Only react in groups/supergroups
    if update.effective_chat.type not in ("group", "supergroup"):
        return

    text = msg.text

    # Check if message has URL
    if not URL_REGEX.search(text):
        return

    # Check time window (IST)
    if not is_night_now_ist():
        return

    # Delete the message (no ban)
    try:
        await msg.delete()
    except Exception as e:
        print("Delete error:", e)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling (simpler, no webhook needed)
    application.run_polling()


if __name__ == "__main__":
    main()
