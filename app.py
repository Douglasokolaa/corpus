import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import rag
import ingest

load_dotenv()

app = Flask(__name__)

if os.getenv("COHERE_API_KEY") and rag.get_collection().count() == 0:
    ingest.main()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    result = rag.answer(question)
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "chunks": rag.get_collection().count()})


@app.route("/docs/<doc_id>")
def doc(doc_id):
    return send_from_directory("docs", doc_id + ".md", mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
