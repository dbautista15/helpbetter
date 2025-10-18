"""
Electron Bridge - Python Subprocess with Database & ML Integration
Communicates with Electron via stdin/stdout using JSON messages.

ARCHITECTURE:
- Runs as subprocess spawned by Electron
- Reads commands from stdin (JSON)
- Writes responses to stdout (JSON)
- 100% offline (no HTTP, no network)
- Integrates database and ML analyzer

FLOW:
User writes entry → Electron IPC → This script → Database + ML → Response → Electron → User
"""

import sys
import json
import os
from database import Database
from ml.analyzer import Analyzer

# Initialize database
# Uses environment variable set by Electron, or falls back to local file
db_path = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "journal.db"))
db = Database(db_path)

# Initialize ML analyzer (loads model once at startup)
sys.stderr.write("🔄 Loading ML analyzer...\n")
sys.stderr.flush()
analyzer = Analyzer()
sys.stderr.write("✅ ML analyzer ready\n")
sys.stderr.flush()


def send_message(msg_type, data=None, error=None, request_id=None):
    """
    Send JSON message to Electron via stdout.

    Protocol:
    - ready: Signal that Python is initialized
    - response: Successful command result
    - error: Command failed with error message

    Args:
        msg_type: 'ready', 'response', or 'error'
        data: Response data (for 'response' type)
        error: Error message (for 'error' type)
        request_id: ID to match request with response
    """
    message = {"type": msg_type}
    if data is not None:
        message["data"] = data
    if error is not None:
        message["error"] = error
    if request_id is not None:
        message["requestId"] = request_id

    # Print JSON to stdout (Electron is listening)
    print(json.dumps(message), flush=True)


def handle_create_entry(data, request_id):
    """
    Handle create_entry command - FULL INTEGRATION!

    WORKFLOW:
    1. Save entry to database (without embedding yet)
    2. Get past entries for ML comparison
    3. Run ML analysis (generate embedding + find patterns)
    4. Update database with embedding
    5. Return analysis to Electron

    Args:
        data: {
            'content': str,      # Journal entry text
            'mood_rating': int   # 1-5 scale
        }
        request_id: Unique ID for this request
    """
    try:
        content = data.get("content", "")
        mood_rating = data.get("mood_rating", 3)

        sys.stderr.write(f"📝 Processing entry (mood: {mood_rating}/5)...\n")
        sys.stderr.flush()

        # Step 1: Save entry to database (without embedding yet - faster UX)
        entry_id = db.save_entry(content=content, mood_rating=mood_rating)
        sys.stderr.write(f"✅ Entry saved: {entry_id}\n")
        sys.stderr.flush()

        # Step 2: Get past entries for ML comparison
        past_entries = db.get_all_entries_for_analysis()
        sys.stderr.write(
            f"📦 Retrieved {len(past_entries)} past entries for analysis\n"
        )
        sys.stderr.flush()

        # Step 3: Run ML analysis
        sys.stderr.write(f"🧠 Running ML analysis...\n")
        sys.stderr.flush()

        analysis = analyzer.analyze_entry(content, past_entries)

        sys.stderr.write(
            f"✅ ML analysis complete: {analysis['mood']['detected']} mood\n"
        )
        sys.stderr.flush()

        # Step 4: Update database with embedding
        db.update_embedding(entry_id, analysis["embedding"], analysis)
        sys.stderr.write(f"✅ Embedding saved to database\n")
        sys.stderr.flush()

        # Step 5: Format response for Electron
        response = {
            "entry_id": entry_id,
            "insight": analysis["insight"],
            "similar_entries": analysis["similar_entries"],
            "mood": analysis["mood"],
        }

        send_message("response", data=response, request_id=request_id)

    except Exception as e:
        sys.stderr.write(f"❌ Error in create_entry: {e}\n")
        sys.stderr.flush()
        import traceback

        traceback.print_exc(file=sys.stderr)
        send_message("error", error=str(e), request_id=request_id)


def handle_get_entries(data, request_id):
    """
    Get recent entries from database.

    Used for timeline view in UI.
    Does NOT include embeddings (too large for UI).

    Args:
        data: {'limit': int}  # Number of entries to retrieve
        request_id: Unique ID for this request
    """
    try:
        limit = data.get("limit", 20)

        sys.stderr.write(f"📥 Getting {limit} entries from database...\n")
        sys.stderr.flush()

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
    Get statistics from database.

    Used for dashboard display.

    Args:
        data: {} (no parameters needed)
        request_id: Unique ID for this request
    """
    try:
        sys.stderr.write(f"📊 Calculating statistics...\n")
        sys.stderr.flush()

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


# Command dispatcher - maps command names to handler functions
COMMANDS = {
    "create_entry": handle_create_entry,
    "get_entries": handle_get_entries,
    "get_stats": handle_get_stats,
}


def main():
    """
    Main loop: Read from stdin, process commands, write to stdout.

    PROTOCOL:
    - Electron sends: {"command": "create_entry", "data": {...}, "requestId": 123}
    - Python processes command
    - Python responds: {"type": "response", "data": {...}, "requestId": 123}

    WHY STDIN/STDOUT?
    - No HTTP server needed
    - No ports to manage
    - Direct process communication
    - Provably offline
    - Faster than HTTP
    """

    # Signal ready to Electron
    send_message("ready")
    sys.stderr.write("✅ Python subprocess ready (with database + ML!)\n")
    sys.stderr.write(f"📁 Database: {db_path}\n")
    sys.stderr.flush()

    # Process commands from stdin (blocking loop)
    for line in sys.stdin:
        try:
            # Parse JSON command
            message = json.loads(line.strip())
            command = message.get("command")
            data = message.get("data", {})
            request_id = message.get("requestId")

            sys.stderr.write(f"📨 Received command: {command} (ID: {request_id})\n")
            sys.stderr.flush()

            # Dispatch to appropriate handler
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
            import traceback

            traceback.print_exc(file=sys.stderr)
            send_message("error", error=f"Unexpected error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("\n👋 Python subprocess shutting down\n")
        sys.stderr.flush()
        db.close()
    except Exception as e:
        sys.stderr.write(f"\n💥 Fatal error: {e}\n")
        sys.stderr.flush()
        import traceback

        traceback.print_exc(file=sys.stderr)
        db.close()
