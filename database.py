import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.con = sqlite3.connect(self.db_name)
    
    def create_tables(self):
        with self.con:
            self.con.execute(f"CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, username TEXT UNIQUE, state TEXT, point INTEGER DEFAULT 0)")
            self.con.execute(f"CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code INTEGER UNIQUE, video TEXT)")
            self.con.execute(f"CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER UNIQUE, channel_url TEXT)")
            self.con.commit()

    def add_user(self, user_id, username, state, point=0):
        with self.con:
            self.con.execute("INSERT OR IGNORE INTO users (user_id, username, state, point) VALUES (?, ?, ?, ?)", (user_id, username, state, point))
            self.con.commit()
    
    def get_user(self, user_id=None, username=None):
        with self.con:
            self.con.row_factory = sqlite3.Row
            if user_id:
                cursor = self.con.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                return dict(cursor.fetchone()) #if cursor.fetchone() else None
            elif username:
                cursor = self.con.execute("SELECT * FROM users WHERE username = ?", (username,))
                return dict(cursor.fetchone()) #if cursor.fetchone() else None
    
    def add_lesson(self, name, code, video):
        with self.con:
            self.con.execute("INSERT OR IGNORE INTO lessons (name, code, video) VALUES (?, ?, ?)", (name, code, video))
            self.con.commit()

    def get_lessons(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM lessons")
            return [dict(row) for row in cursor.fetchall()]

    def add_channel(self, channel_id, channel_url):
        with self.con:
            self.con.execute("INSERT OR IGNORE INTO channels (channel_id, channel_url) VALUES (?, ?)", (channel_id, channel_url))
            self.con.commit()
    
    def get_channels(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM channels")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_user_count(self):
        with self.con:
            cursor = self.con.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    
    def get_oddiy_users(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM users WHERE state = 'oddiy'")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_vip_users(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM users WHERE state = 'vip'")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_premium_users(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM users WHERE state = 'premium'")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_users(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def get_lesson(self, lesson_code):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM lessons WHERE code = ?", (lesson_code,))
            return dict(cursor.fetchone()) #if cursor.fetchone() else None
    
    def check_code(self, code):
        with self.con:
            cursor = self.con.execute("SELECT * FROM lessons WHERE code = ?", (code,))
            return bool(cursor.fetchone())
        
    def promote_user(self, promotion_type: str, username: str = None, user_id: int = None):
        with self.con:
            if username:
                self.con.execute("UPDATE OR IGNORE users SET state = ? WHERE username = ?", (promotion_type, username))
            elif user_id:
                self.con.execute("UPDATE OR IGNORE users SET state = ? WHERE user_id = ?", (promotion_type, user_id))
            self.con.commit()
    
    def demote_user(self, demote_type: str, username: str):
        with self.con:
            self.con.execute("UPDATE OR IGNORE users SET state = ? WHERE username = ?", (demote_type, username))
            self.con.commit()

    def add_points(self, username: str, points: int):
        with self.con:
            user = self.get_user(username=username)
            if user:
                new_points = user["point"] + points
                self.con.execute("UPDATE OR IGNORE users SET point = ? WHERE username = ?", (new_points, username))
                self.con.commit()
    
    def get_lessons_count(self):
        with self.con:
            cursor = self.con.execute("SELECT COUNT(*) FROM lessons")
            return cursor.fetchone()[0]
    
    def get_admins(self):
        with self.con:
            self.con.row_factory = sqlite3.Row
            cursor = self.con.execute("SELECT * FROM users WHERE state = 'admin'")
            return [dict(row) for row in cursor.fetchall()]

# db = Database("database.db")

# db.create_tables()

# print(db.add_channel(123456789, "https://t.me/example_channel"))
# print(db.get_channels())

# print(db.get_user(username="Tr_Muhammad"))