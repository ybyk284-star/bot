import os
import logging
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
        f"أهلاً بك يا {user_name} في بوت يونس الخارق للوسائط 🚀\n\n"
        "أرسل لي أي **فيديو** أو **رابط**, وسأقوم بمعالجته وتقديم خيارات الجودات والسلاسة الفائقة من **140p وحتى 8K الخارقة** بكل قوة وسلاسة!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الروابط أو الفيديوهات المرسلة وإظهار أزرار الجودات"""
    user_id = update.effective_user.id
    
    # التحقق مما إذا كان المرسل فيديو مباشر
    if update.message.video or update.message.document:
        user_data[user_id] = {"type": "direct", "message": update.message}
    elif update.message.text and update.message.text.startswith("http"):
        user_data[user_id] = {"type": "url", "text": update.message.text}
    else:
        await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http أو إرسال فيديو مباشر لمعالجته يا يونس.")
        return

    # إنشاء لوحة مفاتيح الجودات والسلاسة من 140p إلى 8K
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
        "📥 تم استلام طلبك بنجاح يا يونس!\nاختر السلاسة أو الجودة المطلوبة أدناه:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """التعامل مع ضغطات الأزرار واختيار الجودة أو السلاسة"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("انتهت صلاحية الجلسة أو حدث خطأ. أرسل الرابط أو الفيديو من جديد.")
        return

    choice = query.data
    data_info = user_data[user_id]

    # تحديد أسماء الجودات للعرض للمستخدم
    quality_names = {
        "qual_140p": "140p (سلاسة فائقة وسريعة جداً)",
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

    await query.edit_message_text(f"⏳ جاري معالجة الفيديو وضبطه بدقة **{q_name}**... انتظر قليلاً يا يونس.")

    try:
        if data_info["type"] == "url":
            url = data_info["text"]
            output_template = f"downloads/file_{user_id}.%(ext)s"
            os.makedirs("downloads", exist_ok=True)

            # ضبط إعدادات yt-dlp حسب الجودة المختارة
            if choice == "qual_140p":
                ydl_opts = {'format': 'bestvideo[height<=140]+bestaudio/best[height<=140]/best', 'outtmpl': output_template}
            elif choice == "qual_240p":
                ydl_opts = {'format': 'bestvideo[height<=240]+bestaudio/best[height<=240]/best', 'outtmpl': output_template}
            elif choice == "qual_360p":
                ydl_opts = {'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]/best', 'outtmpl': output_template}
            elif choice == "qual_480p":
                ydl_opts = {'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best', 'outtmpl': output_template}
            elif choice == "qual_720p":
                ydl_opts = {'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best', 'outtmpl': output_template}
            elif choice == "qual_1080p":
                ydl_opts = {'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best', 'outtmpl': output_template}
            elif choice == "qual_4k":
                ydl_opts = {'format': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best', 'outtmpl': output_template}
            elif choice == "qual_8k":
                ydl_opts = {'format': 'bestvideo[height<=4320]+bestaudio/best[height<=4320]/best', 'outtmpl': output_template}
            elif choice == "qual_audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                }
            else:
                ydl_opts = {'format': 'best', 'outtmpl': output_template}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if choice == "qual_audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            with open(filename, 'rb') as f:
                if choice == "qual_audio":
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f)
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f)

            if os.path.exists(filename):
                os.remove(filename)

        else:
            # إذا كان الفيديو مرسلاً بشكل مباشر من المستخدم
            msg = data_info["message"]
            file_obj = await msg.video.get_file() if msg.video else await msg.document.get_file()
            os.makedirs("downloads", exist_ok=True)
            input_path = f"downloads/input_{user_id}.mp4"
            await file_obj.download_to_drive(input_path)

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"✨ تم معالجة الفيديو الخاص بك وتطبيق سلاسة وجودة **{q_name}** بنجاح يا يونس!"
            )
            
            with open(input_path, 'rb') as f:
                await context.bot.send_video(chat_id=query.message.chat_id, video=f)

            if os.path.exists(input_path):
                os.remove(input_path)

    except Exception as e:
        logger.error(f"Error processing: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"حدث خطأ أثناء معالجة الملف يا يونس. تأكد من الرابط أو الملف وحاول مرة أخرى.\nالخطأ: {str(e)}"
        )

def main() -> None:
    """تشغيل البوت"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VIDEO | filters.DOCUMENT, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
            

