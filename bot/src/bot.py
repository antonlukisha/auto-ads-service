import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.logging import get_logger, setup_logging

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

setup_logging()
logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Объявления о продаже автомобилей с сайта carsensor.net*\n\n"
        "Я помогу найти машину! Просто напишите, что ищете.\n\n"
        "Примеры:\n"
        "• `bmw x5 чёрный`\n"
        "• `тойота до 2.5 млн`\n"
        "• `хонда после 2020 красная`\n"
        "• `хонда в пределах 3 млн`\n\n"
        "Я сам пойму, что вы ищете!",
        parse_mode="Markdown"
    )
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*Как искать:*\n\n"
        "Просто напишите, что хотите найти. Например:\n"
        "• `bmw x5 чёрный`\n"
        "• `тойота до 2.5 млн`\n"
        "• `хонда после 2020 красная`\n"
        "• `хонда в пределах 3 млн`\n\n"
        "Я сам пойму, что вы ищете!",
        parse_mode="Markdown"
    )
    logger.info("Help command received")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Request from {update.effective_user.first_name}: {update.message.text}")
    await update.message.chat.send_action(action="typing")
    answer = await
    await update.message.reply_text(answer, parse_mode="Markdown", disable_web_page_preview=False)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}", exc_info=context.error)


def main() -> None:
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found. Get it from @BotFather")
        return

    if not LLM_API_KEY or not LLM_MODEL:
        logger.error("LLM_API_KEY or LLM_MODEL not found. Set them in .env")
        return


    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()