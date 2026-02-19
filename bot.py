import os
import sys
import logging
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8340258435:AAH0f7SFjrLm1x3utfzHEfGxbAmPF0oH8t0')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8529480073'))

# ===== Flask-сервер для пингов =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Запускаем Flask в отдельном потоке
threading.Thread(target=run_flask, daemon=True).start()

# ===== ЛОГИРОВАНИЕ =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ===== ФУНКЦИИ БОТА =====
def start(update, context):
    user = update.message.from_user
    update.message.reply_text(f"👋 Привет, {user.first_name}! Я бот на Render.com 24/7!")
    logger.info(f"Новый пользователь: {user.id}")

def forward_message(update, context):
    user = update.message.from_user
    text = update.message.text
    
    logger.info(f"Сообщение от {user.first_name}: {text[:100]}...")
    
    context.bot.send_message(
        ADMIN_ID,
        f"📨 От: {user.first_name}\n"
        f"👤 @{user.username or 'нет'}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 {text}"
    )
    
    update.message.reply_text("✅ Отправлено!")

# ===== ЗАПУСК =====
print("=" * 50)
print("🤖 TELEGRAM BOT ON RENDER.COM")
print("=" * 50)

updater = Updater(BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))

print("✅ Бот запущен на Render.com!")
print("⏰ Работает 24/7")
print("=" * 50)

updater.start_polling()
updater.idle()
