import os
import telebot
import yt_dlp

TOKEN = "8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا يونس! أرسل لي رابط فيديو من تيك توك أو إنستجرام وسأقوم"
      " بتحميله لك فوراً 📥.",
  )


@bot.message_handler(
    func=lambda message: "tiktok.com" in message.text
    or "instagram.com" in message.text
)
def download_media(message):
  url = message.text.strip()
  processing_msg = bot.reply_to(message, "⏳ جاري جلب المعلومات وتحميل الفيديو...")

  # إعدادات قوية لتجاوز الحماية ومنع حظر تيك توك
  ydl_opts = {
      "format": "best",
      "outtmpl": "downloaded_video.mp4",
      "quiet": True,
      "nocheckcertificate": True,
      "http_headers": {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
          ),
          "Accept-Language": "en-US,en;q=0.9",
      },
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      video_title = info.get("title", "Media Video")
      thumbnail_url = info.get("thumbnail", "")
      ydl.download([url])

    if thumbnail_url and "tiktok.com" in url:
      bot.send_photo(
          message.chat.id,
          thumbnail_url,
          caption=f"📝 **العنوان:** {video_title}",
          parse_mode="Markdown",
      )

    with open("downloaded_video.mp4", "rb") as video_file:
      bot.send_video(
          message.chat.id,
          video_file,
          caption="✅ تم تحميل الفيديو بنجاح يا بطل!",
      )

    if os.path.exists("downloaded_video.mp4"):
      os.remove("downloaded_video.mp4")

    bot.delete_message(message.chat.id, processing_msg.message_id)

  except Exception as e:
    bot.edit_message_text(
        "❌ عذراً، تيك توك يحظر الرابط حالياً أو يحتاج وقت. جرب فيديو آخر.",
        message.chat.id,
        processing_msg.message_id,
    )


if __name__ == "__main__":
  bot.infinity_polling()
  
