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
        "🎬 **أرسل لي أي فيديو أو صورة الآن** وسأقوم بمعالجتها ورفع جودتها لتكون جاهزة لتكسر الترند!"
    )
    await update.message.reply_text(welcome_text, reply_to_message_id=update.message.message_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message
    
    os.makedirs("downloads", exist_ok=True)
    
    try:
        if message.photo:
            status_msg = await message.reply_text(
                "🔥 جاري تحويل وتصفية الصورة بدقة خارقة وفلاتر النشر يا يونس... 📸",
                reply_to_message_id=message.message_id
            )
            
            photo_file = await message.photo[-1].get_file()
            input_path = f"downloads/img_in_{user_id}.jpg"
            output_path = f"downloads/img_out_{user_id}.jpg"

            await photo_file.download_to_drive(input_path)

            img = cv2.imread(input_path)
            if img is None:
                raise Exception("فشل في قراءة الصورة.")

            h, w = img.shape[:2]
            scale = 2.5
            img = cv2.detailEnhance(img, sigma_s=8, sigma_r=0.12)
            
            new_w = int(w * scale)
            new_h = int(h * scale)

            resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            kernel = np.array([[0, -1, 0], [-1, 5.2, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(resized_img, -1, kernel)

            cv2.imwrite(output_path, sharpened)

            try:
                await context.bot.delete_message(chat_id=message.chat_id, message_id=status_msg.message_id)
            except:
                pass

            with open(output_path, 'rb') as f:
                await message.reply_photo(
                    photo=f,
                    caption="🔥 **تمت معالجة الصورة بنجاح ورفع نقائها!**\nجاهزة لتكسر الدنيا يا يونس 📸🚀",
                    reply_to_message_id=message.message_id
                )

            for p in [input_path, output_path]:
                if os.path.exists(p):
                    os.remove(p)

        elif message.text and message.text.startswith("http"):
            status_msg = await message.reply_text(
                "🚀 جاري تحميل ومعالجة الرابط بأعلى جودة وسلاسة يا يونس...",
                reply_to_message_id=message.message_id
            )
            
