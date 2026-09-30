import os
import telebot
import yt_dlp

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا بطل! أرسل لي رابط أي فيديو تيك توك وسأقوم بتحميله لك بدون"
      " علامة مائية مع الصورة الخاصة به 📥.",
  )


@bot.message_handler(func=lambda message: "tiktok.com" in message.text)
def download_tiktok(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري جلب المعلومات وتحميل الفيديو...")

  ydl_opts = {
      "format": "best",
      "outtmpl": "tiktok_video.mp4",
      "quiet": True,
      "http_headers": {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          )
      },
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
          caption="✅ تم التنزيل بنجاح بدون علامة مائية!",
      )

    if os.path.exists("tiktok_video.mp4"):
      os.remove("tiktok_video.mp4")

    bot.delete_message(message.chat.id, processing_msg.message_id)

  except Exception as e:
    bot.edit_message_text(
        f"❌ عذراً، حدث خطأ أو أن الرابط محظور حالياً: {str(e)}",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
  
