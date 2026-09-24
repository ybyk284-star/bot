import os
import logging
import cv2
import numpy as np
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

# تخزين مؤقت لبيانات المستخدمين
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة البدء الترحيبية"""
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت يونس الخارق للمعالجة الفعلية 🚀\n\n"
        "أرسل لي أي **فيديو** أو **رابط**, وسأقوم بمعالجته وتغيير دقته ورفع جودته فوراً!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """استقبال الروابط أو الفيديوهات وإظهار أزرار الجودات بدقة عالية"""
    user_id = update.effective_user.id
    message = update.message
    
    # التحقق مما إذا كان المرسل فيديو، مستند فيديو، أو رابط نصي
    if message.video or message.document or message.animation:
        user_data[user_id] = {"type": "direct", "message": message}
    elif message.text and message.text.startswith("http"):
        user_data[user_id] = {"type": "url", "text": message.text}
    else:
        await message.reply_text("يا يونس يا بطل، أرسل لي **فيديو** أو **رابط** صحيح عشان أقدر أعالج لك إياه! 📥")
        return

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
    await message.reply_text(
        "📥 تم استلام الفيديو بنجاح يا يونس!\nاختر الجودة المطلوبة لبدء المعالجة الفورية:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الفيديو فعلياً وتغيير داقته وأبعاده"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("انتهت صلاحية الجلسة يا يونس. أرسل الفيديو أو الرابط من جديد.")
        return

    choice = query.data
    data_info = user_data[user_id]

    quality_names = {
        "qual_140p": "140p", "qual_240p": "240p", "qual_360p": "360p",
        "qual_480p": "480p", "qual_720p": "720p HD", "qual_1080p": "1080p FHD",
        "qual_4k": "4K ULTRA", "qual_8k": "8K EXTREME الخارقة",
        "qual_audio": "صوت MP3"
    }
    q_name = quality_names.get(choice, "المطلوبة")

    await query.edit_message_text(f"⚙️ جاري تطبيق المعالجة ورفع الوضوح إلى **{q_name}**... انتظر قليلاً يا يونس.")

    os.makedirs("downloads", exist_ok=True)

    try:
        if data_info["type"] == "url":
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
            else:
                h = height_map.get(choice, 720)
                ydl_opts = {'format': f'bestvideo[height<={h}]+bestaudio/best[height<={h}]/best', 'outtmpl': output_template}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if choice == "qual_audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            with open(filename, 'rb') as f:
                if choice == "qual_audio":
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="🎵 تفضل الملف الصوتي يا يونس")
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=f"🚀 تم تحميل ومعالجة الفيديو بجودة {q_name}")

            if os.path.exists(filename):
                os.remove(filename)

        else:
            # معالجة الفيديو المباشر عبر OpenCV
            msg = data_info["message"]
            media_file = msg.video or msg.document or msg.animation
            file_obj = await media_file.get_file()
            
            input_path = f"downloads/input_{user_id}.mp4"
            output_path = f"downloads/output_{user_id}.mp4"
            
            await file_obj.download_to_drive(input_path)

            if choice == "qual_audio":
                output_path = f"downloads/output_{user_id}.mp3"
                import subprocess
                subprocess.run(f"ffmpeg -i {input_path} -q:a 0 -map a {output_path} -y", shell=True)
                with open(output_path, 'rb') as f:
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="✨ تم استخراج الصوت بنجاح يا يونس!")
            else:
                target_height = {
                    "qual_140p": 140, "qual_240p": 240, "qual_360p": 360,
                    "qual_480p": 480, "qual_720p": 720, "qual_1080p": 1080,
                    "qual_4k": 2160, "qual_8k": 4320
                }.get(choice, 720)

                cap = cv2.VideoCapture(input_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0 or np.isnan(fps):
                    fps = 25.0

                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                if width == 0 or height == 0:
                    width, height = 640, 360

                aspect_ratio = width / height if height > 0 else 16/9
                new_height = target_height
                new_width = int(new_height * aspect_ratio)
                if new_width % 2 != 0:
                    new_width += 1

                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                    gaussian = cv2.GaussianBlur(resized, (0, 0), 2.0)
                    enhanced = cv2.addWeighted(resized, 1.5, gaussian, -0.5, 0)
                    out.write(enhanced)

                cap.release()
                out.release()

                with open(output_path, 'rb') as f:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption=f"🔥 تمت المعالجة وتعديل الدقة إلى {q_name} بنجاح يا يونس!")

            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)

    except Exception as e:
        logger.error(f"Error in processing: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"عذراً يا يونس، حدث خطأ أثناء المعالجة: {str(e)}"
        )

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # فلاتر شاملة لاستقبال الفيديوهات، الملفات، المتحرك, أو الروابط النصية
    msg_filter = filters.VIDEO | filters.Document.ALL | filters.ANIMATION | (filters.TEXT & ~filters.COMMAND)
    application.add_handler(MessageHandler(msg_filter, handle_message))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling()

if __name__ == "__main__":
    main()
                    
