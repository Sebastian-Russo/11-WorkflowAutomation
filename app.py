"""
Thin Flask layer — same pattern as every other project.
The only new thing here is conversation_history, which gets
passed back and forth between the browser and server so Claude
remembers what was said earlier in the conversation.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from src.assistant import Assistant

app       = Flask(__name__, static_folder="static")
CORS(app)
assistant = Assistant()

# Store conversation histories in memory keyed by session ID
# In production you'd use Redis or a database — for personal use this is fine
conversations = {}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data       = request.get_json()
    message    = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Load existing conversation history for this session
    history = conversations.get(session_id, [])

    result = assistant.chat(message, conversation_history=history)

    # Save updated history back
    conversations[session_id] = result["history"]

    return jsonify({
        "response":   result["response"],
        "tools_used": result["tools_used"]
    })


@app.route("/reset", methods=["POST"])
def reset():
    """Clear conversation history for a session."""
    data       = request.get_json()
    session_id = data.get("session_id", "default")
    conversations.pop(session_id, None)
    return jsonify({"status": "reset"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
