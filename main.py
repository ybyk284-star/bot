import os
import requests
import telebot

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا بطل! أرسل لي رابط تيك توك أو إنستجرام وسأقوم بتحميله لك"
      " فوراً 📥.",
  )


@bot.message_handler(
    func=lambda message: "tiktok.com" in message.text
    or "instagram.com" in message.text
)
def download_media(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري تحميل الفيديو والصورة...")

  try:
    # إذا كان الرابط تيك توك، نستخدم الـ API السريع والمباشر
    if "tiktok.com" in url:
      api_url = f"https://tikwm.com/api/?url={url}"
      res = requests.get(api_url).json()

      if "data" in res and "play" in res["data"]:
        video_url = res["data"]["play"]
        cover_url = res["data"]["cover"]
        title = res["data"].get("title", "TikTok Video")

        # إرسال الصورة البارزة مع العنوان
        if cover_url:
          bot.send_photo(
              message.chat.id,
              cover_url,
              caption=f"📝 **العنوان:** {title}",
              parse_mode="Markdown",
          )

        # إرسال الفيديو بدون علامة مائية
        bot.send_video(
            message.chat.id,
            video_url,
            caption="✅ تم التحميل بنجاح بدون علامة مائية!",
        )
        bot.delete_message(message.chat.id, processing_msg.message_id)
      else:
        raise Exception("فشل جلب بيانات تيك توك")

    else:
      # إذا كان إنستجرام، نترك الكود الخاص به أو نستخدم الطريقة العادية
      bot.edit_message_text(
          "❌ عذراً، ركز معي حالياً على روابط تيك توك أو جرب رابط تيك توك"
          " آخر.",
          message.chat.id,
          processing_msg.message_id,
      )

  except Exception as e:
    bot.edit_message_text(
        "❌ حدث خطأ أثناء التحميل. تأكد أن الرابط صحيح.",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
  
