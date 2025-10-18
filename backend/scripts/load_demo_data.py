"""
Load Demo Data for Introspect - Hackathon Presentation

WHY THIS EXISTS:
- Judges won't write 10 entries during 5-minute demo
- Pre-loaded data shows pattern detection IMMEDIATELY
- Showcases the "wow factor" in first 30 seconds

DESIGN PRINCIPLES:
- Show recurring themes (anxiety → preparation → success)
- Show what helped (talking to friends, exercise, therapy)
- Show mood variation (2s and 5s, not all 3s)
- Spread over 2 weeks for time progression
- Use different words for similar emotions (tests semantic search)
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

# Use environment variable for database path (same as Electron)
# If not set, uses local journal.db
db_path = os.getenv("DB_PATH", "journal.db")
db = Database(db_path)

# Demo entries designed to show clear patterns
demo_entries = [
    {
        "content": "Feeling really anxious about tomorrow's team presentation. What if I mess up and look incompetent? This always happens before big meetings. Can't sleep.",
        "mood": 2,
        "days_ago": 14,
    },
    {
        "content": "Had a great brainstorming session with Sarah today. We worked through the presentation together and I feel so much more prepared. Sometimes I just need to talk things through with someone.",
        "mood": 4,
        "days_ago": 12,
    },
    {
        "content": "Monday morning dread is back. Same pattern every single week - weekends are fine, but Sunday night the work anxiety creeps in. Why does this keep happening?",
        "mood": 2,
        "days_ago": 10,
    },
    {
        "content": "The presentation went way better than I expected! I was nervous at first but the preparation with Sarah really helped. Why do I always catastrophize beforehand when things usually turn out okay?",
        "mood": 5,
        "days_ago": 9,
    },
    {
        "content": "Feeling completely overwhelmed with three deadlines hitting this week. Don't even know where to start. This is exactly how I felt last month right before the burnout episode.",
        "mood": 2,
        "days_ago": 7,
    },
    {
        "content": "Took a long walk during lunch break and it really helped clear my head. Need to remember to do this more often when I'm stressed. Such a simple thing but so effective.",
        "mood": 3,
        "days_ago": 6,
    },
    {
        "content": "Another frustrating conflict with my manager today. I felt completely dismissed when I tried to share my ideas in the meeting. This same pattern keeps repeating and I don't know how to break it.",
        "mood": 2,
        "days_ago": 5,
    },
    {
        "content": "Really productive therapy session today. We talked about my pattern of seeking external validation and how it connects to my work anxiety. Starting to see how these things link together.",
        "mood": 4,
        "days_ago": 3,
    },
    {
        "content": "Spent the whole day procrastinating and now I feel guilty about it. Same exhausting cycle - anxiety about task leads to avoidance which leads to more anxiety. Need to find a way to break this loop.",
        "mood": 2,
        "days_ago": 2,
    },
    {
        "content": "Finished the big project a day early! Breaking it into smaller chunks like my therapist suggested actually worked. Feels amazing to prove my anxious thoughts wrong. Maybe I can handle more than I think.",
        "mood": 5,
        "days_ago": 1,
    },
    {
        "content": "Went to the gym this morning before work. Noticed I feel less anxious on days when I exercise. Connection between physical activity and mental state is real.",
        "mood": 4,
        "days_ago": 1,
    },
    {
        "content": "Had coffee with Emma and talked about the work stuff that's been bothering me. She reminded me that I felt this way before my last promotion too. Pattern: I doubt myself right before growth.",
        "mood": 4,
        "days_ago": 0,
    },
]


def load_demo_data():
    """
    Load demo entries into database WITH EMBEDDINGS.

    Each entry is backdated to create realistic timeline.
    Patterns emerge: anxiety → preparation → success.
    """
    print("\n" + "=" * 70)
    print("Loading Demo Data for Hackathon Presentation")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")
    print(f"Loading {len(demo_entries)} entries with emotional patterns...")
    print()

    # Check if database already has entries
    stats = db.get_stats()
    if stats["total_entries"] > 0:
        print(f"⚠️  Warning: Database already has {stats['total_entries']} entries")
        response = input("Delete existing entries and load demo data? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled. No changes made.")
            return

        # Clear existing entries
        db.conn.execute("DELETE FROM entries")
        db.conn.commit()
        print("✅ Cleared existing entries\n")

    # Import ML analyzer to generate embeddings
    print("🔄 Loading ML analyzer to generate embeddings...")
    from ml.analyzer import Analyzer

    analyzer = Analyzer()
    print("✅ ML analyzer loaded\n")

    # Load each demo entry
    for i, entry in enumerate(demo_entries, 1):
        # Calculate timestamp (backdate by days_ago)
        timestamp = datetime.now() - timedelta(days=entry["days_ago"])

        # Save entry to database
        entry_id = db.save_entry(content=entry["content"], mood_rating=entry["mood"])

        # Update timestamp to match days_ago
        db.conn.execute(
            "UPDATE entries SET timestamp = ? WHERE id = ?",
            (timestamp.isoformat(), entry_id),
        )
        db.conn.commit()

        # Generate embedding for this entry
        print(f"{i:2d}. Generating embedding... ", end="", flush=True)
        embedding = analyzer.model.encode(entry["content"])

        # Update entry with embedding
        db.update_embedding(entry_id, embedding)

        # Print progress
        preview = (
            entry["content"][:60] + "..."
            if len(entry["content"]) > 60
            else entry["content"]
        )
        mood_emoji = (
            "😊" if entry["mood"] >= 4 else "😐" if entry["mood"] == 3 else "😔"
        )

        print(
            f"✅ [{entry['days_ago']:2d} days ago] {mood_emoji} Mood: {entry['mood']}/5"
        )
        print(f"    {preview}")
        print()

    # Show final statistics
    print("=" * 70)
    stats = db.get_stats()
    print(f"✅ Successfully loaded {stats['total_entries']} demo entries")
    print()
    print("📊 Database Statistics:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Average mood: {stats['avg_mood']}/5")
    print(f"   Mood range: {stats['min_mood']}-{stats['max_mood']}")
    print()
    print("💡 These entries showcase:")
    print("   ✓ Recurring pattern: Anxiety before presentations")
    print("   ✓ What helps: Preparation with Sarah, therapy, exercise")
    print("   ✓ Emotional progression: Anxiety → Action → Success")
    print("   ✓ Self-awareness: User notices patterns over time")
    print("   ✓ Semantic similarity: 'anxious'/'worried'/'nervous' will match")
    print()
    print(f"📁 Database location: {db_path}")
    print()
    print("=" * 70)
    print("✅ Demo data ready for Electron app presentation!")
    print()
    print("🎯 Next steps:")
    print("   1. Run Electron app: cd ../electron && npm start")
    print("   2. Click 'Get Entries' to see timeline")
    print("   3. Write new entry: 'Nervous about next presentation'")
    print("   4. Watch ML detect pattern with past anxiety entries!")
    print()

    db.close()


if __name__ == "__main__":
    try:
        load_demo_data()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        db.close()
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        db.close()
