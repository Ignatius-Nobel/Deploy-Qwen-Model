"""
Frontend — serves the chat UI and proxies requests to the backend.
GET  /       → index.html
POST /chat   → backend /chat
GET  /health
"""
import os, requests
from flask import Flask, request, jsonify, send_from_directory

app         = Flask(__name__, static_folder="static")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:5001")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    msg = (request.json or {}).get("message", "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400
    try:
        resp = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": msg},
            timeout=300,
        )
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Model is still thinking — try again in a moment."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
