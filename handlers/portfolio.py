from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_portfolio_works

def show_portfolio_work(query, context, index):
    """Показывает работу из портфолио"""
    works = context.user_data.get('portfolio_works', [])
    if not works or index >= len(works):
        query.edit_message_text("Работы не найдены.")
        return
    
    work = works[index]
    
    # Создаем клавиатуру навигации
    keyboard = []
    nav_buttons = []
    
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data="portfolio_prev"))
    if index < len(works) - 1:
        if nav_buttons:
            nav_buttons.append(InlineKeyboardButton("Следующая ➡️", callback_data="portfolio_next"))
        else:
            nav_buttons = [InlineKeyboardButton("Следующая ➡️", callback_data="portfolio_next")]
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.extend([
        [InlineKeyboardButton("📁 Вернуться к категориям", callback_data="portfolio")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формируем сообщение с уникальным содержимым
    message = f"*{work['title']}*\n\n"
    message += f"*Категория:* {work['category']}\n\n"
    message += f"*Описание:*\n{work['description']}\n\n"
    
    if work.get('webarchive'):
        message += f"[🌐 Посмотреть на WebArchive]({work['webarchive']})"
    
    # Добавляем номер работы для уникальности
    message += f"\n\n_Работа {index + 1} из {len(works)}_"
    
    try:
        query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        if "Message is not modified" in str(e):
            # Если сообщение не изменилось, пробуем добавить немного разного контента
            try:
                message += "\n🔄"
                query.edit_message_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            except Exception as e2:
                print(f"Не удалось обновить сообщение портфолио: {e2}")
        else:
            print(f"Ошибка при редактировании сообщения портфолио: {e}")

def handle_portfolio_category(query, context, category):
    """Обрабатывает выбор категории портфолио"""
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
