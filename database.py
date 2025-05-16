"""Database module for managing Discord messages storage in SQLite."""

import sqlite3
from typing import List, Dict, Any, Optional


class Database:
    def __init__(self, db_path: str = "discord_messages.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id     TEXT PRIMARY KEY,
            channel_id     TEXT,
            server_id      TEXT,
            author_id      TEXT,
            author_name    TEXT,
            content        TEXT,
            timestamp      INTEGER,
            edited_ts      INTEGER
        );
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chan_time
            ON messages(channel_id, timestamp);
        """)
        
        self.conn.commit()

    def insert_messages(self, messages: List[Dict[str, Any]]) -> int:
        inserted_count = 0
        for message in messages:
            try:
                self.cursor.execute("""
                INSERT OR REPLACE INTO messages 
                (message_id, channel_id, server_id, author_id, author_name, content, timestamp, edited_ts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message["message_id"],
                    message["channel_id"],
                    message["server_id"],
                    message["author_id"],
                    message["author_name"],
                    message["content"],
                    message["timestamp"],
                    message.get("edited_ts")
                ))
                inserted_count += 1
            except sqlite3.Error:
                pass
        
        self.conn.commit()
        return inserted_count

    def get_recent_messages(self, channel_id: str, since_ms: int) -> List[Dict[str, Any]]:
        self.cursor.execute("""
        SELECT * FROM messages 
        WHERE channel_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
        """, (channel_id, since_ms))
        
        rows = self.cursor.fetchall()
        return [{k: row[k] for k in row.keys()} for row in rows]

    def get_all_messages(self, channel_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        self.cursor.execute("""
        SELECT * FROM messages 
        WHERE channel_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (channel_id, limit))
        
        rows = self.cursor.fetchall()
        return [{k: row[k] for k in row.keys()} for row in rows]
        
    def get_messages(self, server_id: str, channel_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get messages for a specific server and channel"""
        self.cursor.execute("""
        SELECT * FROM messages 
        WHERE server_id = ? AND channel_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (server_id, channel_id, limit))
        
        rows = self.cursor.fetchall()
        return [{k: row[k] for k in row.keys()} for row in rows]

    def close(self) -> None:
        self.conn.close()


db = Database()
