import os
from flask import Flask, jsonify, request
from brain import ask_astra

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


@app.get("/")
def home():
    return jsonify({
        "assistant": "Astra",
        "status": "online",
        "message": "Hello! Astra is ready."
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "assistant": "Astra"})


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    history = data.get("history", [])

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message."}), 400

    if not isinstance(history, list):
        return jsonify({"error": "History must be a list."}), 400

    try:
        reply = ask_astra(message.strip(), history)
        return jsonify({
            "assistant": "Astra",
            "reply": reply
        })
    except RuntimeError as error:
        app.logger.warning("Astra configuration error: %s", error)
        return jsonify({
            "error": "Astra's AI service needs configuration. Check the server settings."
        }), 503
    except Exception:
        app.logger.exception("Astra chat failed")
        return jsonify({
            "error": "Astra couldn't respond. Please try again."
        }), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
