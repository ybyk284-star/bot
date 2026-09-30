import os
import requests
import telebot

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message, "أهلاً بك يا بطل! أرسل لي رابط تيك توك وسأقوم بتحميله فوراً 📥."
  )


@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def download_tiktok(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري التحميل يا بطل...")

  try:
    # استخدام هيدرز متصفح حقيقي بالكامل لتجاوز الحظر
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
            "Mobile/15E148 Safari/604.1"
        )
    }

    api_url = f"https://tikwm.com/api/?url={url}&hd=1"
    res = requests.get(api_url, headers=headers).json()

    if "data" in res and "play" in res["data"]:
      video_url = res["data"]["play"]
      cover_url = res["data"]["cover"]
      title = res["data"].get("title", "TikTok Video")

      if cover_url:
        bot.send_photo(
            message.chat.id,
            cover_url,
            caption=f"📝 **العنوان:** {title}",
            parse_mode="Markdown",
        )

      bot.send_video(
          message.chat.id, video_url, caption="✅ تم التحميل بنجاح يا بطل!"
      )
      bot.delete_message(message.chat.id, processing_msg.message_id)
    else:
      raise Exception("خطأ من السيرفر")

  except Exception as e:
    bot.edit_message_text(
        "❌ عذراً، حاول إرسال رابط تيك توك آخر مباشر.",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
  
