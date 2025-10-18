"""
Electron Bridge - Python Subprocess
Communicates with Electron via stdin/stdout using JSON messages.

This is NOT an HTTP server - it's a subprocess that reads from stdin
and writes to stdout. This proves true offline capability.

Protocol:
- Electron sends: {"command": "create_entry", "data": {...}, "requestId": 123}
- Python returns: {"type": "response", "data": {...}, "requestId": 123}
- Python errors: {"type": "error", "error": "...", "requestId": 123}
"""

import sys
import json
import time


def send_message(msg_type, data=None, error=None, request_id=None):
    """Send JSON message to Electron via stdout."""
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
    Handle create_entry command.

    For now, returns mock data.
    Later, Person 1 (ML) will add real analysis here.
    Later, Person 2 (Database) will add real database save here.
    """
    try:
        content = data.get("content", "")
        mood_rating = data.get("mood_rating", 3)

        # Log to stderr (so Electron can see it, but it doesn't interfere with JSON)
        sys.stderr.write(f"📝 Processing entry: {content[:50]}...\n")
        sys.stderr.flush()

        # Simulate some processing time
        time.sleep(1)

        # Mock response (later this will be real ML analysis + database save)
        response = {
            "entry_id": 1,
            "insight": f"This is a test insight! Your mood rating was {mood_rating}/5. Once we connect the ML model, you'll see real pattern analysis here.",
            "similar_entries": [
                {
                    "text": "This is a mock similar entry from your past",
                    "similarity": 0.85,
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            ],
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
    Get recent entries.

    For now, returns mock data.
    Later, Person 2 (Database) will query real database here.
    """
    try:
        limit = data.get("limit", 20)

        sys.stderr.write(f"📥 Getting {limit} entries...\n")
        sys.stderr.flush()

        # Mock entries (later this will query real database)
        response = {
            "entries": [
                {
                    "id": 1,
                    "content": "Today I learned how Electron and Python communicate via IPC!",
                    "mood_rating": 5,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "insight": "You seem excited about learning new technology",
                },
                {
                    "id": 2,
                    "content": "Working on the hackathon project. Making good progress.",
                    "mood_rating": 4,
                    "timestamp": "2024-01-14T15:20:00Z",
                    "insight": "Productive day with steady focus",
                },
            ]
        }

        send_message("response", data=response, request_id=request_id)

    except Exception as e:
        sys.stderr.write(f"❌ Error in get_entries: {e}\n")
        sys.stderr.flush()
        send_message("error", error=str(e), request_id=request_id)


def handle_get_stats(data, request_id):
    """
    Get statistics.

    For now, returns mock data.
    Later, Person 2 (Database) will calculate real stats here.
    """
    try:
        sys.stderr.write(f"📊 Getting statistics...\n")
        sys.stderr.flush()

        response = {
            "total_entries": 42,
            "average_mood": 3.8,
            "entries_this_week": 7,
            "most_common_theme": "productivity and learning",
        }

        send_message("response", data=response, request_id=request_id)

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
    sys.stderr.write("✅ Python subprocess ready\n")
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
