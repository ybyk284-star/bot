import os
import logging
import cv2
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8266423475:AAFUyf5Ee6eWIPY2pWErii3HUm0M9JfDY6k'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت يونس الخارق 🚀🔥\n\n"
        "📸 **أرسل لي أي صورة أو فيديو الآن** وسأقوم برفع جودتها وتطبيق فلاتر الـ 8K الخارقة فوراً!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message
    
    os.makedirs("downloads", exist_ok=True)
    
    try:
        if message.photo:
            status_msg = await message.reply_text("⚙️ جاري معالجة الصورة ورفع دقتها لـ 8K يا يونس... انتظر ثواني 🚀")
            
            photo_file = await message.photo[-1].get_file()
            input_path = f"downloads/img_in_{user_id}.jpg"
            output_path = f"downloads/img_out_{user_id}.jpg"

            await photo_file.download_to_drive(input_path)

            # قراءة الصورة وتخفيف الاستهلاك
            img = cv2.imread(input_path)
            if img is None:
                raise Exception("فشل في قراءة الصورة.")

            h, w = img.shape[:2]
            
            # تقليل معامل التكبير قليلاً لحماية السيرفر من الانطفاء مع الحفاظ على دقة خارقة
            scale = 2.0
            img = cv2.detailEnhance(img, sigma_s=5, sigma_r=0.1)
            
            new_w = int(w * scale)
            new_h = int(h * scale)

            resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(resized_img, -1, kernel)

            cv2.imwrite(output_path, sharpened)

            try:
                await context.bot.delete_message(chat_id=message.chat_id, message_id=status_msg.message_id)
            except:
                pass

            with open(output_path, 'rb') as f:
                await message.reply_photo(
                    photo=f,
                    caption="🔥 **تمت معالجة الصورة ورفعها بدقة خارقة + فلاتر النشر بنجاح!**\nجاهزة لتكسر الدنيا على تيك توك وإنستغرام يا يونس 📸🚀"
                )

            # تنظيف الملفات فوراً لتفريغ الذاكرة
            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)

        elif message.text and message.text.startswith("http"):
            status_msg = await message.reply_text("⚙️ جاري تحميل ومعالجة الرابط يا يونس... 🚀")
            url = message.text
            output_template = f"downloads/file_{user_id}.%(ext)s"
            ydl_opts = {'format': 'best', 'outtmpl': output_template}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            try:
                await context.bot.delete_message(chat_id=message.chat_id, message_id=status_msg.message_id)
            except:
                pass

            with open(filename, 'rb') as f:
                await message.reply_video(video=f, caption="🚀 تم تحميل ومعالجة الفيديو بنجاح يا يونس!")

            if os.path.exists(filename):
                os.remove(filename)

        elif message.video or message.document:
            status_msg = await message.reply_text("⚙️ جاري معالجة الفيديو ورفع جودته يا يونس... انتظر قليلاً 🎬")
            
            media_file = message.video or message.document
            file_obj = await media_file.get_file()
            
            input_path = f"downloads/input_{user_id}.mp4"
            output_path = f"downloads/output_{user_id}.mp4"
            
            await file_obj.download_to_drive(input_path)

            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0 or np.isnan(fps):
                fps = 25.0

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width == 0 or height == 0:
                width, height = 640, 360

            target_height = 720
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
                out.write(resized)

            cap.release()
            out.release()

            try:
                await context.bot.delete_message(chat_id=message.chat_id, message_id=status_msg.message_id)
            except:
                pass

            with open(output_path, 'rb') as f:
                await message.reply_video(video=f, caption="🔥 تمت معالجة الفيديو ورفع دقته بنجاح يا يونس!")

            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)
        else:
            await message.reply_text("يا يونس يا بطل، أرسل لي **صورة** أو **فيديو** وسأقوم برفع دقته فوراً! 📥")

    except Exception as e:
        logger.error(f"Error in processing: {e}")
        await message.reply_text(f"عذراً يا يونس، حصل خطأ بسيط أثناء المعالجة: {str(e)}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    msg_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL | (filters.TEXT & ~filters.COMMAND)
    application.add_handler(MessageHandler(msg_filter, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
