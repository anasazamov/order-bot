from tinydb import TinyDB, Query
from datetime import datetime

class DB:
    def __init__(self):
        self.db = TinyDB('db.json', indent=4)  # Ma'lumotlar bazasi fayli
        self.users_table = self.db.table('users')
        self.food_table = self.db.table('food')
        self.orders_table = self.db.table('orders')

    def startup(self):
        """TinyDB uchun boshlang'ich jadvalni yaratish"""
        # Ma'lumotlar bazasi avtomatik ravishda faylni yaratadi
        # if len(self.users_table.all()) == 0:
        #     self.users_table.insert_multiple([
        #         {'id': 1, 'name': 'John Doe', 'chat_id': 123456789},
        #         {'id': 2, 'name': 'Jane Doe', 'chat_id': 987654321}
        #     ])

        # if len(self.food_table.all()) == 0:
        #     self.food_table.insert_multiple([
        #         {'id': 1, 'name': 'Pizza', 'image': 'pizza.jpg'},
        #         {'id': 2, 'name': 'Burger', 'image': 'burger.jpg'}
        #     ])
    
    def get_all_orders(self):
        """Hozirgi kundagi barcha buyurtmalarni olish"""
        return self.orders_table.search(Query().created_at == datetime.now().strftime('%Y-%m-%d'))
    
    def get_today_orders_summary(self):
        """Bugungi buyurtmalarni va qaysi taomdan nechtadan buyurtma berilganini hisoblash"""
        # Hozirgi kunning sanasi
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Bugungi buyurtmalarni olish
        orders = self.orders_table.search(Query().created_at == today)
        
        # Taomlar bo'yicha buyurtmalarni hisoblash
        food_summary = {}

        for order in orders:
            food_id = order['food_id']
            food = self.food_table.get(Query().id == food_id)
            if food:
                food_name = food['name']
                if food_name not in food_summary:
                    food_summary[food_name] = 1
                else:
                    food_summary[food_name] += 1
        
        return food_summary

    def register_user(self, name, chat_id):
        """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
        user_id = len(self.users_table.all()) + 1  
        self.users_table.insert({'id': user_id, 'name': name, 'chat_id': chat_id})

    def order_food(self, user_id, food_id):
        """Foydalanuvchi buyurtma qilish"""
        food = self.food_table.get(Query().id == food_id)
        if food:
            order = {
                'user_id': user_id,
                'food_id': food_id,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            self.orders_table.insert(order)
            return order
        return None

    def get_user(self, chat_id):
        """Foydalanuvchini chat_id orqali olish"""
        return self.users_table.search(Query().chat_id == chat_id)

    def get_food(self):
        """Taomlar ro'yxatini olish"""
        return self.food_table.all()

    def get_food_by_id(self, food_id):
        """Taomni ID orqali olish"""
        return self.orders_table.get(Query().id == food_id, Query().created_at == datetime.now().strftime('%Y-%m-%d'))

    def add_food(self, name, image):
        """Yangi taom qo'shish"""
        food_id = len(self.food_table.all()) + 1  # Yangi taom ID
        self.food_table.insert({'id': food_id, 'name': name, 'image': image})
        return {'id': food_id, 'name': name, 'image': image}

    def delete_food(self, food_id):
        """Taomni o'chirish"""
        self.food_table.remove(Query().id == food_id)

    def delete_order(self, order_id):
        """Buyurtmani o'chirish"""
        self.orders_table.remove(Query().id == order_id)

    def get_chat_ids(self):
        """Barcha foydalanuvchilarning chat_id larini olish"""
        return [user['chat_id'] for user in self.users_table.all()]

    def exists_food(self, food_id):
        """Taom mavjudligini tekshirish"""
        return self.food_table.contains(Query().id == food_id)

    def get_user_order_current(self, user_id):
        """Foydalanuvchining hozirgi buyurtmalarini olish"""
        return self.orders_table.search(Query().user_id == user_id)
    
    def user_register(self, name, chat_id):
        """Foydalanuvchini ro'yxatdan o'tkazish"""
        if not self.get_user(chat_id):
            user_id = len(self.users_table.all()) + 1
            self.users_table.insert({'id': user_id, 'name': name, 'chat_id': chat_id})
            return True
        return False
    
    def get_food_by_ids(self, food_ids):
        """ID lar bo'yicha taomlarni olish"""
        return self.food_table.get(Query().id ==food_ids)


# Misol uchun ishlatish
# db = DB()
# db.startup()

# # Yangi foydalanuvchi ro'yxatga olish
# db.register_user('Alice', 123456789)

# # Taom qo'shish
# db.add_food('Pasta', 'pasta.jpg')

# # Buyurtma qilish
# db.order_food(1, 1)

# # Foydalanuvchilarni olish
# users = db.get_user(123456789)
# print("Foydalanuvchi:", users)

# # Taomlar ro'yxatini olish
# food = db.get_food()
# print("Taomlar:", food)

# # Buyurtmalar ro'yxatini olish
# orders = db.get_all_orders()
# print("Buyurtmalar:", orders)
