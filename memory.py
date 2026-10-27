"""Kalıcı hafıza (SQLite): konuşma geçmişi + uzun vadeli bilgiler."""
import datetime
import sqlite3


class Memory:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, role TEXT, text TEXT);
            CREATE TABLE IF NOT EXISTS facts(
                id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, text TEXT UNIQUE);
            """
        )
        self.db.commit()

    @staticmethod
    def _now():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def add_message(self, role, text):
        self.db.execute("INSERT INTO messages(ts, role, text) VALUES (?,?,?)", (self._now(), role, text))
        self.db.commit()

    def recent_messages(self, n):
        rows = self.db.execute("SELECT role, text FROM messages ORDER BY id DESC LIMIT ?", (n * 2,)).fetchall()
        rows.reverse()
        while rows and rows[0][0] != "user":
            rows.pop(0)
        return [{"role": r, "content": t} for r, t in rows]

    def remember(self, fact):
        try:
            self.db.execute("INSERT INTO facts(ts, text) VALUES (?,?)", (self._now(), fact.strip()))
            self.db.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def forget(self, needle):
        cur = self.db.execute("DELETE FROM facts WHERE text LIKE ?", (f"%{needle}%",))
        self.db.commit()
        return cur.rowcount

    def facts(self):
        return [t for (t,) in self.db.execute("SELECT text FROM facts ORDER BY id")]

    def search(self, query, limit=8):
        like = f"%{query}%"
        rows = self.db.execute(
            "SELECT ts, role, text FROM messages WHERE text LIKE ? ORDER BY id DESC LIMIT ?", (like, limit)
        ).fetchall()
        return [f"[{ts}] {'Sen' if r == 'user' else 'Zorvael'}: {t}" for ts, r, t in rows]
