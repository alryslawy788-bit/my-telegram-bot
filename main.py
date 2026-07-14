from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
import re

TOKEN = "8920702443:AAHjBDpRmT0QhIp_GVc--oKDkAon1lh4B3g" 
GROUP_ID = -1003835392009

db = {}
temp_buffer = []

def clean_udid(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

# --- الترحيب والواجهة ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔎 بحث عن شهادتي", callback_data='start_search')],
        [InlineKeyboardButton("💳 شراء شهادة رسمية", url='https://t.me/abn_aqeel')],
        [InlineKeyboardButton("💬 تواصل مع الدعم", url='https://t.me/abn_aqeel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "✨ *أهلاً بك في متجر علي لخدمات الأبل!*\n\n"
        "نحن هنا لتسهيل عملية تفعيل شهادتك بكل احترافية.\n"
        "اختر أحد الخيارات أدناه للبدء:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'start_search':
        await query.message.reply_text("📥 *يرجى إرسال الـ UDID الخاص بك أدناه للبحث عن ملفاتك:*", parse_mode='Markdown')

# --- معالج الحفظ والإرسال ---
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

    elif chat_id > 0:
        text = msg.text or ""
        match = re.search(r'[0-9a-fA-F-]{20,}', text)
        if match:
            key = clean_udid(match.group(0))
            if key in db:
                await msg.reply_text("🔍 *جاري البحث في قاعدة البيانات...*", parse_mode='Markdown')
                for orig in db[key]:
                    try:
                        if orig.text and orig.reply_markup:
                            await context.bot.send_message(chat_id=chat_id, text=orig.text, reply_markup=orig.reply_markup)
                        else:
                            await context.bot.copy_message(chat_id=chat_id, from_chat_id=GROUP_ID, message_id=orig.message_id)
                    except Exception as e:
                        print(f"خطأ في الإرسال: {e}")
            else:
                # رسالة خطأ احترافية
                error_text = (
                    "⚠️ *عذراً، لم يتم العثور على شهادة.*\n\n"
                    "يبدو أن الـ UDID الذي أدخلته غير مسجل في قاعدة بياناتنا.\n"
                    "يرجى التأكد من الـ UDID والمحاولة مرة أخرى، أو التواصل مع الدعم الفني للمساعدة:\n\n"
                    "👤 التواصل: @abn_aqeel"
                )
                await msg.reply_text(error_text, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.ALL, main_handler))
    print("متجر علي يعمل الآن بكامل أناقته..")
    app.run_polling()
