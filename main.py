from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import re

TOKEN = "YOUR_TOKEN_BOt" 
GROUP_ID = -1003835392009

db = {}
temp_buffer = []

def clean_udid(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# --- الترحيب والأزرار ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 ابحث عن شهادتي", callback_data='start_search')],
        [InlineKeyboardButton("🛒 لشراء الشهادات", url='https://t.me/abn_aqeel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ أهلاً بك في متجر ابن عقيل!\n\n"
        "للبحث عن شهادتك الجاهزة، اضغط على الزر أدناه.",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'start_search':
        await query.message.reply_text("يرجى إرسال الـ UDID الخاص بك للبحث:")

# --- معالج الحفظ في المجموعة ---
async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg: return
    chat_id = update.effective_chat.id
    
    if chat_id == GROUP_ID:
        temp_buffer.append(msg)
        text = (msg.text or "") + (msg.caption or "")
        match = re.search(r'[0-9a-fA-F-]{20,}', text)
        if match:
            clean_key = clean_udid(match.group(0))
            db[clean_key] = list(temp_buffer)
            print(f"✅ تم حفظ الحزمة للـ UDID: {clean_key}")

    # --- معالج الإرسال في الخاص (فقط عند إرسال نص الـ UDID) ---
    elif chat_id > 0:
        text = msg.text or ""
        match = re.search(r'[0-9a-fA-F-]{20,}', text)
        if match:
            key = clean_udid(match.group(0))
            if key in db:
                await msg.reply_text("🔎 تم العثور على الشهادة، جاري الإرسال...")
                for orig in db[key]:
                    try:
                        if orig.text and orig.reply_markup:
                            await context.bot.send_message(chat_id=chat_id, text=orig.text, reply_markup=orig.reply_markup)
                        else:
                            await context.bot.copy_message(chat_id=chat_id, from_chat_id=GROUP_ID, message_id=orig.message_id)
                    except Exception as e:
                        print(f"خطأ: {e}")
            else:
                await msg.reply_text("❌ لم أجد ملفات لهذا الـ UDID. تواصل مع @abn_aqeel")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.ALL, main_handler))
    print("البوت يعمل الآن (الترحيب + الأزرار + النسخ الأصلي)..")
    app.run_polling()
