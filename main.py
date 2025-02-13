import logging
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram.ext import Updater
from get_db import DB  # DB faylini import qilish

ADMIN_CHAT_IDS = [1698951222]

# Loggingni yoqish
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# DBni yaratish
db = DB()
print(db.startup())

# Bot tokeni va adminlar chat_id sini qo'shish
TOKEN = '8072666419:AAGplm6gIS9lW-oGySMcHVg0NHkc6ZGvEag'



# Taomlar ro'yxatini inline button bilan yuborish
def send_food_list(update: Update, context: CallbackContext):
    food_items = db.get_food()
    print(food_items)
    keyboard = []
    
    if not food_items:
        update.message.reply_text("Hozirda mavjud taomlar yo'q.")
        return

    # Inline button yaratish
    for food in food_items:
        name = food[1]
        food_id = food[0]  # Taom ID
        keyboard.append([InlineKeyboardButton(name, callback_data=f"order_{food_id}")])

    # Inline keyboardni yuborish
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Buyurtma berish uchun taomlardan birini tanlang:", reply_markup=reply_markup)

# Buyurtma qilish
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Callback data orqali taom ID olish
    food_id = int(query.data.split("_")[1])
    user_id = query.from_user.id

    # Foydalanuvchi buyurtma berishi uchun ro'yxatda bo'lishi kerak
    user = db.get_user(user_id)
    if not user:
        query.edit_message_text("Siz ro'yxatdan o'tmagan ekansiz. Iltimos, avval ro'yxatdan o'ting.")
        return

    
    food = db.get_food_by_id(food_id)
    if food:
        db.delete_order(food.id)  
    
    if not db.exists_food(food_id):
        query.edit_message_text("Uzr, bu taom hozirda mavjud emas.")
        return
        
    db.order_food(user[0], food_id)  # user[0] is the user's id
    query.edit_message_text(f"{food[1]} taomni muvaffaqiyatli buyurtma qildingiz.")

# Taom qo'shish
def add_food(update: Update, context: CallbackContext):
    # Admin uchun taom qo'shish komandasini yaratish
    chat_id = update.message.chat_id
    if chat_id not in ADMIN_CHAT_IDS:
        update.message.reply_text("Sizda bu amalni bajarish huquqi yo'q.")
        return

    if update.message.photo:
        image = update.message.photo[-1].file_id  # Rasmdan image id olish
        name = update.message.caption if update.message.caption else "Taom nomi yo'q"

        db.add_food(name, image)  # Rasmdagi caption taom nomi bo'ladi
        update.message.reply_text(f"{name} taomi bazaga qo'shildi.")
    elif update.message.text.startswith("/add_food"):
        name = update.message.text[9:]  # /add_food buyurtmasi
        db.add_food(name, None)
        update.message.reply_text(f"{name} taomi bazaga qo'shildi.")

# Buyurtmalar ro'yxatini yuborish
def get_orders(update: Update, context: CallbackContext):
    orders = db.get_all_orders()
    message = "Bugungi buyurtmalar ro'yxati:\n\n"

    for order in orders:
        user = db.get_user_by_id(order[1])
        food = db.get_food_by_id(order[4])
        message += f"{user[1]} buyurtma berdi: {food[1]}\n"

    update.message.reply_text(message)

# Har kuni 9:00 vaqtda taomlar ro'yxatini yuborish (O'zbekiston vaqti)
def send_food_daily(update: Update, context: CallbackContext):
    send_food_list(update, context)

# Har kuni 9:45 vaqtda buyurtmalar ro'yxatini yuborish (O'zbekiston vaqti)
def send_orders_daily(update: Update, context: CallbackContext):
    orders = db.get_all_order()
    message = "Bugungi buyurtmalar:\n\n"
    total_orders = {}

    for order in orders:
        food = db.get_food_by_id(order[4])
        if food:
            if food[1] not in total_orders:
                total_orders[food[1]] = 1
            else:
                total_orders[food[1]] += 1

    for food_name, count in total_orders.items():
        message += f"{food_name} - {count} taom\n"

    chat_ids = db.get_chat_ids()
    for chat_id in chat_ids:
        context.bot.send_message(chat_id=chat_id, text=message)

# Har kuni 9:00 vaqtda taomlar ro'yxatini yuborish
def schedule_jobs(updater: Updater):
    job_queue = updater.job_queue
    chat_ids = db.get_chat_ids()
    for chat_id in chat_ids:   
        job_queue.run_daily(send_food_daily, time(9, 0, 0), context=chat_id)  # 9:00
        job_queue.run_daily(send_orders_daily, time(9, 45, 0), context=chat_id)  # 9:45

# Start komandasini yaratish
def start(update: Update, context: CallbackContext):
    user = db.get_user(update.message.chat_id)
    
    # Agar foydalanuvchi ro'yxatdan o'tmagan bo'lsa, uni ro'yxatga olishni taklif qilamiz
    if not user:
        update.message.reply_text("Salom! Men sizga taom buyurtma qilishda yordam beraman. Iltimos, ro'yxatdan o'ting: /register")
    else:
        update.message.reply_text("Salom! Buyurtma qilish uchun quyidagi taomlar ro'yxatini ko'ring:")

    # Taomlar ro'yxatini yuboramiz
    send_food_list(update, context)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Komandalar qo'shish
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("register", register))
    # dp.add_handler(CommandHandler("order", get_order))
    dp.add_handler(CommandHandler("orders", get_orders))
    dp.add_handler(CommandHandler("add_food", add_food))
    # dp.add_handler(CommandHandler("delete_food", delete_food))

    # Har bir foydalanuvchi yuborgan xabarni qabul qilish
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, order))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo | Filters.text, add_food))

    # Botni ishga tushurish
    schedule_jobs(updater)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
