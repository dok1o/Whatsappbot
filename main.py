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
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))  # Render назначает порт через переменную окружения

# Flask сервер
flask_app = Flask(__name__)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Сәлеметсің бе!\n\n"
        "Мен — қазақ тілін үйрететін ИИ ботпын 🇰🇿\n\n"
        "📌 Төмендегі жағдайлардың бірін таңда:\n"
        "1️⃣ Дүкенде\n"
        "2️⃣ Мектепте\n"
        "3️⃣ Қонақта\n"
        "4️⃣ Қоғамдық көлікте\n"
        "5️⃣ Достармен кездесу\n"
        "6️⃣ Дәрігерде\n"
        "7️⃣ Ауа райы\n"
        "8️⃣ Саяхат\n"
        "9️⃣ Ұлттық дәстүрлер\n"
        "🔟 Болашақ жоспарлар\n\n"
        "👉 Тек санын жібер (1–10)"
    )
    await update.message.reply_text(text)

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

# Flask endpoint для Telegram webhook
@flask_app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    from telegram import Update
    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "ok"

# Настройка webhook на старт
def set_webhook():
    url = os.environ.get("WEBHOOK_URL")
    if url:
        webhook_url = f"{url}/webhook/{BOT_TOKEN}"  # теперь точно совпадает
        app.bot.set_webhook(webhook_url)
        print(f"Webhook установлен: {webhook_url}")

# Запуск Flask сервера
if __name__ == "__main__":
    set_webhook()
    PORT = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=PORT)
