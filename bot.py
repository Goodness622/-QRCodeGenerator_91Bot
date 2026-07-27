import logging
import os
from io import BytesIO

import qrcode
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def generate_qr(text: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=None,  # auto-size based on content
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to QRCodeGenerator_91Bot!\n\n"
        "🔳 Just send me any text or link and I'll turn it into a QR code.\n"
        "Or use /qr <text> explicitly.\n\n"
        "Type /help for more info."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/qr <text or link> - Generate a QR code\n\n"
        "You can also just send me plain text or a URL directly, "
        "without a command, and I'll generate the QR code for it."
    )


async def qr_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "Please provide some text or a link after /qr.\n"
            "Example: /qr https://example.com"
        )
        return

    text = " ".join(context.args)
    buffer = generate_qr(text)

    await update.message.reply_photo(
        photo=buffer,
        caption=f"✅ QR code generated for:\n{text}",
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if not text:
        return

    buffer = generate_qr(text)
    await update.message.reply_photo(
        photo=buffer,
        caption=f"✅ QR code generated for:\n{text}",
    )


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Add it in Railway's Variables tab (get the token from @BotFather)."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("qr", qr_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )

    logger.info("Bot started. Polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
