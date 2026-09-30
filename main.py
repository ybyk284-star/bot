import os
import logging
import time
import requests
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def self_ping():
    app_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:10000")
    while True:
        try:
            if "onrender.com" in app_url:
                requests.get(app_url, timeout=10)
        except Exception:
            pass
        time.sleep(240)

def keep_alive():
    t1 = Thread(target=run_web)
    t1.start()
    t2 = Thread(target=self_ping)
    t2.start()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت التحميل الخارق 🚀🔥\n\n"
        "• البوت شغال الآن **24/7** بدون توقف!\n"
        "• أرسل **رابط تيك توك** أو **إنستغرام** لتحميله بأعلى جودة أصلية!\n"
        "• أرسل **يوزر تيك توك** لجلب الأفاتار والبيانات."
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    
    # 1. تحميل فيديوهات تيك توك عبر API مباشر ومستقر 100%
    if "tiktok.com" in text or "vt.tiktok.com" in text or "vm.tiktok.com" in text:
        processing_msg = await update.message.reply_text("⚡️ جاري تحميل فيديو تيك توك بأعلى جودة...")
        try:
            target_url = text.split("?")[0]
            api_url = f"https://www.tikwm.com/api/?url={target_url}&hd=1"
            res = requests.get(api_url, timeout=15).json()

            if res.get("code") == 0 and "data" in res:
                video_data = res["data"]
                hd_play = video_data.get("hdplay") or video_data.get("play")
                title = video_data.get("title", "فيديو تيك توك")
                
                await processing_msg.delete()
                await update.message.reply_video(
                    video=hd_play,
                    caption=f"🎥 **تم تحميل تيك توك بنجاح يا وحش!** 🚀\n\n📝 {title}",
                    supports_streaming=True
                )
            else:
                await processing_msg.edit_text("❌ لم أستطع تحميل فيديو تيك توك، تأكد من صحة الرابط.")
        except Exception as e:
            logger.error(f"TikTok Error: {e}")
            await processing_msg.edit_text("❌ حدث خطأ أثناء تحميل تيك توك.")
        return

    # 2. تحميل فيديوهات إنستغرام عبر yt-dlp القوي والمضمون
    if "instagram.com" in text or "instagr.am" in text:
        processing_msg = await update.message.reply_text("⚡️ جاري سحب فيديو إنستغرام بأعلى جودة أصلية...")
        try:
            clean_url = text.split("?")[0]
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            
            video_url = ""
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                video_url = info.get('url') or info.get('requested_formats', [{}])[0].get('url')

            if video_url:
                await processing_msg.delete()
                await update.message.reply_video(
                    video=video_url,
                    caption="🎥 **تم تحميل فيديو إنستغرام بنجاح يا بطل!** 🚀",
                    supports_streaming=True
                )
            else:
                await processing_msg.edit_text("❌ عذراً، لم أستطع استخراج الفيديو. تأكد أن الحساب عام.")
        except Exception as e:
            logger.error(f"IG Error: {e}")
            await processing_msg.edit_text("❌ حدث خطأ أثناء تحميل إنستغرام.")
        return

    # 3. جلب معلومات حسابات تيك توك
    if not " " in text and len(text) < 30 and not text.startswith("السلام") and not text.startswith("هلا"):
        processing_msg = await update.message.reply_text("⚡️ جاري سحب الأفاتار والبيانات...")
        try:
            clean_user = text.replace("@", "").replace("https://www.tiktok.com/@", "").split("/")[0].strip()
            profile_url = f"https://www.tiktok.com/@{clean_user}"
            avatar_url = f"https://www.tikwm.com/avatar/{clean_user}"
            
            api_url = f"https://www.tikwm.com/api/user/info?unique_id={clean_user}"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.get(api_url, headers=headers, timeout=10)
            nickname = clean_user
            signature = "لا يوجد بايو"
            followers = "غير معروف"
            following = "غير معروف"
            hearts = "غير معروف"

            if response.status_code == 200:
                res = response.json()
                if res.get("code") == 0 and "data" in res:
                    user_data = res["data"].get("user", {})
                    stats_data = res["data"].get("stats", {})
                    nickname = user_data.get("nickname", clean_user)
                    signature = user_data.get("signature", "لا يوجد بايو")
                    followers = stats_data.get("followerCount", "غير معروف")
                    following = stats_data.get("followingCount", "غير معروف")
                    hearts = stats_data.get("heartCount", "غير معروف")

            msg = (
                f"🎯 **معلومات حساب التيك توك:**\n\n"
                f"👤 **اسم الحساب:** {nickname}\n"
                f"🆔 **المعرف:** @{clean_user}\n"
                f"✍️ **البايو:** {signature}\n"
                f"👥 **المتابعين:** {followers}\n"
                f"🤝 **المُتابَعون:** {following}\n"
                f"❤️️ **الإعجابات:** {hearts}\n\n"
                f"📌 تفضل الأفاتار الأصلي يا وحش!"
            )

            keyboard = [[InlineKeyboardButton("🔗 فتح الحساب", url=profile_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await processing_msg.delete()
            await update.message.reply_photo(
                photo=avatar_url,
                caption=msg,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Profile Error: {e}")
            await processing_msg.edit_text("❌ حدث خطأ أثناء جلب تفاصيل الحساب.")
        return

    chat_responses = {
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته يا يونس يا ذيبان! منور يا غالي ⚡️",
        "هلا": "هلا بيك يا وحش! أنا جاهز لأي خدمة تبيها.",
        "شلونك": "أنا بخير بشوفتك يا بطل، أنت كيف أمورك؟",
    }
    reply_text = chat_responses.get(text.lower(), f"يا هلا فيك يا يونس! أرسل رابط تيك توك أو إنستغرام وأنا حاضر 🔥")
    await update.message.reply_text(reply_text)

def main() -> None:
    keep_alive()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
    
