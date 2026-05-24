import sqlite3
import threading
from contextlib import contextmanager


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        # Allow use from different threads and protect access with a lock
        self.con = sqlite3.connect(self.db_name, check_same_thread=False)
        self.lock = threading.Lock()

    @contextmanager
    def _conn(self):
        """Context manager that yields the shared connection while holding a lock."""
        with self.lock:
            yield self.con
    
    def create_tables(self):
        with self._conn() as con:
            con.execute(f"CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, username TEXT UNIQUE, state TEXT, point INTEGER DEFAULT 0)")
            con.execute(f"CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code INTEGER UNIQUE, video TEXT)")
            con.execute(f"CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_url TEXT)")
            con.commit()

    def add_user(self, user_id, username, state, point=0):
        with self._conn() as con:
            con.execute("INSERT OR IGNORE INTO users (user_id, username, state, point) VALUES (?, ?, ?, ?)", (user_id, username, state, point))
            con.commit()
    
    def get_user(self, user_id=None, username=None):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            if user_id:
                cursor = con.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            elif username:
                cursor = con.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                return dict(row) if row else None
    
    def add_lesson(self, name, code, video):
        with self._conn() as con:
            con.execute("INSERT OR IGNORE INTO lessons (name, code, video) VALUES (?, ?, ?)", (name, code, video))
            con.commit()

    def get_lessons(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM lessons")
            return [dict(row) for row in cursor.fetchall()]

    def add_channel(self, channel_url):
        with self._conn() as con:
            con.execute("INSERT OR IGNORE INTO channels (channel_url) VALUES (?)", (channel_url,))
            con.commit()
    
    def get_channels(self):
        with self._conn() as con:
            cursor = con.execute("SELECT channel_url FROM channels")
            return [row[0] for row in cursor.fetchall()]

    def get_user_count(self):
        with self._conn() as con:
            cursor = con.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    
    def get_oddiy_users(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM users WHERE state = 'oddiy'")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_vip_users(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM users WHERE state = 'vip'")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_premium_users(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM users WHERE state = 'premium'")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_users(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def get_lesson(self, lesson_code):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM lessons WHERE code = ?", (lesson_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def check_code(self, code):
        with self._conn() as con:
            cursor = con.execute("SELECT * FROM lessons WHERE code = ?", (code,))
            return bool(cursor.fetchone())
        
    def promote_user(self, promotion_type: str, username: str = None, user_id: int = None):
        with self._conn() as con:
            if username:
                con.execute("UPDATE OR IGNORE users SET state = ? WHERE username = ?", (promotion_type, username))
            elif user_id:
                con.execute("UPDATE OR IGNORE users SET state = ? WHERE user_id = ?", (promotion_type, user_id))
            con.commit()
    
    def demote_user(self, demote_type: str, username: str):
        with self._conn() as con:
            con.execute("UPDATE OR IGNORE users SET state = ? WHERE username = ?", (demote_type, username))
            con.commit()

    def add_points(self, username: str, points: int):
        with self._conn() as con:
            user = self.get_user(username=username)
            if user:
                new_points = user["point"] + points
                con.execute("UPDATE OR IGNORE users SET point = ? WHERE username = ?", (new_points, username))
                con.commit()
    
    def get_lessons_count(self):
        with self._conn() as con:
            cursor = con.execute("SELECT COUNT(*) FROM lessons")
            return cursor.fetchone()[0]
    
    def get_admins(self):
        with self._conn() as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute("SELECT * FROM users WHERE state = 'admin'")
            return [dict(row) for row in cursor.fetchall()]
    
    def remove_lesson(self, code):
        with self._conn() as con:
            con.execute("DELETE FROM lessons WHERE code = ?", (code,))
            con.commit()
    
    def remove_channels(self):
        with self._conn() as con:
            con.execute("DELETE FROM channels")
            con.commit()

db = Database("database.db")

db.create_tables()

# print(db.get_channels())
