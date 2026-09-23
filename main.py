import os
from flask import Flask
import telebot
import threading

# توكن البوت الخاص بك يا يونس
TOKEN = "8266423475:AAFUyf5Ee6eWIPY2pWErii3HUm0M9JfDY6k"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running smoothly 24/7!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا يونس! البوت يعمل بقوة وسلاسة 24/7 🚀")

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port

