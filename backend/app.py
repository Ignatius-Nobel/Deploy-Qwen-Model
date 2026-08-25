"""
Backend — Qwen2.5-0.5B-Instruct chatbot
POST /chat  {"message": "..."}  →  {"reply": "...", "pod": "..."}
GET  /health
"""
import os, socket
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Use all available CPU cores for inference
_threads = int(os.getenv("NUM_THREADS", str(os.cpu_count() or 4)))
torch.set_num_threads(_threads)
torch.set_num_interop_threads(_threads)

app   = Flask(__name__)
HOST  = socket.gethostname()
MODEL = os.getenv("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

print(f"[backend] loading {MODEL} ...", flush=True)
tok   = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
model.eval()
print("[backend] ready.", flush=True)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "pod": HOST})


@app.route("/chat", methods=["POST"])
def chat():
    msg = (request.json or {}).get("message", "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400
    msgs = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": msg},
    ]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids  = tok([text], return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=64, do_sample=False)
    reply = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True).strip()
    return jsonify({"reply": reply, "pod": HOST})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))
