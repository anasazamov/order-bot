import logging
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram.ext import Updater
from apscheduler.schedulers.background import BackgroundScheduler
from get_db import DB  # DB faylini import qilish

ADMIN_CHAT_IDS = [1698951222]

# Loggingni yoqish
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# DBni yaratish
db = DB()
db.startup()

TOKEN = '8072666419:AAGplm6gIS9lW-oGySMcHVg0NHkc6ZGvEag'


def send_food_list(update: Update, context: CallbackContext):

    if update.message:
        msg = update.message
    else:
        msg = update.callback_query.message

    food_items = db.get_food()

    
    
    if not food_items:
        update.message.reply_text("Hozirda mavjud taomlar yo'q.")
        return
    
    if update.callback_query and update.callback_query.data.startswith("page_"):
        page = int(update.callback_query.data.split("_")[-1])
    else:
        page = 1

    start = (page - 1) * 1
    end = page * 1

    if page > 1:
        back = InlineKeyboardButton("⬅️", callback_data=f"page_{page - 1}")
    else:
        back = None

    if end < len(food_items):
        previus = InlineKeyboardButton("➡️", callback_data=f"page_{page + 1}")
    else:
        previus = None

    food_items = food_items[start:end]
    food = food_items[-1]
    
    name = food['name']
    food_id = food['id']  
    image = food['image']

    food = InlineKeyboardButton(name, callback_data=f"order_{food_id}")

    if back and previus:
        keyboard = [[back, food, previus]]
    elif back and not previus:
        keyboard = [[back, food]]
    elif not back and previus:
        keyboard = [[food, previus]]
    elif not back and not previus:
        keyboard = [[food]]
    elif back and not previus:
        keyboard = [[back, food]]
    else:
        keyboard = [[food]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if image:
        msg.delete()
        return msg.reply_photo(photo=image, caption=name, reply_markup=reply_markup)
    msg.delete()
    msg.reply_text(name, reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data.startswith("page_"):
        send_food_list(update, context)
        return
    
    food_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id

    user = db.get_user(user_id)
    if not user:
        query.edit_message_text("Siz ro'yxatdan o'tmagan ekansiz. Iltimos, avval ro'yxatdan o'ting.")
        return

    
    food = db.get_food_by_id(food_id)
    if food:
        db.delete_order(food['id'])  
    
    if not db.exists_food(food_id):
        query.edit_message_text("Uzr, bu taom hozirda mavjud emas.")
        return
    food = db.get_food_by_ids(food_id)
    print(food)
    db.order_food(user[0], food)
    query.message.delete()
    query.message.reply_text(f"{food['name']} taomni muvaffaqiyatli buyurtma qildingiz.")


def add_food(update: Update, context: CallbackContext):
    
    chat_id = update.message.chat_id
    if chat_id not in ADMIN_CHAT_IDS:
        update.message.reply_text("Sizda bu amalni bajarish huquqi yo'q.")
        return

    if update.message.photo:
        image = update.message.photo[-1].file_id  
        name = update.message.caption if update.message.caption else "Taom nomi yo'q"

        db.add_food(name, image)  
        update.message.reply_text(f"{name} taomi bazaga qo'shildi.")
    elif update.message.text.startswith("/add_food"):
        name = update.message.text[9:]  
        db.add_food(name, None)
        update.message.reply_text(f"{name} taomi bazaga qo'shildi.")

def get_orders(update: Update, context: CallbackContext):
    orders = db.get_all_orders()
    message = "Bugungi buyurtmalar ro'yxati:\n\n"
    today_orders = db.get_today_orders_summary()
    txt = "Umumi buyurtmalar soni:\n\n"

    for food_name, count in today_orders.items():
        txt += f"<b>{food_name}</b> - {count} taom\n"

    for order in orders:
        user = order['user_id']['name']
        food = db.get_food_by_ids(order['food_id'])
        message += f"<b>{user}</b> buyurtma berdi: <b>{food['name']}</b>\n"

    update.message.reply_text(message, parse_mode='HTML')
    update.message.reply_text(txt, parse_mode='HTML')
    

def send_food_daily(update: Update, context: CallbackContext, chat_id):
    send_food_list(update, context)

def send_orders_daily(update: Update, context: CallbackContext, chat_id):
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
        message += f"{food_name} - {count} ta\n"

    chat_ids = db.get_chat_ids()
    for chat_id in chat_ids:
        context.bot.send_message(chat_id=chat_id, text=message)

def send_orders_at_11(context):
    today_orders = db.get_today_orders_summary()
    message = "Bugungi buyurtmalar:\n\n"
    for food_name, count in today_orders.items():
        message += f"{food_name} - {count} ta\n"
    chat_ids = db.get_chat_ids()
    for chat_id in chat_ids:
        context.bot.send_message(chat_id=chat_id, text=message)

def send_orders_at_11_30(context):
    today_orders = db.get_today_orders_summary()
    message = "Bugungi buyurtmalar:\n\n"
    for food_name, count in today_orders.items():
        message += f"{food_name} - {count} ta\n"
    chat_ids = db.get_chat_ids()
    for chat_id in chat_ids:
        context.bot.send_message(chat_id=chat_id, text=message)

def schedule_jobs(updater, context):
    scheduler = BackgroundScheduler()

    # Har kuni soat 11:00 da buyurtmalar ro'yxatini yuborish
    scheduler.add_job(
        send_orders_at_11, 'interval', hours=24, start_date='2025-02-13 11:00:00',
        timezone='Asia/Tashkent', kwargs={'context': context}  # contextni uzatish
    )

    # Har kuni soat 11:30 da buyurtmalar ro'yxatini yuborish
    scheduler.add_job(
        send_orders_at_11_30, 'interval', hours=24, start_date='2025-02-13 11:30:00',
        timezone='Asia/Tashkent', kwargs={'context': context}  # contextni uzatish
    )

    scheduler.start()


def start(update: Update, context: CallbackContext):
    user = db.get_user(update.message.chat_id)
    user_id = update.message.chat_id
    db.user_register(chat_id=user_id, name=update.message.from_user.full_name)
    
    if not user:
        update.message.reply_text("Salom! Men sizga taom buyurtma qilishda yordam beraman. Iltimos, ro'yxatdan o'ting: /register")
    else:
        update.message.reply_text("Salom! Buyurtma qilish uchun quyidagi taomlar ro'yxatini ko'ring:")

    
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
    dp.add_handler(CommandHandler("food", send_food_list))

    # Har bir foydalanuvchi yuborgan xabarni qabul qilish
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, order))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.photo | Filters.text, add_food))

    context = CallbackContext(dp)

    # Botni ishga tushurish
    schedule_jobs(updater, None)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
