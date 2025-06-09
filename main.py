import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from bot.handlers import main_handler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    if not Config.TELEGRAM_TOKEN:
        raise ValueError("Необходимо указать TELEGRAM_TOKEN в .env файле")
    if not Config.OPENROUTER_API_KEY:
        raise ValueError("Необходимо указать OPENROUTER_API_KEY в .env файле")

    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", main_handler.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_handler.handle_message))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
