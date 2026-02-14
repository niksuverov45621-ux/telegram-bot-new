import os
import logging
from flask import Flask, request
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID')

# Проверка наличия токена
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    exit(1)

app = Flask(__name__)

def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """Отправка сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return None

@app.route('/')
def home():
    return "🤖 Бот работает! Статус: ONLINE"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook от Telegram"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            user = message.get('from', {})
            text = message.get('text', '')
            chat_id = message.get('chat', {}).get('id')
            
            user_id = user.get('id')
            # Формируем имя пользователя: first_name + last_name (если есть)
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip() or "без имени"
            username = user.get('username')
            
            # Логируем
            logger.info(f"Сообщение от {user_id} ({full_name}): {text}")
            
            # Команда /start
            if text == '/start':
                send_telegram_message(
                    chat_id,
                    "👋 Привет! Я бот для связи. Просто напишите сообщение, и я перешлю его администратору."
                )
                return 'ok'
            
            # Создаем кликабельную ссылку на пользователя (работает в Telegram)
            # Если есть username, можно использовать https://t.me/username, иначе tg://user?id=...
            if username:
                user_link = f"<a href=\"https://t.me/{username}\">{full_name}</a>"
            else:
                user_link = f"<a href=\"tg://user?id={user_id}\">{full_name}</a>"
            
            # Формируем сообщение для админа
            admin_message = (
                f"📨 <b>Новое сообщение</b>\n"
                f"👤 От: {user_link}\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"💬 Текст:\n{text}"
            )
            
            # Отправляем админу
            send_telegram_message(ADMIN_ID, admin_message)
            
            # Подтверждаем пользователю
            send_telegram_message(chat_id, "✅ Ваше сообщение отправлено администратору!")
        
        return 'ok'
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка webhook через Telegram API"""
    webhook_url = f"https://{request.host}/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('ok'):
            return f"✅ Webhook установлен: {webhook_url}"
        else:
            return f"❌ Ошибка: {result.get('description')}"
    except Exception as e:
        return f"❌ Ошибка при установке webhook: {e}"

@app.route('/health', methods=['GET'])
def health():
    return {"status": "healthy", "python": "3.13.4"}

@app.route('/info', methods=['GET'])
def info():
    return {
        "service": "telegram-bot",
        "url": f"https://{request.host}",
        "admin_id": ADMIN_ID,
        "bot_token_set": bool(BOT_TOKEN)
    }

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """Удаление webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)
    result = response.json()
    
    if result.get('ok'):
        return "✅ Webhook удален"
    else:
        return f"❌ Ошибка: {result.get('description')}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
