# Acme Policy Assistant (RAG)

A Retrieval-Augmented Generation app that answers questions about Acme Corporation's company policies. Built with Flask, Cohere embeddings, ChromaDB, and an OpenAI chat model. No LangChain — the pipeline is implemented directly.

## How it works

```
docs/*.md  ->  ingest.py (chunk by heading + embed with Cohere)  ->  chroma_db/ (local vector store)
user question  ->  embed  ->  top-4 similar chunks  ->  prompt with citations  ->  OpenAI LLM  ->  answer + sources
```

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

2. Get API keys:
   - Cohere (embeddings): https://dashboard.cohere.com/api-keys (trial key is free)
   - OpenAI (LLM): https://platform.openai.com/api-keys (paid, but `gpt-4o-mini` costs well under a cent per question)

3. Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

4. Build the vector index (run once, and again whenever docs change):

```bash
python ingest.py
```

5. Run the app:

```bash
python app.py
```

Open http://localhost:5000

## Endpoints

- `/` — web chat UI
- `/chat` — POST `{"question": "..."}`, returns `{"answer": ..., "sources": [...]}` with citations and snippets
- `/health` — returns `{"status": "ok"}`
- `/docs/<doc_id>` — serves the source policy document

## Tests

```bash
pytest -q
```

Tests cover the health endpoint, the chat input validation, and the chunking logic. They do not need API keys.

## Evaluation

With your `.env` keys set and the index built:

```bash
python eval/evaluate.py
```

Runs 22 questions (20 policy questions + 2 off-topic refusal checks), measures groundedness, citation accuracy, partial match, refusal accuracy, and latency p50/p95, and writes `eval/results.md`. See `design-and-evaluation.md` for details.

A full eval run makes ~40 LLM calls (20 answers + 20 judge calls); with `gpt-4o-mini` that costs a few cents. The app retries automatically on transient 429s.

## Reproducibility

There is no randomness in the pipeline: chunking is deterministic, retrieval uses fixed k=4, generation uses temperature 0, and the evaluation runs every question in fixed order (no sampling), so no seed is needed.

## Deployment (optional)

The app runs on Render/Railway free tiers with start command `gunicorn app:app`. Set `COHERE_API_KEY`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL` as environment variables, and run `python ingest.py` as a build step so the Chroma index exists on the instance.

## Project structure

```
app.py                  Flask app (/ , /chat, /health, /docs)
rag.py                  retrieval + generation pipeline
ingest.py               chunk + embed + store in ChromaDB
docs/                   20 synthetic policy documents (the corpus)
templates/index.html    chat UI
eval/questions.json     evaluation set
eval/evaluate.py        evaluation script (writes eval/results.md)
tests/test_app.py       smoke tests
.github/workflows/ci.yml  CI: install, import check, pytest
```
