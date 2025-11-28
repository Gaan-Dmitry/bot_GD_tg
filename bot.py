import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from config import BOT_TOKEN
from handlers.start import start
from handlers.buttons import button_handler
from handlers.messages import handle_message

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    error = context.error
    if "Message is not modified" in str(error):
        logger.info("Сообщение не изменилось, пропускаем ошибку")
    else:
        logger.error(f"Ошибка: {error}", exc_info=error)

def main():
    # Создаем updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Получаем dispatcher для регистрации обработчиков
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error_handler)
    
    # Запускаем бота
    updater.start_polling()
    logger.info("Бот запущен!")
    updater.idle()

if __name__ == '__main__':
    main()
