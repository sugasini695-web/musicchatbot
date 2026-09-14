"""
app.py

Flask backend for the Music Chatbot.
Talks to the Gemini API (gemini-3.1-flash-lite) using a fixed system prompt
defined in chatbot_config.py so the bot only answers music-related questions.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

# Create the Gemini client once at startup
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


@app.route("/")
def home():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the Gemini model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
            contents=user_message,
        )
        reply_text = response.text or "Sorry, I couldn't come up with a reply."
        return jsonify({"reply": reply_text})

    except Exception as exc:  # noqa: BLE001
        app.logger.error("Gemini API error: %s", exc)
        return jsonify({"error": "Something went wrong while contacting the AI. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
