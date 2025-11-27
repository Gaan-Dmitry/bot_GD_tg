import os
import logging
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', '8501378717:AAGhzm-krzKpqBwxG_vB37dQvLkEeD_3cW8')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6297103998')

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',
    'database': 'u3299512_gaan-developments',
    'user': 'u3299512_default',  # замените на вашего пользователя БД
    'password': 'your_password_here'  # замените на ваш пароль БД
}

# Данные о пользователях
user_requests = {}

# Функции для работы с БД
def get_db_connection():
    """Создает подключение к базе данных"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        return None

def save_bot_request(request_data):
    """Сохраняет заявку из бота в базу данных"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Маппинг типов услуг для БД
        service_mapping = {
            'landing': 'landing',
            'shop': 'shop', 
            'corporate': 'corporate',
            'improve': 'landing'  # доработка сайта -> лендинг
        }
        
        site_type = service_mapping.get(request_data.get('service', ''), 'landing')
        
        # Извлекаем контактные данные
        contact_info = request_data.get('contact', '')
        email = contact_info if '@' in contact_info else ''
        phone = contact_info if '@' not in contact_info else ''
        
        query = """
        INSERT INTO requests (site_type, design, content, support, budget, details, name, email, phone, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        values = (
            site_type,
            'need',  # по умолчанию нужен дизайн
            'provide',  # по умолчанию предоставим контент
            'maintenance',  # по умолчанию с поддержкой
            'under_30',  # бюджет по умолчанию
            request_data.get('description', ''),
            request_data.get('name', ''),
            email,
            phone
        )
        
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Заявка сохранена в БД для пользователя {request_data.get('name')}")
        return True
        
    except mysql.connector.Error as e:
        logger.error(f"Ошибка сохранения заявки в БД: {e}")
        if conn:
            conn.close()
        return False

def get_portfolio_works(category_key=None):
    """Получает работы из портфолио из БД"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Маппинг категорий для БД
        category_mapping = {
            'landing': 'Лендинг',
            'shop': 'Интернет-магазин',
            'corporate': 'Корпоративный сайт',
            'learning': 'Обучающая платформа'
        }
        
        if category_key and category_key in category_mapping:
            category_filter = category_mapping[category_key]
            query = "SELECT * FROM works WHERE category = %s ORDER BY id DESC"
            cursor.execute(query, (category_filter,))
        else:
            query = "SELECT * FROM works ORDER BY id DESC"
            cursor.execute(query)
        
        works = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return works
        
    except mysql.connector.Error as e:
        logger.error(f"Ошибка получения портфолио из БД: {e}")
        if conn:
            conn.close()
        return []

# Команда /start
def start(update, context):
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
def button_handler(update, context):
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
            [InlineKeyboardButton("🌐 Все работы", callback_data="portfolio_all")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "📁 *Наше портфолио*\n\n"
            "Выберите категорию для просмотра работ:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("portfolio_"):
        category = query.data.replace("portfolio_", "")
        works = get_portfolio_works(category if category != 'all' else None)
        
        if not works:
            query.edit_message_text(
                "В этой категории пока нет работ.\n\n"
                "Посмотрите другие категории или свяжитесь с нами для обсуждения вашего проекта!",
                parse_mode='Markdown'
            )
            return
        
        # Показываем первую работу с навигацией
        context.user_data['current_portfolio_index'] = 0
        context.user_data['portfolio_works'] = works
        show_portfolio_work(query, context, 0)
    
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
            [InlineKeyboardButton("💰 Заказать расчет", callback_data="order_" + service_type)],
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
    
    elif query.data == "portfolio_next":
        works = context.user_data.get('portfolio_works', [])
        current_index = context.user_data.get('current_portfolio_index', 0)
        if current_index < len(works) - 1:
            context.user_data['current_portfolio_index'] = current_index + 1
            show_portfolio_work(query, context, current_index + 1)
    
    elif query.data == "portfolio_prev":
        works = context.user_data.get('portfolio_works', [])
        current_index = context.user_data.get('current_portfolio_index', 0)
        if current_index > 0:
            context.user_data['current_portfolio_index'] = current_index - 1
            show_portfolio_work(query, context, current_index - 1)
    
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

def show_portfolio_work(query, context, index):
    """Показывает работу из портфолио"""
    works = context.user_data.get('portfolio_works', [])
    if not works or index >= len(works):
        query.edit_message_text("Работы не найдены.")
        return
    
    work = works[index]
    
    # Создаем клавиатуру навигации
    keyboard = []
    if index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Предыдущая", callback_data="portfolio_prev")])
    if index < len(works) - 1:
        if keyboard:
            keyboard[-1].append(InlineKeyboardButton("Следующая ➡️", callback_data="portfolio_next"))
        else:
            keyboard.append([InlineKeyboardButton("Следующая ➡️", callback_data="portfolio_next")])
    
    keyboard.extend([
        [InlineKeyboardButton("📁 Вернуться к категориям", callback_data="portfolio")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формируем сообщение
    message = f"*{work['title']}*\n\n"
    message += f"*Категория:* {work['category']}\n\n"
    message += f"*Описание:*\n{work['description']}\n\n"
    
    if work.get('webarchive'):
        message += f"[🌐 Посмотреть на WebArchive]({work['webarchive']})"
    
    query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# Обработка текстовых сообщений
def handle_message(update, context):
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
        
        # Сохраняем заявку в БД
        save_bot_request(request)
        
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

# Обработка ошибок
def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)

# Основная функция
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
