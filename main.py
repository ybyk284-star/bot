import os
import requests
import telebot

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا يونس! أرسل لي رابط تيك توك وسأقوم بتحميله لك فوراً وبأعلى"
      " جودة 📥.",
  )


@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def download_tiktok(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو...")

  try:
    # خطوة مهمة: فك الرابط المختصر (vt.tiktok.com) للحصول على الرابط الأصلي الطويل
    if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
      session = requests.Session()
      response = session.head(url, allow_redirects=True)
      url = response.url

    # إرسال الرابط الحقيقي للـ API الخاص بالتيك توك
    api_url = f"https://tikwm.com/api/?url={url}"
    res = requests.get(api_url).json()

    if "data" in res and "play" in res["data"]:
      video_url = res["data"]["play"]
      cover_url = res["data"]["cover"]
      title = res["data"].get("title", "TikTok Video")

      # إرسال الصورة البارزة (Thumbnail) إذا وجدت مع العنوان
      if cover_url:
        bot.send_photo(
            message.chat.id,
            cover_url,
            caption=f"📝 **العنوان:** {title}",
            parse_mode="Markdown",
        )

      # إرسال الفيديو بدون علامة مائية
      bot.send_video(
          message.chat.id, video_url, caption="✅ تم التحميل بنجاح 🎯"
      )

      # حذف رسالة الانتظار
      bot.delete_message(message.chat.id, processing_msg.message_id)
    else:
      raise Exception("فشل التحميل من الـ API")

  except Exception as e:
    bot.edit_message_text(
        "❌ عذراً، لم أتمكن من تحميل هذا الرابط. جرب رابطاً آخر.",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
  
