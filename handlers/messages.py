from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import save_bot_request
from handlers.buttons import user_requests
from handlers.start import start
from config import ADMIN_CHAT_ID

def handle_message(update, context):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
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
        unique_id = save_bot_request(request, user_id, username)
        
        if unique_id:
            # Отправляем заявку администратору
            send_request_to_admin(request, unique_id, context)
            
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
        else:
            update.message.reply_text(
                "❌ *Произошла ошибка при сохранении заявки.*\n\n"
                "Пожалуйста, попробуйте еще раз или свяжитесь с нами другим способом.",
                parse_mode='Markdown'
            )
        
        # Очищаем данные пользователя
        if user_id in user_requests:
            del user_requests[user_id]

def send_request_to_admin(request, unique_id, context):
    try:
        request_type_names = {
            'order': 'Заказ сайта',
            'price_request': 'Запрос стоимости', 
            'consultation': 'Консультация'
        }
        
        request_type = request_type_names.get(request['type'], 'Заявка')
        
        service_info = ""
        if 'service' in request:
            from services import SERVICES
            service_name = SERVICES.get(request['service'], {}).get('name', request['service'])
            service_info = f"\nУслуга: {service_name}"
        
        # Экранируем специальные символы Markdown
        def escape_markdown(text):
            if not text:
                return ""
            escape_chars = r'_*[]()~`>#+-=|{}.!'
            return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))
        
        message = (
            f"📨 *Новая заявка из Telegram*\n\n"
            f"Тип: {escape_markdown(request_type)}{escape_markdown(service_info)}\n"
            f"ID заявки: `{unique_id}`\n"
            f"Имя: {escape_markdown(request['name'])}\n"
            f"Контакты: {escape_markdown(request['contact'])}\n"
            f"Описание: {escape_markdown(request['description'])}\n\n"
            f"Пользователь: @{escape_markdown(request.get('username', 'N/A'))}\n"
            f"ID пользователя: {escape_markdown(request.get('user_id', 'N/A'))}"
        )
        
        # Отправляем сообщение администратору
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='MarkdownV2'
        )
        print(f"Уведомление отправлено администратору для заявки {unique_id}")
        
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")