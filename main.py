import os
import telebot
import yt_dlp

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك! أرسل لي رابط أي فيديو تيك توك وسأقوم بتحميله لك بدون علامة"
      " مائية مع الصورة الخاصة به 📥.",
  )


@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def download_tiktok(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري جلب المعلومات وتحميل الفيديو...")

  ydl_opts = {
      "format": "best",
      "outtmpl": "tiktok_video.mp4",
      "quiet": True,
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      video_title = info.get("title", "TikTok Video")
      thumbnail_url = info.get("thumbnail", "")
      ydl.download([url])

    if thumbnail_url:
      bot.send_photo(
          message.chat.id,
          thumbnail_url,
          caption=f"📝 **العنوان:** {video_title}",
          parse_mode="Markdown",
      )

    with open("tiktok_video.mp4", "rb") as video_file:
      bot.send_video(
          message.chat.id,
          video_file,
          caption="✅ تم التنزيل بنجاح بواسطة البوت الخاص بك.",
      )

    if os.path.exists("tiktok_video.mp4"):
      os.remove("tiktok_video.mp4")

    bot.delete_message(message.chat.id, processing_msg.message_id)

  except Exception as e:
    bot.edit_message_text(
        f"❌ حدث خطأ أثناء التحميل: {str(e)}",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
    
