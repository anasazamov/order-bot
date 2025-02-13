from sqlite3 import connect
from pathlib import Path

folder = str(Path(__file__).parent)

class DB:

    def get_db(self):
        return connect(f'{folder}/db.db')

    def get_cursor(self):
        return self.get_db().cursor()

    def startup(self):
        cursor = self.get_cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, chat_id BIGINT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS food (id INTEGER PRIMARY KEY, name TEXT, image TEXT)')
        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS orders (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                created_at DATE DEFAULT CURRENT_DATE,
                                user_id INTEGER,
                                food_id INTEGER,
                                FOREIGN KEY(user_id) REFERENCES users(id),
                                FOREIGN KEY(food_id) REFERENCES food(id)
                            )
                        ''')
        self.get_db().commit()
        self.get_db().close()

    def get_all_orders(self):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM orders WHERE created_at = CURRENT_DATE')
        return cursor.fetchall()

    def register_user(self, name, chat_id):
        cursor = self.get_cursor()
        cursor.execute('INSERT INTO users (name, chat_id) VALUES (?, ?)', (name, chat_id))
        self.get_db().commit()
        self.get_db().close()

    def order_food(self, user_id, food_id):
        cursor = self.get_cursor()
        cursor.execute('INSERT INTO orders (user_id, food_id) VALUES (?, ?)', (user_id, food_id))
        self.get_db().commit()
        self.get_db().close()

    def get_user(self, chat_id):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        return cursor.fetchone()

    def get_food(self):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM food')
        return cursor.fetchall()

    def get_food_by_id(self, food_id):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM food WHERE id = ?', (food_id,))
        return cursor.fetchone()

    def add_food(self, name, image):
        print(f"Adding food: {name}, {image}")  # Debugging uchun
        if image is None:
            image = "No image"
        cursor = self.get_cursor()
        print(cursor.execute('INSERT INTO food (name, image) VALUES (?, ?)', (name, image)))
        self.get_db().commit()  # O'zgarishlarni saqlash
        print("Food added successfully!")  # Bu yerga yozilsa, ma'lumot bazasiga qo'shilgan
        self.get_db().close()  # O'zgarishlarni saqlab, bazani yopish
        

    def delete_food(self, food_id):
        cursor = self.get_cursor()
        cursor.execute('DELETE FROM food WHERE id = ?', (food_id,))
        self.get_db().commit()
        self.get_db().close()

    def delete_order(self, order_id):
        cursor = self.get_cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        self.get_db().commit()
        self.get_db().close()

    def get_order_id_by_food_id(self, food_id):
        cursor = self.get_cursor()
        cursor.execute('SELECT id FROM orders WHERE food_id = ? AND created_at = CURRENT_DATE', (food_id,))
        return cursor.fetchone()

    def get_chat_ids(self):
        cursor = self.get_cursor()
        cursor.execute('SELECT chat_id FROM users')
        return cursor.fetchall()
    
    def get_current_orders(self):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM orders WHERE created_at = CURRENT_DATE')
        return cursor.fetchall()
    
    def get_user_order_current(self, user_id):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM orders WHERE user_id = ? AND created_at = CURRENT_DATE', (user_id,))
        return cursor.fetchall()
    
    def exists_food(self, food_id):
        cursor = self.get_cursor()
        cursor.execute('SELECT * FROM food WHERE id = ?', (food_id,))
        return cursor.fetchone() is not None
import os
print(os.path.exists(f'{folder}/db.sqlite3'))  # 