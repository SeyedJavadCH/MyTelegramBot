import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

load_dotenv()

TELEGRAM_TOKEN = "8416946308:AAE7SrKJnKo_PmYHTryR79-9OOefP51cLoU"
GAPGPT_API_KEY = "sk-yQ3CWxnew0ommL5syjAIGk7Z1nKTADyzL51qVhjyg1CmJwtS"

NOTES = {
    "ژئودزی ماهواره ای": {"file_ids": ["https://t.me/GeomaticsWith_SCh/62"], "keywords": ["ژئودزی", "ژئودزی ماهواره ای", "satlitegeodesy"]},
    "فتوگرامتری بردکوتاه": {"file_ids": ["https://t.me/GeomaticsWith_SCh/60"], "keywords": ["فتوگرامتری", "Photogerametery", "فتوگرامتری برد کوتاه"]},
    "زیرسازی روسازی": {"file_ids": ["https://t.me/GeomaticsWith_SCh/56", "https://t.me/GeomaticsWith_SCh/58"], "keywords": ["زیرسازی", "زیرسازی روسازی راه"]},
    "نقشه برداری ثبتی": {"file_ids": ["https://t.me/GeomaticsWith_SCh/59"], "keywords": ["ثبتی", "نقشه برداری ثبتی"]},
    "پویشگر های لیزری": {"file_ids": ["https://t.me/GeomaticsWith_SCh/51"], "keywords": ["پویشگر", "لیزر اسکنر", "لیزر", "پویشگر های لیزری"]},
    "عملیات سیستم اطلاعات مکانی": {"file_ids": ["https://t.me/GeomaticsWith_SCh/49", "https://t.me/GeomaticsWith_SCh/55"], "keywords": ["عملیات GIS", "جی ای اس", "gis", "GIS", "Gis", "عملیات سیستم اطلاعات مکانی"]},
    "عملیات کاربرد فتوگرامتری": {"file_ids": ["https://t.me/GeomaticsWith_SCh/47"], "keywords": ["کاربرد فتو", "فتوگرامتری", "عملیات کاربرد", "کاربرد فتوگرامتری"]}
}

