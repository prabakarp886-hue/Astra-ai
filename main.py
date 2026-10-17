import os
import logging
from flask import Flask, jsonify, request, render_template
from brain import ask_astra

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "assistant": "Astra"
    }), 200


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "")
    history = data.get("history", [])

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Please enter a message."
        }), 400

    if not isinstance(history, list):
        return jsonify({
            "error": "Chat history must be a list."
        }), 400

    try:
        reply = ask_astra(message.strip(), history)

        if not isinstance(reply, str) or not reply.strip():
            app.logger.error("Astra returned an empty response.")
            return jsonify({
                "error": "Astra received an empty response. Please try again."
            }), 502

        return jsonify({
            "assistant": "Astra",
            "reply": reply.strip()
        }), 200

    except RuntimeError as exc:
        app.logger.error("Astra AI configuration/API error: %s", str(exc))

        return jsonify({
            "error": str(exc)
        }), 503

    except Exception:
        app.logger.exception("Unexpected error in Astra chat.")

        return jsonify({
            "error": "Astra couldn't respond right now. Please check the Render logs and try again."
        }), 502


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "error": "Your message is too large. Please send a shorter message."
    }), 413


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "error": "The requested page was not found."
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.exception("Internal server error.")

    return jsonify({
        "error": "Astra encountered a server error. Please try again."
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)