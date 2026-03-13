import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.config import LLM_API_KEY, LLM_MODEL, POSTGRES_DSN, TELEGRAM_TOKEN
from src.database import db
from src.logging import get_logger, setup_logging
from src.search import search_cars_via_llm

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

setup_logging()
logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a message when the command /start is issued.
    """
    if update.message is None:
        logger.error("Update message is None in start handler")
        return

    await update.message.reply_text(
        "*Объявления о продаже автомобилей с сайта carsensor.net*\n\n"
        "Я помогу найти машину! Просто напишите, что ищете.\n\n"
        "Примеры:\n"
        "• `bmw x5 чёрный`\n"
        "• `тойота до 2.5 млн`\n"
        "• `хонда после 2020 красная`\n"
        "• `хонда в пределах 3 млн`\n\n"
        "Я сам пойму, что вы ищете!",
        parse_mode="Markdown",
    )
    if update.effective_user is not None:
        logger.info(f"User {update.effective_user.id} started the bot")
    else:
        logger.info("Unknown user started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a message when the command /help is issued.
    """
    if update.message is None:
        logger.error("Update message is None in help handler")
        return
    await update.message.reply_text(
        "*Как искать:*\n\n"
        "Просто напишите, что хотите найти. Например:\n"
        "• `bmw x5 чёрный`\n"
        "• `тойота до 2.5 млн`\n"
        "• `хонда после 2020 красная`\n"
        "• `хонда в пределах 3 млн`\n\n"
        "Я сам пойму, что вы ищете!",
        parse_mode="Markdown",
    )
    logger.info("Help command received")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming messages.
    """
    if update.message is None:
        logger.error("Update message is None in message handler")
        return

    text = update.message.text

    if text is None:
        logger.error("Message text is None")
        return

    user_name = "Unknown"
    if update.effective_user is not None:
        user_name = update.effective_user.first_name or "Неизвестный"

    logger.info(f"Request from {user_name}: {text}")

    if update.message.chat is None:
        logger.error("Message chat is None")
        return

    await update.message.chat.send_action(action="typing")
    try:
        answer = await search_cars_via_llm(text)
        await update.message.reply_text(
            answer, parse_mode="Markdown", disable_web_page_preview=False
        )
    except Exception as e:
        await update.message.reply_text(str(e))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors.
    """
    logger.error(f"Error: {context.error}", exc_info=context.error)


async def main() -> None:
    """
    Main entry point for the bot.
    """
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found. Get it from @BotFather")
        return

    if not LLM_API_KEY or not LLM_MODEL:
        logger.error("LLM_API_KEY or LLM_MODEL not found.")
        return

    if POSTGRES_DSN is None:
        logger.error("POSTGRES_DSN not found.")
        return

    try:
        await db.initialize(POSTGRES_DSN)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise Exception(f"Failed to connect to database: {e}")
    else:
        logger.info("Database connected")
        logger.info(f"dsn:{db.dsn}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    await app.initialize()
    await app.start()

    try:
        if app.updater is None:
            logger.error("Updater is None")
            return
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot stopping...")
    finally:
        if app.updater is not None:
            await app.updater.stop()
        await app.stop()
        await app.shutdown()
        await db.close()
        logger.info("Bot stopped")


def run() -> None:
    """
    Synchronous entry point for running the app.
    """

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
