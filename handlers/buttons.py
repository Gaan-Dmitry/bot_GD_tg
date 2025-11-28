from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services import SERVICES
from handlers.portfolio import show_portfolio_work, handle_portfolio_category

# Данные о пользователях (временное хранилище)
user_requests = {}

def button_handler(update, context):
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username
    
    if query.data == "services":
        show_services_menu(query)
    
    elif query.data == "portfolio":
        show_portfolio_menu(query)
    
    elif query.data.startswith("portfolio_"):
        category = query.data.replace("portfolio_", "")
        handle_portfolio_category(query, context, category)
    
    elif query.data == "price_request":
        start_price_request(user_id, username, query)
    
    elif query.data == "consultation":
        start_consultation(user_id, username, query)
    
    elif query.data.startswith("service_"):
        show_service_details(query)
    
    elif query.data.startswith("order_"):
        start_order(user_id, username, query)
    
    elif query.data == "portfolio_next":
        handle_portfolio_next(query, context)
    
    elif query.data == "portfolio_prev":
        handle_portfolio_prev(query, context)
    
    elif query.data == "back_to_main":
        from handlers.start import start
        start(update, context)

def show_services_menu(query):
    keyboard = [
        [InlineKeyboardButton("📰 Лендинг", callback_data="service_landing")],
        [InlineKeyboardButton("🛍 Интернет-магазин", callback_data="service_shop")],
        [InlineKeyboardButton("📝 Блог", callback_data="service_blog")],
        [InlineKeyboardButton("💬 Форум", callback_data="service_forum")],
        [InlineKeyboardButton("🏠 Корпоративный сайт", callback_data="service_corporate")],
        [InlineKeyboardButton("🛠 Веб инструмент", callback_data="service_tool")],
        [InlineKeyboardButton("🎨 Портфолио", callback_data="service_portfolio")],
        [InlineKeyboardButton("🎓 Обучающая платформа", callback_data="service_learning")],
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

def show_portfolio_menu(query):
    keyboard = [
        [InlineKeyboardButton("📰 Лендинги", callback_data="portfolio_landing")],
        [InlineKeyboardButton("🛍 Интернет-магазины", callback_data="portfolio_shop")],
        [InlineKeyboardButton("🏠 Корпоративные сайты", callback_data="portfolio_corporate")],
        [InlineKeyboardButton("🎓 Обучающие платформы", callback_data="portfolio_learning")],
        [InlineKeyboardButton("🎨 Портфолио", callback_data="portfolio_portfolio")],
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

def start_price_request(user_id, username, query):
    user_requests[user_id] = {
        'type': 'price_request', 
        'step': 'name',
        'user_id': user_id,
        'username': username
    }
    query.edit_message_text(
        "💰 *Расчет стоимости проекта*\n\n"
        "Давайте рассчитаем стоимость вашего сайта!\n\n"
        "Как вас зовут?",
        parse_mode='Markdown'
    )

def start_consultation(user_id, username, query):
    user_requests[user_id] = {
        'type': 'consultation', 
        'step': 'name',
        'user_id': user_id,
        'username': username
    }
    query.edit_message_text(
        "📞 *Бесплатная консультация*\n\n"
        "Я отвечу на все ваши вопросы о разработке сайта!\n\n"
        "Как вас зовут?",
        parse_mode='Markdown'
    )

def show_service_details(query):
    service_type = query.data.replace("service_", "")
    service = SERVICES.get(service_type, SERVICES["landing"])
    
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

def start_order(user_id, username, query):
    service_type = query.data.replace("order_", "")
    user_requests[user_id] = {
        'type': 'order', 
        'service': service_type, 
        'step': 'name',
        'user_id': user_id,
        'username': username
    }
    query.edit_message_text(
        "📝 *Оформление заявки*\n\n"
        "Отлично! Давайте оформим заявку на разработку.\n\n"
        "Как вас зовут?",
        parse_mode='Markdown'
    )

def handle_portfolio_next(query, context):
    works = context.user_data.get('portfolio_works', [])
    current_index = context.user_data.get('current_portfolio_index', 0)
    if current_index < len(works) - 1:
        context.user_data['current_portfolio_index'] = current_index + 1
        show_portfolio_work(query, context, current_index + 1)

def handle_portfolio_prev(query, context):
    works = context.user_data.get('portfolio_works', [])
    current_index = context.user_data.get('current_portfolio_index', 0)
    if current_index > 0:
        context.user_data['current_portfolio_index'] = current_index - 1
        show_portfolio_work(query, context, current_index - 1)
