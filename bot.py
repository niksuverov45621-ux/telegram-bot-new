import os
import sys
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8340258435:AAH0f7SFjrLm1x3utfzHEfGxbAmPF0oH8t0')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '8529480073'))

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
    update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n"
        f"Это бот, созданный для связи с администратором.\n"
        f"Как только вы напишете сообщение, я тут же передам его администратору."
    )
    logger.info(f"Новый пользователь: {user.id}")

def forward_message(update, context):
    user = update.message.from_user
    text = update.message.text
    logger.info(f"Сообщение от {user.first_name}: {text[:100]}...")

    # Кнопка "НАПИСАТЬ"
    keyboard = [[InlineKeyboardButton("📝 НАПИСАТЬ", url=f"tg://user?id={user.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    admin_message = (
        f"📨 *Новое сообщение*\n\n"
        f"*От:* {user.first_name}\n"
        f"*ID:* `{user.id}`\n"
    )
    if user.username:
        admin_message += f"*Username:* @{user.username}\n"
    admin_message += f"\n*Текст:*\n{text}"

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    update.message.reply_text("✅ Сообщение отправлено администратору!")

# ===== ЗАПУСК =====
def main():
    print("=" * 50)
    print("🤖 TELEGRAM BOT ON RENDER")
    print("=" * 50)

    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))

    updater.start_polling()
    print("✅ Бот запущен и работает 24/7")
    print("=" * 50)
    updater.idle()

if __name__ == '__main__':
    main()
