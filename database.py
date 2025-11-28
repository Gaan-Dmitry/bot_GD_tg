import pymysql
import uuid
from config import DB_CONFIG

def get_db_connection():
    """Создает подключение к базе данных"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

def save_bot_request(request_data, user_id=None, username=None):
    """Сохраняет заявку из бота в базу данных"""
    conn = get_db_connection()
    if not conn:
        print("Не удалось подключиться к БД")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Правильный маппинг типов услуг для БД
            service_mapping = {
                'landing': 'landing',
                'shop': 'shop', 
                'corporate': 'corporate',
                'blog': 'blog',
                'forum': 'forum', 
                'tool': 'tool',
                'portfolio': 'portfolio',
                'learning': 'learning',
                'improve': 'improve'
            }
            
            # Получаем тип услуги из заявки
            service_type = request_data.get('service', '')
            site_type = service_mapping.get(service_type, 'other')
            
            # Извлекаем контактные данные
            contact_info = request_data.get('contact', '')
            email = contact_info if '@' in contact_info else ''
            phone = contact_info if '@' not in contact_info else ''
            
            # Генерируем уникальный ID
            unique_id = str(uuid.uuid4())
            
            # Определяем тип заявки
            request_type = request_data.get('type', 'consultation')
            
            query = """
            INSERT INTO requests (
                site_type, design, content, support, budget, details, 
                name, email, phone, request_source, request_type, 
                unique_id, telegram_user_id, telegram_username, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                site_type,
                'need',
                'provide', 
                'maintenance',
                'under_30',
                request_data.get('description', ''),
                request_data.get('name', ''),
                email,
                phone,
                'telegram',
                request_type,
                unique_id,
                user_id,
                username
            )
            
            cursor.execute(query, values)
            conn.commit()
            print(f"Заявка сохранена в БД: тип={site_type}, заявка={request_type}, ID={unique_id}")
            return unique_id
            
    except pymysql.Error as e:
        print(f"Ошибка сохранения заявки в БД: {e}")
        return False
    finally:
        conn.close()

def get_portfolio_works(category_key=None):
    """Получает работы из портфолио из БД"""
    conn = get_db_connection()
    if not conn:
        print("Не удалось подключиться к БД для получения портфолио")
        return []
    
    try:
        with conn.cursor() as cursor:
            category_mapping = {
                'landing': 'Лендинг',
                'shop': 'Интернет-магазин',
                'corporate': 'Корпоративный сайт',
                'learning': 'Обучающая платформа',
                'portfolio': 'Портфолио'
            }
            
            if category_key and category_key in category_mapping:
                category_filter = category_mapping[category_key]
                query = "SELECT * FROM works WHERE category = %s ORDER BY id DESC"
                cursor.execute(query, (category_filter,))
            else:
                query = "SELECT * FROM works ORDER BY id DESC"
                cursor.execute(query)
            
            works = cursor.fetchall()
            print(f"Получено {len(works)} работ из портфолио")
            return works
            
    except pymysql.Error as e:
        print(f"Ошибка получения портфолио из БД: {e}")
        return []
    finally:
        conn.close()