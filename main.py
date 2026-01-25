import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from chatgpt.chatgpt import ask_chatgpt
from scenarios.scenarios import SCENARIOS

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://whatsapp-ai-bot-uk0w.onrender.com

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Сәлем! Бот работает.")
    
# Любое сообщение
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if user_text in SCENARIOS:
        reply = SCENARIOS[user_text] + "\n\n✍️ Енді өзің жауап беріп көр!"
    else:
        reply = ask_chatgpt(user_text, "Біз қазақ тілін үйреніп жатырмыз.")
    await update.message.reply_text(reply)

# Создаём приложение Telegram
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Устанавливаем webhook
webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
app.bot.set_webhook(webhook_url)
print(f"Webhook установлен: {webhook_url}")

# Запуск webhook сервера на Render
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=BOT_TOKEN,
    webhook_url=webhook_url
)

