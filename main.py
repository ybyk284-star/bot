import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8266423475:AAFUyf5Ee6eWIPY2pWErii3HUm0M9JfDY6k'

# قائمة البايوهات المرتبة والفخمة
BIOS = {
    "luxury": (
        "💎 **بايو هيبة وفخامة:**\n\n"
        "إِن كَان لِلْمَجْدِ عُنْوَانٌ.. فَهُوَ نَحْنُ 🦅\n"
        "لا نُبَالِي بالظُّروف، بل نَجْعَل الظُّروف تَبَالِي لَنَا.\n"
        "عِزَّةُ النَّفْسِ غَايَةٌ، وَالبَقَاءُ لِلْأَقْوَى."
    ),
    "modern": (
        "🔥 **بايو شبابي وعصري:**\n\n"
        "• كُنْ نَفْسَكَ، فَالجَمِيعُ مُقَلَّدُون ⚡️\n"
        "• نعيش مرة واحدة، فلنصنع شيئاً يخلدنا 🎬\n"
        "• لا شيء مستحيل مع الإصرار 💯"
    ),
    "quiet": (
        "🌙 **بايو هادئ ورايق:**\n\n"
        "سلامٌ على من كفَى ووفَى، واستغنى فارتوى 🌊\n"
        "وفي زحمة الحياة، تبقى القلوب الصافية هي الأجمل.\n"
        "هدوء الظاهر كافٍ لاختصار الكثير."
    ),
    "english": (
        "✨ **بايو إنجليزي فخم:**\n\n"
        "“Silence is the best response when you’re dealing with idiots.” 🖤\n"
        "Creating my own reality ✨\n"
        "Stay lowkey, let them assume."
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("💎 هيبة وفخامة", callback_data="luxury")],
        [InlineKeyboardButton("🔥 شبابي وعصري", callback_data="modern")],
        [InlineKeyboardButton("🌙 هادئ ورايق", callback_data="quiet")],
        [InlineKeyboardButton("✨ إنجليزي فخم", callback_data="english")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"أهلاً بك يا {user_name} في بوت صانع البايو الخارق 🚀🔥\n\n"
        "اختر التصنيف اللي يعجبك من الأزرار تحت، وبيعطيك أجمل وأفخم العبارات لجاهزة لملفك الشخصي بالإنستغرام أو التيك توك! 👇"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, reply_to_message_id=update.message.message_id)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    bio_content = BIOS.get(choice, "عذراً، حدث خطأ ما.")
    
    keyboard = [
        [InlineKeyboardButton("🔄 اختيار قسم آخر", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text=bio_content, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception:
        pass

async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💎 هيبة وفخامة", callback_data="luxury")],
        [InlineKeyboardButton("🔥 شبابي وعصري", callback_data="modern")],
        [InlineKeyboardButton("🌙 هادئ ورايق", callback_data="quiet")],
        [InlineKeyboardButton("✨ إنجليزي فخم", callback_data="english")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = "اختر التصنيف المناسب للبايو الخاص بك يا يونس 👇"
    try:
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
    except Exception:
        pass

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back$"))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
