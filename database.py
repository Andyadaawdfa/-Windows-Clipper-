import os
import sqlite3
from datetime import datetime

from config import DB_PATH, IMAGES_DIR


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                type         TEXT NOT NULL CHECK(type IN ('text', 'image')),
                content      TEXT,
                thumbnail    BLOB,
                content_hash TEXT NOT NULL,
                char_count   INTEGER DEFAULT 0,
                created_at   TEXT NOT NULL,
                is_pinned    INTEGER DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_history(content_hash);
            CREATE INDEX IF NOT EXISTS idx_type ON clipboard_history(type);
            CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_history(created_at DESC);
        """)
        self._conn.commit()

    def add_entry(self, entry_type: str, content: str, thumbnail: bytes | None,
                  content_hash: str, char_count: int) -> int:
        cursor = self._conn.execute(
            "SELECT id FROM clipboard_history WHERE content_hash = ?", (content_hash,)
        )
        if cursor.fetchone():
            return -1

        now = datetime.now().isoformat(timespec="seconds")
        cursor = self._conn.execute(
            "INSERT INTO clipboard_history (type, content, thumbnail, content_hash, char_count, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (entry_type, content, thumbnail, content_hash, char_count, now)
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_all_entries(self, search_query: str = "", entry_type: str = "all",
                        limit: int = 500, offset: int = 0) -> list[dict]:
        query = "SELECT * FROM clipboard_history"
        params: list = []
        conditions = []

        if entry_type in ("text", "image"):
            conditions.append("type = ?")
            params.append(entry_type)

        if search_query:
            conditions.append("content LIKE ?")
            params.append(f"%{search_query}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_entry_by_id(self, entry_id: int) -> dict | None:
        cursor = self._conn.execute(
            "SELECT * FROM clipboard_history WHERE id = ?", (entry_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_entry(self, entry_id: int) -> bool:
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return False

        if entry["type"] == "image" and entry["content"]:
            if os.path.exists(entry["content"]):
                os.remove(entry["content"])

        self._conn.execute("DELETE FROM clipboard_history WHERE id = ?", (entry_id,))
        self._conn.commit()
        return True

    def delete_all(self, entry_type: str = "all") -> int:
        if entry_type in ("text", "image"):
            cursor = self._conn.execute(
                "SELECT content, type FROM clipboard_history WHERE type = ?", (entry_type,)
            )
            entries = cursor.fetchall()
            for row in entries:
                if row["type"] == "image" and row["content"] and os.path.exists(row["content"]):
                    os.remove(row["content"])
            cursor = self._conn.execute(
                "DELETE FROM clipboard_history WHERE type = ?", (entry_type,)
            )
        else:
            cursor = self._conn.execute(
                "SELECT content, type FROM clipboard_history WHERE type = 'image'"
            )
            for row in cursor.fetchall():
                if row["content"] and os.path.exists(row["content"]):
                    os.remove(row["content"])
            cursor = self._conn.execute("DELETE FROM clipboard_history")

        self._conn.commit()
        return cursor.rowcount

    def get_stats(self) -> dict:
        cursor = self._conn.execute(
            "SELECT type, COUNT(*) as cnt FROM clipboard_history GROUP BY type"
        )
        stats = {"total": 0, "text": 0, "image": 0}
        for row in cursor.fetchall():
            stats[row["type"]] = row["cnt"]
            stats["total"] += row["cnt"]
        return stats

    def close(self):
        self._conn.close()
