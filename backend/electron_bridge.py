"""
Electron Bridge - Python Subprocess WITH DATABASE
Communicates with Electron via stdin/stdout using JSON messages.

NOW WITH REAL DATABASE INTEGRATION!
"""

import sys
import json
import time
from database import Database

# Initialize database (Electron sets DB_PATH via environment variable)
db = Database()


def send_message(msg_type, data=None, error=None, request_id=None):
    """Send JSON message to Electron via stdout."""
    message = {"type": msg_type}
    if data is not None:
        message["data"] = data
    if error is not None:
        message["error"] = error
    if request_id is not None:
        message["requestId"] = request_id

    print(json.dumps(message), flush=True)


def handle_create_entry(data, request_id):
    """
    Handle create_entry command - NOW WITH REAL DATABASE!

    FLOW:
    1. Save entry to database (without embedding yet)
    2. Get past entries for ML comparison
    3. [TODO: Person 1 will add ML analysis here]
    4. [TODO: Update entry with embedding]
    5. Return response to Electron
    """
    try:
        content = data.get("content", "")
        mood_rating = data.get("mood_rating", 3)

        sys.stderr.write(f"📝 Saving entry to database...\n")
        sys.stderr.flush()

        # REAL DATABASE SAVE!
        entry_id = db.save_entry(content=content, mood_rating=mood_rating)

        sys.stderr.write(f"✅ Entry saved: {entry_id}\n")
        sys.stderr.flush()

        # Get past entries for ML analysis
        past_entries = db.get_all_entries_for_analysis()
        sys.stderr.write(f"📦 Retrieved {len(past_entries)} past entries\n")
        sys.stderr.flush()

        # TODO: Person 1 (ML) will replace this with real analysis
        # For now, using mock data so Electron still works
        #
        # INTEGRATION POINT FOR PERSON 1:
        # from ml.analyzer import Analyzer
        # analyzer = Analyzer()
        # analysis = analyzer.analyze_entry(content, past_entries)
        #
        # Then update entry with embedding:
        # db.update_embedding(entry_id, analysis['embedding'], analysis)

        # Simulate processing time (ML will be ~1 second)
        time.sleep(1)

        # Mock response (Person 1 will replace with real ML results)
        response = {
            "entry_id": entry_id,  # Real database ID!
            "insight": f"Entry saved to database! Mood: {mood_rating}/5. Once Person 1 integrates ML, you'll see real pattern analysis here. Current entries in database: {len(past_entries) + 1}",
            "similar_entries": (
                [
                    {
                        "text": (
                            entry["text"][:100] + "..."
                            if len(past_entries) > 0
                            else "No past entries yet"
                        ),
                        "similarity": 0.85,
                        "timestamp": entry["timestamp"],
                    }
                    for entry in past_entries[:3]  # Show top 3
                ]
                if len(past_entries) > 0
                else []
            ),
            "mood": {
                "detected": "positive" if mood_rating >= 3 else "negative",
                "confidence": 0.75,
            },
        }

        send_message("response", data=response, request_id=request_id)

    except Exception as e:
        sys.stderr.write(f"❌ Error in create_entry: {e}\n")
        sys.stderr.flush()
        send_message("error", error=str(e), request_id=request_id)


def handle_get_entries(data, request_id):
    """
    Get recent entries - NOW FROM REAL DATABASE!
    """
    try:
        limit = data.get("limit", 20)

        sys.stderr.write(f"📥 Getting {limit} entries from database...\n")
        sys.stderr.flush()

        # REAL DATABASE QUERY!
        entries = db.get_recent_entries(limit=limit)

        sys.stderr.write(f"✅ Retrieved {len(entries)} entries\n")
        sys.stderr.flush()

        response = {"entries": entries}
        send_message("response", data=response, request_id=request_id)

    except Exception as e:
        sys.stderr.write(f"❌ Error in get_entries: {e}\n")
        sys.stderr.flush()
        send_message("error", error=str(e), request_id=request_id)


def handle_get_stats(data, request_id):
    """
    Get statistics - NOW FROM REAL DATABASE!
    """
    try:
        sys.stderr.write(f"📊 Calculating statistics from database...\n")
        sys.stderr.flush()

        # REAL DATABASE STATS!
        stats = db.get_stats()

        sys.stderr.write(
            f"✅ Stats: {stats['total_entries']} entries, avg mood {stats['avg_mood']}\n"
        )
        sys.stderr.flush()

        send_message("response", data=stats, request_id=request_id)

    except Exception as e:
        sys.stderr.write(f"❌ Error in get_stats: {e}\n")
        sys.stderr.flush()
        send_message("error", error=str(e), request_id=request_id)


# Command dispatcher
COMMANDS = {
    "create_entry": handle_create_entry,
    "get_entries": handle_get_entries,
    "get_stats": handle_get_stats,
}


def main():
    """Main loop: Read from stdin, process commands, write to stdout."""

    # Signal ready to Electron
    send_message("ready")
    sys.stderr.write("✅ Python subprocess ready (with database!)\n")
    sys.stderr.flush()

    # Process commands from stdin
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            command = message.get("command")
            data = message.get("data", {})
            request_id = message.get("requestId")

            sys.stderr.write(f"📨 Received command: {command} (ID: {request_id})\n")
            sys.stderr.flush()

            if command in COMMANDS:
                COMMANDS[command](data, request_id)
            else:
                send_message(
                    "error", error=f"Unknown command: {command}", request_id=request_id
                )

        except json.JSONDecodeError as e:
            sys.stderr.write(f"❌ JSON decode error: {e}\n")
            sys.stderr.flush()
            send_message("error", error=f"Invalid JSON: {e}")
        except Exception as e:
            sys.stderr.write(f"❌ Unexpected error: {e}\n")
            sys.stderr.flush()
            send_message("error", error=f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
