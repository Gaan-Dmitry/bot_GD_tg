from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💼 Наши услуги", callback_data="services")],
        [InlineKeyboardButton("📁 Портфолио", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Узнать стоимость", callback_data="price_request")],
        [InlineKeyboardButton("📞 Консультация", callback_data="consultation")],
        [InlineKeyboardButton("🌐 Наш сайт", url="https://gaan-developments.ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        update.message.reply_text(
            "👋 Добро пожаловать в *Gaan Developments*!\n\n"
            "Мы создаем современные сайты, которые приносят результат!\n\n"
            "Я помогу вам:\n"
            "• Узнать о наших услугах и ценах\n• Посмотреть примеры работ\n"
            "• Получить консультацию\n• Оставить заявку на разработку\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        query = update.callback_query
        query.edit_message_text(
            "👋 Добро пожаловать в *Gaan Developments*!\n\n"
            "Мы создаем современные сайты, которые приносят результат!\n\n"
            "Я помогу вам:\n"
            "• Узнать о наших услугах и ценах\n• Посмотреть примеры работ\n"
            "• Получить консультацию\n• Оставить заявку на разработку\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
