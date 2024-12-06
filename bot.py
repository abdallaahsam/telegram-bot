from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp
import nest_asyncio  # <-- أضف هذا
nest_asyncio.apply()  # <-- أضف هذا

# إعدادات التنزيل
async def download_video(url, quality, is_audio):
    ydl_opts = {
        'format': f'{quality}+bestaudio/best' if not is_audio else 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}] if is_audio else [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_name = ydl.prepare_filename(info)
    return file_name

# الأوامر الأساسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط الفيديو الذي تريد تحميله:")

async def process_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    keyboard = [
        [InlineKeyboardButton("تحميل فيديو بجودة عالية", callback_data=f'video-high-{url}')],
        [InlineKeyboardButton("تحميل فيديو بجودة منخفضة", callback_data=f'video-low-{url}')],
        [InlineKeyboardButton("تحميل الصوت فقط", callback_data=f'audio-{url}')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data.split('-')
    file_type, quality, url = callback_data[0], callback_data[1], callback_data[2]
    is_audio = file_type == 'audio'
    quality = 'bestvideo[height<=720]' if quality == 'high' else 'worst'

    await query.edit_message_text("جارِ التحميل...")
    try:
        file_name = await download_video(url, quality, is_audio)
        await query.message.reply_text("تم التحميل! جاري إرسال الملف...")
        with open(file_name, 'rb') as f:
            if is_audio:
                await query.message.reply_audio(f)
            else:
                await query.message.reply_video(f)
    except Exception as e:
        await query.message.reply_text(f"حدث خطأ: {str(e)}")

# إعداد التطبيق
async def main():
    TOKEN = "7682990195:AAELzDSMoP_C9VOxNAnQ9ESlkDM1KJKg0Lc"
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_url))
    application.add_handler(CallbackQueryHandler(button_callback))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
