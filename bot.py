import os
import sys
import logging
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8340258435:AAH0f7SFjrLm1x3utfzHEfGxbAmPF0oH8t0')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8529480073'))

# ===== Flask-сервер для пингов (чтобы Render не "усыплял" бота) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running on Render.com!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

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
    """Обработчик команды /start"""
    user = update.message.from_user
    update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n"
        f"Это бот, созданный для связи с администратором.\n"
        f"Как только вы напишете сообщение, я тут же передам его администратору."
    )
    logger.info(f"Новый пользователь: {user.id}")

def forward_message(update, context):
    """Пересылает сообщение пользователя администратору"""
    user = update.message.from_user
    text = update.message.text

    logger.info(f"Сообщение от {user.first_name}: {text[:100]}...")

    # Создаём кнопку "НАПИСАТЬ", ведущую прямо в чат с пользователем
    keyboard = [[InlineKeyboardButton("📝 НАПИСАТЬ", url=f"tg://user?id={user.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Формируем простое текстовое сообщение
    admin_message = (
        f"📨 *Новое сообщение*\n\n"
        f"*От:* {user.first_name}\n"
        f"*ID:* `{user.id}`\n"
    )
    # Добавляем username, если он есть (но можно и не добавлять)
    if user.username:
        admin_message += f"*Username:* @{user.username}\n"
    admin_message += f"\n*Текст:*\n{text}"

    # Отправляем администратору вместе с кнопкой
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    # Подтверждение пользователю
    update.message.reply_text("✅ Сообщение отправлено администратору!")

# ===== ЗАПУСК =====
def main():
    print("=" * 50)
    print("🤖 TELEGRAM BOT ON RENDER.COM")
    print("=" * 50)

    # Создаём бота
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрируем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))

    # Запускаем поллинг
    updater.start_polling()
    print("✅ Бот запущен на Render.com!")
    print("⏰ Работает 24/7 (Flask-сервер для пингов активен)")
    print("=" * 50)

    # Блокируем поток, пока бот не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
