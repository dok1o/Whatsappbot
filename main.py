from flask import Flask, request
import requests
import os
from scenarios.scenarios import SCENARIOS
from chatgpt.chatgpt import ask_chatgpt

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")

WELCOME_TEXT = "👋 *Сәлеметсің бе!* ..."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        messages = data.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
        if not messages: return "ok", 200

        msg = messages[0]
        text = msg.get("text", {}).get("body", "").strip()
        sender = msg.get("from")
        if not text or not sender: return "ok", 200

        if text in SCENARIOS:
            reply = SCENARIOS[text] + "\n\n✍️ Енді өзің жауап беріп көр!"
        elif text.lower() in ["сәлем", "салам", "hi", "hello"]:
            reply = WELCOME_TEXT
        else:
            reply = ask_chatgpt(text, "Біз қазақ тілін үйреніп жатырмыз.")

        url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {"messaging_product": "whatsapp", "to": sender, "text": {"body": reply}}
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print("ERROR:", e)
    return "ok", 200

@app.route("/")
def home():
    return "Қазақша WhatsApp-бот жұмыс істеп тұр 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
