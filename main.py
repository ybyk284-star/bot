import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ضع توكن البوت الخاص بالخزنة هنا
TOKEN = '8266423475:AAHG4Im-8XKwmcT8NEHv8dQyHgJVvNx_t_g'

# كلمة السر الخاصة بك (تستطيع تغييرها لما تريد)
SECRET_PASSWORD = "123" 

# قاموس لحفظ حالة المستخدمين (هل قاموا بتسجيل الدخول أم لا)
authenticated_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # إزالة حالة المصادقة عند بدء التشغيل لحماية الخزنة
    if user_id in authenticated_users:
        authenticated_users.remove(user_id)
        
    await update.message.reply_text(
        "🔒 **أهلاً بك في خزنـة الصور السرية الخاصة يا يونس!**\n\n"
        "هذه الخزنة محمية بكلمة سر ولا يمكن لأحد رؤية محتواها سواك.\n"
        "الرجاء إرسال **كلمة السر** لفتح الخزنة:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    photo = update.message.photo
    video = update.message.video

    # 1. إذا لم يكن المستخدم مسجلاً لدخوله، نتحقق من كلمة السر
    if user_id not in authenticated_users:
        if text and text.strip() == SECRET_PASSWORD:
            authenticated_users.add(user_id)
            keyboard = [["عرض صوري السرية 📂"], ["قفل الخزنة 🔒"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "✅ **تم فتح الخزنة بنجاح يا يونس!**\n\n"
                "• أرسل أي صورة أو فيديو الآن لحفظه في الخزنة السرية.\n"
                "• أو اضغط على 'عرض صوري السرية' لمشاهدة صورك المخزنة.",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ كلمة السر غير صحيحة! الخزنة مغلقة ومحمية. أرسل كلمة السر الصحيح:")
        return

    # 2. إذا كان المستخدم مسجلاً دخوله، نتعامل مع الأوامر والصور
    if text == "قفل الخزنة 🔒":
        authenticated_users.remove(user_id)
        await update.message.reply_text(
            "🔒 **تم إقفال الخزنة بنجاح!**\nلن يتمكن أحد من رؤية محتوياتها إلا بكلمة السر. أرسل كلمة السر لفتحها مرة أخرى:",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    if text == "عرض صوري السرية 📂":
        # هنا يمكنك تخزين معرفات الصور (file_id) في ملف أو قاعدة بيانات
        # كمثال، سنخبرك أن الصور يتم حفظها مباشرة بمجرد إرسالها
        await update.message.reply_text("📂 كل صورة ترسلها للبوت أثناء فتح الخزنة يتم حفظها هنا بشكل سري ومحمي تماماً. أرسل الصور التي تريد حفظها الآن!")
        return

    # 3. حفظ الصور أو الفيديوهات المرسلة
    if photo:
        # نحصل على أعلى دقة للصورة
        file_id = photo[-1].file_id
        # يمكنك حفظ file_id في ملف نصي أو قاعدة بيانات خاصة بك
        with open("secret_storage.txt", "a") as f:
            f.write(f"{user_id}:{file_id}\n")
            
        await update.message.reply_text("📥 تم حفظ الصورة في الخزنة السرية بنجاح وبأمان تآم! 🔒✨")
        return

    if video:
        file_id = video.file_id
        with open("secret_storage.txt", "a") as f:
            f.write(f"{user_id}:{file_id}\n")
            
        await update.message.reply_text("📥 تم حفظ الفيديو في الخزنة السرية بنجاح! 🔒✨")
        return

    await update.message.reply_text("❓ أمر غير معروف داخل الخزنة. أرسل صورة لحفظها أو استخدم الأزرار بالأسفل.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
            
