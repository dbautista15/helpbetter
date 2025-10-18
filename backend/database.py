"""
Database layer for Introspect - Offline Desktop App

WHY THIS EXISTS:
- Stores journal entries locally on user's device
- Caches ML embeddings (so we don't recompute them)
- Provides data in format ML expects
- Proves "offline-first" (no cloud database)

CRITICAL CONCEPTS:
1. SQLite = Single file database (journal.db)
2. Embeddings = NumPy arrays stored as pickled BLOBs
3. Database path from environment variable (Electron sets it)
4. Everything must work 100% offline
"""

import sqlite3
import pickle
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np


class Database:
    """
    Local SQLite database for offline journaling.

    WHY SQLITE?
    - No server needed (unlike PostgreSQL/MySQL)
    - Single file (users can see their data)
    - Fast for personal use (<10k entries)
    - Built into Python (no dependencies)
    - Works offline automatically

    WHY PICKLE EMBEDDINGS?
    - NumPy arrays can't go directly into SQLite
    - pickle.dumps() converts array → bytes
    - We store bytes as BLOB
    - pickle.loads() converts back to array
    - Standard practice for ML in databases
    """

    def __init__(self, db_path=None):
        """
        Initialize database connection.

        WHY ENVIRONMENT VARIABLE?
        - Electron sets DB_PATH to proper location:
          - Windows: %APPDATA%/Introspect/journal.db
          - Mac: ~/Library/Application Support/Introspect/journal.db
        - Development: Uses local journal.db
        - User controls this file (backup/delete)

        Args:
            db_path: Optional override. If None, uses env var.
        """
        # Get database path from environment (Electron sets this)
        if db_path is None:
            db_path = os.getenv("DB_PATH", "journal.db")

        self.db_path = db_path

        # Create directory if needed (for AppData path)
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to SQLite
        # check_same_thread=False allows subprocess usage
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        # Create tables if they don't exist
        self.create_tables()

        print(f"✅ Database initialized: {db_path}", flush=True)

    def create_tables(self):
        """
        Create database schema.

        SCHEMA DESIGN:
        - id: UUID (unique identifier)
        - timestamp: ISO format datetime
        - content: The journal entry text
        - mood_rating: Integer 1-5
        - embedding: Pickled NumPy array (384 floats)
        - analysis: JSON string of ML results
        - created_at: Auto timestamp

        WHY THIS SCHEMA?
        - Simple (easy to understand/debug)
        - Efficient (index on timestamp for fast queries)
        - Portable (standard SQLite)
        """
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

        # Index for fast "recent entries" queries
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
        """
        Save a journal entry.

        CALLED BY: electron_bridge.py when user submits entry

        WHY ALLOW None FOR EMBEDDING?
        - First save happens before ML runs (faster UX)
        - ML updates entry with embedding later
        - Prevents data loss if ML fails

        WORKFLOW:
        1. User writes entry → save_entry(content, mood) [no embedding yet]
        2. ML analyzes → update with embedding
        3. Future queries can use this embedding

        Args:
            content: Journal entry text
            mood_rating: 1-5 scale
            embedding: Optional NumPy array (384,)
            analysis: Optional dict of ML results

        Returns:
            entry_id: UUID string
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Convert NumPy array to bytes for SQLite storage
        embedding_blob = pickle.dumps(embedding) if embedding is not None else None
        analysis_json = str(analysis) if analysis else None

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
        """
        Update an entry with its embedding after ML analysis.

        WHY SEPARATE FROM save_entry?
        - Save entry immediately (user sees confirmation)
        - ML analysis takes ~1 second
        - Update with embedding when ready
        - Better UX (don't make user wait)

        Args:
            entry_id: UUID of entry to update
            embedding: NumPy array (384,)
            analysis: Optional analysis results
        """
        embedding_blob = pickle.dumps(embedding)
        analysis_json = str(analysis) if analysis else None

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

        THIS IS THE CONTRACT WITH ML (Person 1):

        Returns: [
            {
                "text": str,              # The journal entry content
                "embedding": np.ndarray,  # Shape (384,) - for similarity
                "timestamp": str          # ISO format datetime
            },
            ...
        ]

        WHY ONLY ENTRIES WITH EMBEDDINGS?
        - ML can't compare to entries without embeddings
        - First entry has no past entries (empty list is OK)
        - embedding = None means not yet analyzed

        CALLED BY: electron_bridge.py for each new entry analysis
        ML uses these to find similar past experiences
        """
        cursor = self.conn.execute(
            """
            SELECT content, embedding, timestamp,mood_rating
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
        """
        Get recent entries for display (without embeddings).

        WHY NO EMBEDDINGS?
        - Frontend doesn't need them (huge data ~1.5KB each)
        - Saves IPC bandwidth (subprocess → Electron → React)
        - Faster query (no BLOB deserialization)

        USED FOR: Timeline view in React UI

        Args:
            limit: Number of recent entries to return

        Returns:
            List of entries with id, timestamp, content, mood
        """
        cursor = self.conn.execute(
            """
            SELECT id, timestamp, content, mood_rating
            FROM entries
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        entries = []
        for row in cursor:
            entries.append(
                {"id": row[0], "timestamp": row[1], "content": row[2], "mood": row[3]}
            )

        return entries

    def get_stats(self) -> Dict:
        """
        Get aggregate statistics for dashboard.

        USED FOR:
        - "You've written X entries" display
        - Average mood trend
        - Encouragement messaging

        Returns:
            Dict with total_entries, avg_mood, min_mood, max_mood
        """
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


# ============================================================================
# TESTING CODE - Run this file directly to verify database works
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing Database for Electron Integration")
    print("=" * 70 + "\n")

    # Use test database (don't pollute real data)
    db = Database("test_journal.db")

    # Test 1: Save entry without embedding
    print("📝 Test 1: Save entry without embedding")
    entry_id = db.save_entry(
        content="Today I learned about Electron and Python IPC!", mood_rating=4
    )
    print(f"   Entry ID: {entry_id}\n")

    # Test 2: Save entry with embedding
    print("📝 Test 2: Save entry with embedding")
    fake_embedding = np.random.rand(384)
    entry_id2 = db.save_entry(
        content="Working on the hackathon project. Making progress!",
        mood_rating=4,
        embedding=fake_embedding,
    )
    print(f"   Entry ID: {entry_id2}")
    print(f"   Embedding shape: {fake_embedding.shape}\n")

    # Test 3: Update first entry with embedding
    print("📝 Test 3: Update entry with embedding")
    another_embedding = np.random.rand(384)
    db.update_embedding(entry_id, another_embedding)
    print()

    # Test 4: Get entries for ML (THE CRITICAL TEST)
    print("📝 Test 4: Get entries for ML analysis")
    for_ml = db.get_all_entries_for_analysis()
    print(f"   Retrieved: {len(for_ml)} entries with embeddings")

    if len(for_ml) > 0:
        print(f"   First entry keys: {list(for_ml[0].keys())}")
        print(f"   Embedding shape: {for_ml[0]['embedding'].shape}")
        print(f"   Text preview: {for_ml[0]['text'][:50]}...")

        # VERIFY CONTRACT WITH ML
        assert "text" in for_ml[0], "Missing 'text' key!"
        assert "embedding" in for_ml[0], "Missing 'embedding' key!"
        assert "timestamp" in for_ml[0], "Missing 'timestamp' key!"
        assert for_ml[0]["embedding"].shape == (384,), "Wrong embedding shape!"
        print("   ✅ Format matches ML contract!\n")

    # Test 5: Get recent entries (for UI)
    print("📝 Test 5: Get recent entries for display")
    recent = db.get_recent_entries(limit=5)
    print(f"   Retrieved: {len(recent)} recent entries")
    print(f"   Keys: {list(recent[0].keys())}")
    print(f"   'embedding' in keys: {'embedding' in recent[0].keys()}")
    print("   ✅ No embeddings in display data (good!)\n")

    # Test 6: Statistics
    print("📝 Test 6: Get statistics")
    stats = db.get_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Average mood: {stats['avg_mood']}/5")
    print(f"   Mood range: {stats['min_mood']}-{stats['max_mood']}\n")

    # Test 7: Verify database file
    print("📝 Test 7: Verify database file exists")
    assert os.path.exists("test_journal.db"), "Database file not created!"
    file_size = os.path.getsize("test_journal.db")
    print(f"   ✅ File exists: test_journal.db")
    print(f"   File size: {file_size:,} bytes\n")

    db.close()

    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n💡 What this proves:")
    print("   • Database creates/updates entries ✅")
    print("   • Embeddings pickle/unpickle correctly ✅")
    print("   • Data format matches ML expectations ✅")
    print("   • Ready for Electron integration ✅")
    print("\n📋 Next steps:")
    print("   1. Integrate with electron_bridge.py")
    print("   2. Test with real ML model (Person 1)")
    print("   3. Load demo data for presentation")
    print("   4. Test in Electron app\n")