NOTESQ = {
    "این بخش هنوز فعال نشده است.": {"file_ids": [""], "keywords": [""]}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["نمونه سوال امتحانی", "دریافت جزوه"],
        ["/start","پرسش از هوش مصنوعی"],
        
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("سلام دوست من اسم من آزیموت هست🤓 چطور میتونم بهت کمک کنم😉؟؟" +
                                    "میتونی از داخل منو انتخاب کنی که چطور بهت کمک کنم\n" +
                                    "\nبرای بهبود کیفیت مطالب و یا ارسال جزوه و نمونه سوالات به آیدی ادمین ربات:" +
                                    "\n@Javad_Dynasty\n" +
                                    "پیام بدین با تشکر ❤️", reply_markup=reply_markup)
    context.user_data['mode'] = 'auto'

async def show_notes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    keyboard.append(["سرچ جزوه"])
    keyboard.append(["برگشت"])
    for lesson in NOTES.keys():
        keyboard.append([lesson])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("درس مورد نظر رو انتخاب کن یا سرچ کن:", reply_markup=reply_markup)
    context.user_data['mode'] = "select_note"

async def show_exam_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    keyboard.append(["سرچ نمونه سوال"])
    keyboard.append(["برگشت"])
    for lesson in NOTESQ.keys():
        keyboard.append([lesson])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("نمونه سوال مورد نظر رو انتخاب کن یا سرچ کن:", reply_markup=reply_markup)
    context.user_data['mode'] = "select_exam"

async def show_ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["برگشت"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text("سوالت رو از آزیموت بپرس دوست من", reply_markup=reply_markup)
    context.user_data['mode'] = "ai"

async def get_ai_response(query: str) -> str:
    client = OpenAI(base_url="https://api.gapgpt.app/v1", api_key=GAPGPT_API_KEY)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500
        )
        print(f"Response: {response.choices[0].message.content}") 
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {str(e)}")  # برای دیباگ
        return "خطا در ارتباط با هوش مصنوعی"

async def search_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = "search_note"
    await update.message.reply_text("اسم درس یا بخشی از اون رو بنویس تا سرچ کنم:")

async def search_exams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = "search_exam"
    await update.message.reply_text("اسم درس یا بخشی از اون رو بنویس تا نمونه سوال سرچ کنم:")

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    matching_lessons = [lesson for lesson in NOTES.keys() if user_message in lesson.lower()]
    if matching_lessons:
        keyboard = []
        for lesson in matching_lessons:
            keyboard.append([lesson])
        keyboard.append(["برگشت"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        if context.user_data['mode'] == "search_note":
            await update.message.reply_text("جزوات یافت‌شده:", reply_markup=reply_markup)
            context.user_data['mode'] = "select_note"
        elif context.user_data['mode'] == "search_exam":
            await update.message.reply_text("نمونه سوالات یافت‌شده:", reply_markup=reply_markup)
            context.user_data['mode'] = "select_exam"
    else:
        await update.message.reply_text("درس پیدا نشد. دوباره امتحان کن یا برگشت بزن.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    mode = context.user_data.get('mode', 'auto')

    if update.message.text:
        user_message = update.message.text.lower()

        if user_message == "/start":
            await start(update, context)
            return

        if user_message == "دریافت جزوه":
            await show_notes_menu(update, context)
            return

        if user_message == "نمونه سوال امتحانی":
            await show_exam_menu(update, context)
            return

        if user_message == "پرسش از هوش مصنوعی":
            await show_ai_menu(update, context)
            return

        if user_message == "برگشت":
            await start(update, context)
            return

        if mode == "select_note":
            if user_message == "سرچ جزوه":
                await search_notes(update, context)
                return
            if user_message in NOTES:
                data = NOTES[user_message]
                for i, file_url in enumerate(data['file_ids'], 1):
                    try:
                        chat_id_part = file_url.split('/')[3]
                        message_id = int(file_url.split('/')[-1])
                        await context.bot.forward_message(chat_id=chat_id, from_chat_id=f"@{chat_id_part}", message_id=message_id)
                        await update.message.reply_text(f"جزوه {user_message} - بخش {i} ارسال شد✅")
                    except Exception as e:
                        await update.message.reply_text(f"خطا در ارسال جزوه: {str(e)}. لینک رو چک کن!")
                return
            else:
                await update.message.reply_text("درس پیدا نشد. لطفاً از منو انتخاب کن یا تایپ دقیق بنویس.")
            return

        if mode == "select_exam":
            if user_message == "سرچ نمونه سوال":
                await search_exams(update, context)
                return
            if user_message in NOTESQ:
                data = NOTESQ[user_message]
                for i, file_id in enumerate(data['file_ids'], 1):
                    await update.message.reply_document(file_id, caption=f"نمونه سوال {user_message} - بخش {i}")
                return
            else:
                await update.message.reply_text("درس پیدا نشد. لطفاً از منو انتخاب کن یا تایپ دقیق بنویس.")
            return

        if mode == "search_note" or mode == "search_exam":
            await handle_search(update, context)
            return

        if mode == "ai":
            ai_response = await get_ai_response(update.message.text)
            await update.message.reply_text(ai_response)
            return

        if mode == "note" or user_message.startswith('جزوه'):
            for lesson, data in NOTES.items():
                if any(keyword in user_message for keyword in data['keywords']):
                    for i, file_url in enumerate(data['file_ids'], 1):
                        try:
                            chat_id_part = file_url.split('/')[3]
                            message_id = int(file_url.split('/')[-1])
                            await context.bot.forward_message(chat_id=chat_id, from_chat_id=f"@{chat_id_part}", message_id=message_id)
                            await update.message.reply_text(f"جزوه {lesson} - بخش {i} ارسال شد✅")
                        except Exception as e:
                            await update.message.reply_text(f"خطا در ارسال جزوه: {str(e)}. لینک رو چک کن!")
                    return
            await update.message.reply_text("درس پیدا نشد. لطفاً واضح بنویس (مثل ژئودزی ماهواره ای، فتوگرامتری).")
            return

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("ربات شروع شد...")
    app.run_polling()

if __name__ == '__main__':
    main()
