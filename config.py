import os
import pymysql.cursors

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8501378717:AAGhzm-krzKpqBwxG_vB37dQvLkEeD_3cW8')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6297103998')

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',
    'database': 'u3299512_gaan-developments',
    'user': 'u3299512_gaan-dmitry',
    'password': 'yZU-gQW-cET-qVK',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # Исправлено - класс, а не строка
}