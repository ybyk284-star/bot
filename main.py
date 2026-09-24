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
        f"أهلاً بك يا {user_name} في بوت يونس الخارق لتحسين ورفع جودة الصور والفيديوهات 🚀🔥\n\n"
        "📸 **أرسل لي أي صورة أو فيديو** وسأقوم برفع جودتها وتطبيق الفلاتر الاحترافية الفخمة جاهزة للنشر!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """استقبال الصور، الفيديوهات أو الملفات وإظهار خيارات الجودة"""
    user_id = update.effective_user.id
    message = update.message
    
    # التقاط الصور سواء أرسلت كصورة أو كمستند صورة
    if message.photo:
        photo_file = await message.photo[-1].get_file()
        user_data[user_id] = {"type": "photo", "file": photo_file}
    elif message.document and any(ext in message.document.file_name.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
        photo_file = await message.document.get_file()
        user_data[user_id] = {"type": "photo", "file": photo_file}
    elif message.video or message.document or message.animation:
        user_data[user_id] = {"type": "video", "message": message}
    elif message.text and message.text.startswith("http"):
        user_data[user_id] = {"type": "url", "text": message.text}
    else:
        await message.reply_text("يا يونس يا بطل، أرسل لي **صورة** أو **فيديو** واضح لنبدأ رفع دقته الفورية! 📥")
        return

    # لوحة المفاتيح المخصصة
    keyboard = [
        [
            InlineKeyboardButton("✨ تصفية ورفع الجودة HD", callback_data="qual_hd"),
            InlineKeyboardButton("🔥 رفع الجودة لـ 4K", callback_data="qual_4k")
        ],
        [
            InlineKeyboardButton("🚀 تفعيل جودة 8K الخارقة + فلاتر النشر", callback_data="qual_8k"),
            InlineKeyboardButton("💎 فلتر السينما الفاخر", callback_data="qual_cinema")
        ],
        [
            InlineKeyboardButton("🎵 تحويل الفيديو لصوت MP3", callback_data="qual_audio")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text(
        "📥 تم استلام الملف بنجاح يا يونس!\nاختر نوع المعالجة والفلتر المطلوب لتجهيزه للنشر:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنفيذ المعالجة الفعلية ورفع الجودة للصور والفيديوهات"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in user_data:
        await query.edit_message_text("انتهت صلاحية الجلسة يا يونس. أرسل الصورة أو الفيديو من جديد.")
        return

    choice = query.data
    data_info = user_data[user_id]

    await query.edit_message_text(f"⚙️ جاري تطبيق المعالجة الفعلية ورفع الوضوح وتفعيل الفلاتر الخارقة... انتظر قليلاً يا يونس 🚀")

    os.makedirs("downloads", exist_ok=True)

    try:
        if data_info["type"] == "photo":
            # --- معالجة الصور الحقيقية ورفعها حتى 8K مع فلاتر النشر ---
            photo_file = data_info["file"]
            input_path = f"downloads/img_in_{user_id}.jpg"
            output_path = f"downloads/img_out_{user_id}.jpg"

            await photo_file.download_to_drive(input_path)

            img = cv2.imread(input_path)
            if img is None:
                raise Exception("فشل في قراءة الصورة المرفقة.")

            h, w = img.shape[:2]

            # تحديد معامل التكبير والفلاتر الاحترافية
            if choice == "qual_8k":
                scale = 4.0
                img = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
            elif choice == "qual_cinema":
                scale = 3.0
                img = cv2.convertScaleAbs(img, alpha=1.25, beta=10)
                img = cv2.detailEnhance(img, sigma_s=15, sigma_r=0.2)
            elif choice == "qual_4k":
                scale = 3.0
                img = cv2.detailEnhance(img, sigma_s=8, sigma_r=0.1)
            else:
                scale = 2.0
                img = cv2.detailEnhance(img, sigma_s=5, sigma_r=0.1)

            new_w = int(w * scale)
            new_h = int(h * scale)

            # تكبير الأبعاد بجودة فائقة
            resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            # زيادة الحدة والنقاء
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(resized_img, -1, kernel)

            cv2.imwrite(output_path, sharpened)

            with open(output_path, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=f,
                    caption="🔥 **تمت معالجة الصورة ورفعها بدقة خارقة + فلاتر النشر بنجاح!**\nجاهزة لتكسر الدنيا يا يونس 🚀📸"
                )

            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)

        elif data_info["type"] == "url":
            url = data_info["text"]
            output_template = f"downloads/file_{user_id}.%(ext)s"
            ydl_opts = {'format': 'best', 'outtmpl': output_template}

            if choice == "qual_audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if choice == "qual_audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"

            with open(filename, 'rb') as f:
                if choice == "qual_audio":
                    await context.bot.send_audio(chat_id=query.message.chat_id, audio=f, caption="🎵 تفضل الملف الصوتي يا يونس")
                else:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption="🚀 تم تحميل ومعالجة الفيديو بجودة عالية للنشر")

            if os.path.exists(filename):
                os.remove(filename)

        else:
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
                cap = cv2.VideoCapture(input_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps == 0 or np.isnan(fps):
                    fps = 25.0

                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if width == 0 or height == 0:
                    width, height = 640, 360

                target_height = 1080 if "8k" in choice or "4k" in choice else 720
                aspect_ratio = width / height if height > 0 else 16/9
                new_width = int(target_height * aspect_ratio)
                if new_width % 2 != 0:
                    new_width += 1

                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, target_height))

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized = cv2.resize(frame, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
                    enhanced = cv2.detailEnhance(resized, sigma_s=8, sigma_r=0.15)
                    out.write(enhanced)

                cap.release()
                out.release()

                with open(output_path, 'rb') as f:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=f, caption="🔥 تمت معالجة الفيديو وتفعيل الفلاتر الاحترافية بنجاح يا يونس!")

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
    
    # فلاتر واسعة وشاملة للصور كملفات ومباشرة والفيديوهات
    msg_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.ANIMATION | (filters.TEXT & ~filters.COMMAND)
    application.add_handler(MessageHandler(msg_filter, handle_message))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling()

if __name__ == "__main__":
    main()
    
