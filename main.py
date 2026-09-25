import os
import logging
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن الصحيح الخاص بك يا يونس
TOKEN = '8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت سحب البايو من تيك توك 🚀🔥\n\n"
        "فقط أرسل لي رابط حساب تيك توك (مثل: `https://www.tiktok.com/@username`) وسأجلب لك البايو الخاص به فوراً وجاهز للنسخ! 👇"
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def get_tiktok_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    
    if "tiktok.com" not in text:
        await update.message.reply_text("❌ عذراً يا يونس، يرجى إرسال رابط حساب تيك توك صحيح.")
        return

    processing_msg = await update.message.reply_text("⏳ جاري جلب البايو من تيك توك...")

    try:
        urls = re.findall(r'(https?://[^\s]+)', text)
        target_url = urls[0] if urls else text

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(target_url, headers=headers, timeout=10)
        if response.status_code != 200:
            await processing_msg.edit_text("❌ تعذر الوصول إلى الحساب، تأكد أن الرابط صحيح وعام.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        bio_element = soup.find('meta', attrs={'property': 'og:description'})
        
        if bio_element and bio_element.get('content'):
            bio_text = bio_element['content']
            
            result_text = (
                "🎯 **تم سحب البايو بنجاح:**\n\n"
                f"```text\n{bio_text}\n```\n"
                "📌 جاهز للنسخ والاستخدام يا وحش!"
            )
            await processing_msg.edit_text(result_text, parse_mode="Markdown")
        else:
            await processing_msg.edit_text("⚠️ لم يتم العثور على بايو لهذا الحساب أو أن الحساب خاص.")

    except Exception as e:
        logger.error(f"Error: {e}")
        await processing_msg.edit_text("❌ حدث خطأ أثناء جلب البيانات، حاول مرة أخرى لاحقاً.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_tiktok_bio))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
