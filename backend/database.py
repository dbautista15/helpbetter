"""
Database layer for Introspect - Offline Desktop App
"""

import sqlite3
import pickle
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
import sys
import json


class Database:
    """Local SQLite database for offline journaling."""

    def __init__(self, db_path=None):
        """Initialize database connection."""
        if db_path is None:
            db_path = os.getenv("DB_PATH", "journal.db")

        self.db_path = db_path

        # Create directory if needed
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to SQLite
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        # Create tables if they don't exist
        self.create_tables()

        print(f"✅ Database initialized: {db_path}", flush=True)

    def create_tables(self):
        """Create database schema."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                content TEXT NOT NULL,
                mood_rating INTEGER,
                embedding BLOB,
                analysis TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON entries(timestamp DESC)
        """
        )

        self.conn.commit()
        print("✅ Database tables created", flush=True)

    def save_entry(
        self,
        content: str,
        mood_rating: int,
        embedding: np.ndarray = None,
        analysis: dict = None,
    ) -> str:
        """Save a journal entry."""
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Convert NumPy array to bytes for SQLite storage
        embedding_blob = pickle.dumps(embedding) if embedding is not None else None

        # Use JSON instead of str() for proper serialization
        analysis_json = json.dumps(analysis) if analysis else None

        self.conn.execute(
            """
            INSERT INTO entries (id, timestamp, content, mood_rating, embedding, analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (entry_id, timestamp, content, mood_rating, embedding_blob, analysis_json),
        )

        self.conn.commit()

        print(f"✅ Saved entry: {entry_id[:8]}... (mood: {mood_rating})", flush=True)
        return entry_id

    def update_embedding(
        self, entry_id: str, embedding: np.ndarray, analysis: dict = None
    ):
        """Update an entry with its embedding after ML analysis."""
        embedding_blob = pickle.dumps(embedding)

        # Use JSON instead of str() for proper serialization
        analysis_json = json.dumps(analysis) if analysis else None

        self.conn.execute(
            """
            UPDATE entries 
            SET embedding = ?, analysis = ?
            WHERE id = ?
        """,
            (embedding_blob, analysis_json, entry_id),
        )

        self.conn.commit()
        print(f"✅ Updated embedding for: {entry_id[:8]}...", flush=True)

    def get_all_entries_for_analysis(self) -> List[Dict]:
        """
        Get entries in format ML needs.

        Returns: [
            {
                "text": str,
                "embedding": np.ndarray,
                "timestamp": str,
                "mood": int
            },
            ...
        ]
        """
        cursor = self.conn.execute(
            """
            SELECT content, embedding, timestamp, mood_rating
            FROM entries
            WHERE embedding IS NOT NULL
            ORDER BY timestamp DESC
        """
        )

        entries = []
        for row in cursor:
            # Unpickle bytes back to NumPy array
            embedding = pickle.loads(row[1])

            entries.append(
                {
                    "text": row[0],
                    "embedding": embedding,
                    "timestamp": row[2],
                    "mood": row[3],
                }
            )

        print(f"📦 Retrieved {len(entries)} entries for analysis", flush=True)
        return entries

    def get_recent_entries(self, limit: int = 20) -> List[Dict]:
        """Get recent entries for display (with summaries extracted from analysis)."""
        cursor = self.conn.execute(
            """
            SELECT id, timestamp, content, mood_rating, analysis
            FROM entries
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        entries = []
        for row in cursor:
            entry = {
                "id": row[0],
                "timestamp": row[1],
                "content": row[2],
                "mood": row[3],
            }

            # Parse JSON analysis (works for new entries, skips old ones)
            if row[4]:
                try:
                    analysis = json.loads(row[4])
                    if isinstance(analysis, dict) and "summary" in analysis:
                        entry["summary"] = analysis["summary"]
                        sys.stderr.write(
                            f"✅ Loaded summary for {row[0][:8]}: {analysis['summary']['title']}\n"
                        )
                        sys.stderr.flush()
                except Exception as e:
                    # Old entries with unparseable format - silently skip
                    sys.stderr.write(
                        f"⚠️ Could not parse analysis for {row[0][:8]} (probably old format)\n"
                    )
                    sys.stderr.flush()

            entries.append(entry)

        sys.stderr.write(f"✅ Retrieved {len(entries)} entries\n")
        sys.stderr.flush()
        return entries

    def get_stats(self) -> Dict:
        """Get aggregate statistics for dashboard."""
        cursor = self.conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                AVG(mood_rating) as avg_mood,
                MIN(mood_rating) as min_mood,
                MAX(mood_rating) as max_mood
            FROM entries
        """
        )

        row = cursor.fetchone()

        return {
            "total_entries": row[0] or 0,
            "avg_mood": round(row[1], 1) if row[1] else 0,
            "min_mood": row[2] or 0,
            "max_mood": row[3] or 0,
        }

    def close(self):
        """Close database connection cleanly."""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed", flush=True)
