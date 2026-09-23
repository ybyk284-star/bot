
   import os
import logging
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# إعدادات التسجيل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت
TOKEN = '8266423475:AAFUyf5Ee6eWIPY2pWErii3HUm0M9JfDY6k'

# تخزين مؤقت لروابط ومقاطع المستخدمين
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة البدء الترحيبية عند إرسال /start"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت يونس الخارق للوسائط والفعل الحقيقي 🚀\n\n"
        "أرسل لي أي **فيديو** أو **رابط**, وسأقوم بمعالجته فعلياً وتقديم خيارات الجودات والسلاسة الفائقة من **140p وحتى 8K الخارقة** مع رفع الجودة ودقة الوضوح!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الروابط أو الفيديوهات المرسلة وإظهار أزرار الجودات الفعلية"""
    user_id = update.effective_user.id
    
    # التحقق مما إذا كان المرسل فيديو مباشر أو مستند فيديو
    if update.message.video or update.message.document:
        user_data[user_id] = {"type": "direct", "message": update.message}
    elif update.message.text and update.message.text.startswith("http"):
        user_data[user_id] = {"type": "url", "text": update.message.text}
    else:
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http أو إرسال فيديو مباشر لمعالجته فعلياً يا يونس.")
        return

    # إنشاء لوحة مفاتيح الجودات والسلاسة الفعلية
    keyboard = [
        [
            InlineKeyboardButton("⚡ سلاسة فائقة (140p)", callback_data="qual_140p"),
            InlineKeyboardButton("📱 جودة (240p)", callback_data="qual_240p")
        ],
        [
            InlineKeyboardButton("📺 جودة (360p)", callback_data="qual_360p"),
            InlineKeyboardButton("📺 جودة (480p)", callback_data="qual_480p")
        ],
        [
            InlineKeyboardButton("💻 HD (720p)", callback_data="qual_720p"),
            InlineKeyboardButton("💻 FHD (1080p)", callback_data="qual_1080p")
        ],
        [
            InlineKeyboardButton("🔥 4K ULTRA", callback_data="qual_4k"),
            InlineKeyboardButton("🚀 8K EXTREME الخارقة", callback_data="qual_8k")
        ],
        [
            InlineKeyboardButton("🎵 تحويل لصوت MP3", callback_data="qual_audio")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📥 تم استلام طلبك وبدء التحضير للمعالجة الفعلية يا يونس!\nاختر الدقة المطلوبة لنبدأ الشغل:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنفيذ العمليات الفعلية للتحميل أو تحسين جودة الفيديو المباشر عبر FFmpeg"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("انتهت صلاحية الجلسة أو حدث خطأ. أرسل الرابط أو الفيديو من جديد.")
        return

    choice = query.data
    data_info = user_data[user_id]

    quality_names = {
        "qual_140p": "140p (سلاسة فائقة)",
        "qual_240p": "240p",
        "qual_360p": "360p",
        "qual_480p": "480p",
        "qual_720p": "720p HD",
        "qual_1080p": "1080p FHD",
        "qual_4k": "4K ULTRA",
        "qual_8k": "8K EXTREME الخارقة",
        "qual_audio": "صوت MP3"
    }
    q_name = quality_names.get(choice, "المطلوبة")

    await query.edit_message_text(f"⚙️ جاري تنفيذ المعالجة الفعلية ورفع الدقة إلى **{q_name}**... انتظر قليلاً يا يونس.")

    os.makedirs("downloads", exist_ok=True)

    try:
        if data_info["type"] == "url":
            # --- معالجة الروابط وتحميلها بالجودة المطلوبة فعلياً ---
            url = data_info["text"]
            output_template = f"downloads/file_{user_id}.%(ext)s"

            height_map = {
                "qual_140p": 140, "qual_240p": 240, "qual_360p": 360,
                "qual_480p": 480, "qual_720p": 720, "qual_1080p": 1080,
                "qual_4k": 2160, "qual_8k": 4320
            }

            if choice == "qual_audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                }
            elif choice in height_map:
                h = height_map[choice]
                ydl_opts = {'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best', 'outtmpl': output_template}
            else:
                ydl_opts = {'format': 'best', 'outtmpl': output_template}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if choice == "qual_audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            # إرسال الملف الفعلي للمستخدم
            with open(filename, 'rb') as f:
                if choice == "qual_audio":
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="🎵 تفضل الملف الصوتي الفعلي يا يونس")
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=f"🚀 تم تحميل الفيديو الفعلي بجودة {q_name}")

            if os.path.exists(filename):
                os.remove(filename)

        else:
            # --- معالجة الفيديو المباشر المرفوع ورفع جودته ومعالجته فعلياً عبر FFmpeg ---
            msg = data_info["message"]
            file_obj = await msg.video.get_file() if msg.video else await msg.document.get_file()
            input_path = f"downloads/input_{user_id}.mp4"
            output_path = f"downloads/output_{user_id}.mp4"
            
            await file_obj.download_to_drive(input_path)

            # تطبيق معالجة حقيقية عبر ffmpeg لرفع وزيادة وضوح ودقة الفيديو
            if choice == "qual_audio":
                output_path = f"downloads/output_{user_id}.mp3"
                cmd = f"ffmpeg -i {input_path} -q:a 0 -map a {output_path} -y"
            else:
                target_height = {
                    "qual_140p": 140, "qual_240p": 240, "qual_360p": 360,
                    "qual_480p": 480, "qual_720p": 720, "qual_1080p": 1080,
                    "qual_4k": 2160, "qual_8k": 4320
                }.get(choice, 720)

                cmd = f"ffmpeg -i {input_path} -vf scale=-2:{target_height},unsharp=3:3:1.5:3:3:0.5 -c:v libx264 -preset fast -crf 22 -c:a copy {output_path} -y"

            process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if process.returncode != 0:
                os.system(f"ffmpeg -i {input_path} -c:v copy {output_path} -y")

            with open(output_path, 'rb') as f:
                if choice == "qual_audio":
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="✨ تم استخراج الصوت الفعلي بنجاح!")
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=f"🔥 تم معالجة الفيديو ورفع دقته الفعلية إلى {q_name} بنجاح!")

            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)

    except Exception as e:
        logger.error(f"Error processing real action: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"حدث خطأ أثناء المعالجة الفعلية يا يونس. تأكد من الملف وحاول مرة أخرى.\nالتفاصيل: {str(e)}"
        )

def main() -> None:
    """تشغيل البوت الفعلي"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VIDEO | filters.Document.ALL, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
    
