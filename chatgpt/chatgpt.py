import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def ask_chatgpt(user_text, context=""):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Сен қазақ тілін үйрететін, сыпайы мұғалімсің. Тек қазақ тілінде жауап бер."},
            {"role": "assistant", "content": context},
            {"role": "user", "content": user_text}
        ]
    )
    return response.choices[0].message.content
