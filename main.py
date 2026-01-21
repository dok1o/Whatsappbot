from flask import Flask, request
import requests
import os
import openai

# ======================
# ⚙️ APP INIT
# ======================
app = Flask(__name__)

# ======================
# 🔐 ENV (Render)
# ======================
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# ======================
# 📚 СЦЕНАРИИ (1–10)
# ======================
SCENARIOS = {
    "1": """🛒 *Дүкенде*
— Сәлеметсіз бе, сізге не керек?
— Сәлеметсіз бе, маған нан мен сүт керек.
— Нанның қай түрін аласыз?
— Қара нанды алыңызшы.
— Барлығы қанша тұрады?
— Барлығы 650 теңге болады.""",

    "2": """🏫 *Мектепте*
— Бүгін қандай сабақтар бар?
— Бүгін математика мен қазақ тілі бар.
— Қазақ тілінен не өттік?
— Диалог құру тақырыбын өттік.
— Үй тапсырмасы көп пе?
— Орташа, жасауға болады.""",

    "3": """🏠 *Қонақта*
— Қош келдіңіз, жолыңыз қалай болды?
— Рахмет, жол жақсы болды.
— Шай немесе қымыз ішесіз бе?
— Шай ішемін, рахмет.
— Тағам ұнады ма?
— Иә, өте дәмді екен.""",

    "4": """🚌 *Қоғамдық көлікте*
— Кешіріңіз, бұл автобус орталыққа бара ма?
— Иә, барады.
— Қанша уақытта жетеміз?
— Шамамен 20 минутта.
— Мен қай аялдамадан түсуім керек?
— «Бәйтерек» аялдамасынан.""",

    "5": """👫 *Достармен кездесу*
— Бүгін не істейміз?
— Киноға барсақ қалай?
— Қандай фильм көргіміз келеді?
— Комедия көрейік.
— Қай уақытта кездесеміз?
— Сағат жетіде.""",

    "6": """🩺 *Дәрігерде*
— Сізге не болды?
— Басым ауырып жүр.
— Қанша күн болды?
— Үш күндей болды.
— Температураңыз бар ма?
— Жоқ, жоқ сияқты.""",

    "7": """☀️ *Ауа райы*
— Бүгін ауа райы қандай?
— Бүгін күн жылы.
— Жел бар ма?
— Жоқ, жел жоқ.
— Серуендеуге шығамыз ба?
— Иә, жақсы идея.""",

    "8": """✈️ *Саяхат*
— Соңғы рет қайда бардың?
— Алматыға бардым.
— Қала ұнады ма?
— Иә, өте әдемі.
— Қай жерін көрдің?
— Медеу мен Көк-Төбені.""",

    "9": """🎉 *Ұлттық дәстүрлер*
— Сен Наурызды қалай тойлайсың?
— Отбасыммен бірге тойлаймын.
— Қандай тағам дайындалады?
— Наурыз көже.
— Қонақтар келеді ме?
— Иә, көршілер келеді.""",

    "10": """🚀 *Болашақ жоспарлар*
— Болашақта кім болғың келеді?
— Бағдарламашы болғым келеді.
— Неге осы мамандықты таңдадың?
— Себебі ол қызық.
— Қай жерде оқығың келеді?
— Қазақстанда оқығым келеді."""
}

WELCOME_TEXT = """👋 *Сәлеметсің бе!*

Мен — қазақ тілін үйренуге көмектесетін *WhatsApp-ботпын* 🇰🇿  

📌 *Жағдайды таңда:*
1️⃣ Дүкенде  
2️⃣ Мектепте  
3️⃣ Қонақта  
4️⃣ Қоғамдық көлікте  
5️⃣ Достармен кездесу  
6️⃣ Дәрігерде  
7️⃣ Ауа райы  
8️⃣ Саяхат  
9️⃣ Ұлттық дәстүрлер  
🔟 Болашақ жоспарлар  

👉 *Тек санын жібер (1–10)*"""

# ======================
# 🤖 CHATGPT
# ======================
def ask_chatgpt(user_text, context=""):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Сен қазақ тілін үйрететін, сыпайы мұғалімсің. Тек қазақ тілінде жауап бер."
            },
            {
                "role": "assistant",
                "content": context
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )
    return response.choices[0].message.content

# ======================
# 📩 WEBHOOK
# ======================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        entry = data.get("entry", [])
        if not entry:
            return "ok", 200

        changes = entry[0].get("changes", [])
        value = changes[0].get("value", {})
        messages = value.get("messages")

        if not messages:
            return "ok", 200

        msg = messages[0]
        text = msg.get("text", {}).get("body", "").strip()
        sender = msg.get("from")

        if not text or not sender:
            return "ok", 200

        # 🟢 ЛОГИКА
        if text in SCENARIOS:
            reply = SCENARIOS[text] + "\n\n✍️ Енді өзің жауап беріп көр!"
            context = SCENARIOS[text]

        elif text.lower() in ["сәлем", "салам", "hi", "hello"]:
            reply = WELCOME_TEXT
            context = ""

        else:
            reply = ask_chatgpt(text, "Біз қазақ тілін үйреніп жатырмыз.")

        # 📤 ОТПРАВКА В WHATSAPP
        url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "text": {"body": reply}
        }

        requests.post(url, json=payload, headers=headers)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200

# ======================
# 🏠 HOME
# ======================
@app.route("/")
def home():
    return "Қазақша WhatsApp-бот жұмыс істеп тұр 🚀"

# ======================
# ▶️ RUN
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
