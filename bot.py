import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', 'YOUR_CHAT_ID')

# Данные о пользователях
user_requests = {}

# Команда /start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💼 Наши услуги", callback_data="services")],
        [InlineKeyboardButton("📁 Портфолио", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Узнать стоимость", callback_data="price_request")],
        [InlineKeyboardButton("📞 Консультация", callback_data="consultation")],
        [InlineKeyboardButton("🌐 Наш сайт", url="https://gaan-developments.ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "👋 Добро пожаловать в *Gaan Developments*!\n\n"
        "Мы создаем современные сайты, которые приносят результат:\n"
        "• 🎯 Лендинги\n• 🛒 Интернет-магазины\n• 🏢 Корпоративные сайты\n\n"
        "Я помогу вам:\n"
        "• Узнать о наших услугах и ценах\n• Посмотреть примеры работ\n"
        "• Получить консультацию\n• Оставить заявку на разработку\n\n"
        "Выберите действие:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Обработка кнопок
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "services":
        keyboard = [
            [InlineKeyboardButton("🎯 Лендинг", callback_data="service_landing")],
            [InlineKeyboardButton("🛒 Интернет-магазин", callback_data="service_shop")],
            [InlineKeyboardButton("🏢 Корпоративный сайт", callback_data="service_corporate")],
            [InlineKeyboardButton("💎 Доработка сайта", callback_data="service_improve")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "💼 *Наши услуги*\n\n"
            "Выберите тип сайта для подробной информации:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == "portfolio":
        keyboard = [
            [InlineKeyboardButton("🛒 Интернет-магазины", callback_data="portfolio_shop")],
            [InlineKeyboardButton("🏢 Корпоративные сайты", callback_data="portfolio_corporate")],
            [InlineKeyboardButton("🎓 Обучающие платформы", callback_data="portfolio_learning")],
            [InlineKeyboardButton("🌐 Весь каталог", url="https://gaan-developments.ru/#portfolio")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "📁 *Наше портфолио*\n\n"
            "Вот некоторые из наших проектов:\n\n"
            "• Онлайн-зоомагазин «ZooSwag» 🛒\n"
            "• Сайт ремонтной компании «IРемонт» 🛠️\n"  
            "• V.Museum - онлайн музей 🎓\n\n"
            "Выберите категорию для деталей:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == "price_request":
        user_requests[user_id] = {'type': 'price_request', 'step': 'name'}
        query.edit_message_text(
            "💰 *Расчет стоимости проекта*\n\n"
            "Давайте рассчитаем стоимость вашего сайта!\n\n"
            "Как вас зовут?",
            parse_mode='Markdown'
        )
    
    elif query.data == "consultation":
        user_requests[user_id] = {'type': 'consultation', 'step': 'name'}
        query.edit_message_text(
            "📞 *Бесплатная консультация*\n\n"
            "Я отвечу на все ваши вопросы о разработке сайта!\n\n"
            "Как вас зовут?",
            parse_mode='Markdown'
        )
    
    elif query.data.startswith("service_"):
        service_type = query.data.replace("service_", "")
        services = {
            "landing": {
                "name": "🎯 Лендинг",
                "price": "от 15 000 руб.",
                "desc": "Одностраничный сайт для быстрых продаж и генерации заявок",
                "features": ["Адаптивный дизайн", "SEO-оптимизация", "Формы обратной связи", "Интеграция с аналитикой"]
            },
            "shop": {
                "name": "🛒 Интернет-магазин", 
                "price": "от 30 000 руб.",
                "desc": "Полноценный магазин с каталогом, корзиной и оплатой",
                "features": ["Каталог товаров", "Корзина и оформление", "Платежные системы", "Управление заказами"]
            },
            "corporate": {
                "name": "🏢 Корпоративный сайт",
                "price": "от 25 000 руб.", 
                "desc": "Сайт для компании с несколькими страницами",
                "features": ["О компании", "Услуги/товары", "Контакты", "Блог/новости"]
            },
            "improve": {
                "name": "💎 Доработка сайта",
                "price": "от 5 000 руб.",
                "desc": "Улучшение и доработка существующих сайтов",
                "features": ["Исправление ошибок", "Добавление функций", "Оптимизация", "Техподдержка"]
            }
        }
        
        service = services[service_type]
        
        keyboard = [
            [InlineKeyboardButton("💰 Заказать расчет", callback_data=f"order_{service_type}")],
            [InlineKeyboardButton("💬 Консультация", callback_data="consultation")],
            [InlineKeyboardButton("⬅️ Назад к услугам", callback_data="services")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        features_text = "\n".join([f"• {feature}" for feature in service["features"]])
        
        query.edit_message_text(
            f"{service['name']}\n\n"
            f"*Стоимость:* {service['price']}\n\n"
            f"*Описание:* {service['desc']}\n\n"
            f"*Включено:*\n{features_text}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("order_"):
        service_type = query.data.replace("order_", "")
        user_requests[user_id] = {'type': 'order', 'service': service_type, 'step': 'name'}
        query.edit_message_text(
            "📝 *Оформление заявки*\n\n"
            "Отлично! Давайте оформим заявку на разработку.\n\n"
            "Как вас зовут?",
            parse_mode='Markdown'
        )
    
    elif query.data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("💼 Наши услуги", callback_data="services")],
            [InlineKeyboardButton("📁 Портфолио", callback_data="portfolio")],
            [InlineKeyboardButton("💰 Узнать стоимость", callback_data="price_request")],
            [InlineKeyboardButton("📞 Консультация", callback_data="consultation")],
            [InlineKeyboardButton("🌐 Наш сайт", url="https://gaan-developments.ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "👋 Добро пожаловать в *Gaan Developments*!\n\n"
            "Мы создаем современные сайты, которые приносят результат:\n"
            "• 🎯 Лендинги\n• 🛒 Интернет-магазины\n• 🏢 Корпоративные сайты\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# Обработка текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text
    
    if user_id not in user_requests:
        # Обычное сообщение - отправляем главное меню
        start(update, context)
        return
    
    request = user_requests[user_id]
    
    if request['step'] == 'name':
        request['name'] = text
        request['step'] = 'contact'
        update.message.reply_text(
            "Отлично! Теперь укажите ваш телефон или email для связи:"
        )
    
    elif request['step'] == 'contact':
        request['contact'] = text
        request['step'] = 'description'
        
        if request['type'] == 'consultation':
            update.message.reply_text(
                "Опишите ваш вопрос или проект. Что вас интересует?"
            )
        else:
            update.message.reply_text(
                "Опишите ваш проект. Какие задачи должен решать сайт?"
            )
    
    elif request['step'] == 'description':
        request['description'] = text
        
        # Отправляем заявку администратору
        send_request_to_admin(request, user_id, update.message.from_user.username, context)
        
        # Подтверждение пользователю
        keyboard = [
            [InlineKeyboardButton("💼 Наши услуги", callback_data="services")],
            [InlineKeyboardButton("📁 Портфолио", callback_data="portfolio")],
            [InlineKeyboardButton("🌐 Наш сайт", url="https://gaan-developments.ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "✅ *Спасибо за заявку!*\n\n"
            "Мы получили вашу заявку и свяжемся с вами в ближайшее время.\n\n"
            "Обычно мы отвечаем в течение 1-2 часов в рабочее время.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Очищаем данные пользователя
        if user_id in user_requests:
            del user_requests[user_id]

# Отправка заявки администратору
def send_request_to_admin(request, user_id, username, context):
    try:
        request_type = {
            'order': 'Заказ сайта',
            'price_request': 'Запрос стоимости', 
            'consultation': 'Консультация'
        }.get(request['type'], 'Заявка')
        
        service_names = {
            'landing': 'Лендинг',
            'shop': 'Интернет-магазин',
            'corporate': 'Корпоративный сайт',
            'improve': 'Доработка сайта'
        }
        
        service_info = ""
        if 'service' in request:
            service_info = f"\nУслуга: {service_names.get(request['service'], request['service'])}"
        
        message = (
            f"📨 *Новая заявка от @{username}*\n\n"
            f"Тип: {request_type}{service_info}\n"
            f"Имя: {request['name']}\n"
            f"Контакты: {request['contact']}\n"
            f"Описание: {request['description']}\n\n"
            f"ID пользователя: {user_id}"
        )
        
        # Отправляем сообщение администратору
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

# Команда для администратора
def admin_stats(update: Update, context: CallbackContext):
    if str(update.message.chat_id) != ADMIN_CHAT_ID:
        return
    
    stats_text = (
        f"📊 Статистика бота\n\n"
        f"Активные заявки: {len(user_requests)}\n"
        f"ID администратора: {ADMIN_CHAT_ID}"
    )
    
    update.message.reply_text(stats_text)

# Обработка ошибок
def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)

# Основная функция
def main():
    # Создаем updater
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Получаем dispatcher для регистрации обработчиков
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_stats))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error_handler)
    
    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
