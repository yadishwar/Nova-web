from flask import Flask, jsonify, render_template, request

from config import APP_NAME, MAX_INPUT_CHARS, OPENROUTER_MODEL
from openrouter_client import OpenRouterError, ask_claude

app = Flask(__name__)


def clean_messages(raw):
    """Validate the incoming chat history. Returns (messages, error)."""
    if not isinstance(raw, list) or not raw:
        return None, "Please type a message."
    cleaned = []
    for item in raw:
        if not isinstance(item, dict):
            return None, "Invalid message format."
        role, content = item.get("role"), item.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            return None, "Invalid message format."
        content = content.strip()
        if content:
            cleaned.append({"role": role, "content": content})
    if not cleaned or cleaned[-1]["role"] != "user":
        return None, "Please type a message."
    if len(cleaned[-1]["content"]) > MAX_INPUT_CHARS:
        return None, f"Message is too long (max {MAX_INPUT_CHARS} characters)."
    return cleaned, None


@app.get("/")
def index():
    return render_template("index.html", app_name=APP_NAME, model=OPENROUTER_MODEL)


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages, error = clean_messages(data.get("messages"))
    if error:
        return jsonify(error=error), 400
    try:
        reply = ask_claude(messages)
    except OpenRouterError as exc:
        return jsonify(error=str(exc)), exc.status
    except Exception:
        app.logger.exception("Unexpected error")
        return jsonify(error="Something went wrong on the server. Please try again."), 500
    return jsonify(reply=reply)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
