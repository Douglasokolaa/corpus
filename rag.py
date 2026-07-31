import os
import time
import requests
import cohere
import chromadb

EMBED_MODEL = "embed-english-v3.0"
TOP_K = 4
MAX_DISTANCE = 0.7
REFUSAL = "I can only answer questions about our company policies, and I couldn't find anything relevant in them."

SYSTEM_PROMPT = """You answer employee questions about Acme Corporation policies.
Rules:
- Use ONLY the policy excerpts provided. Do not use outside knowledge.
- Cite the source of every fact with its doc id in square brackets, like [pto-policy].
- If the excerpts do not answer the question, reply exactly: "{refusal}"
- Keep answers under 150 words."""


def get_collection():
    client = chromadb.PersistentClient(path="chroma_db")
    return client.get_or_create_collection("policies", metadata={"hnsw:space": "cosine"})


def embed_query(question):
    co = cohere.Client(os.environ["COHERE_API_KEY"])
    resp = co.embed(texts=[question], model=EMBED_MODEL, input_type="search_query")
    return resp.embeddings[0]


def retrieve(question, k=TOP_K):
    col = get_collection()
    result = col.query(query_embeddings=[embed_query(question)], n_results=k)
    chunks = []
    for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        chunks.append({
            "text": text,
            "doc_id": meta["doc_id"],
            "title": meta["title"],
            "heading": meta["heading"],
            "distance": dist,
        })
    return chunks


def call_llm(messages):
    for attempt in range(4):
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
            json={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0,
            },
            timeout=60,
        )
        if resp.status_code == 429:
            time.sleep(5)
            continue
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        time.sleep(5)
    resp.raise_for_status()
    raise Exception("LLM call failed after retries: " + resp.text[:200])


def answer(question):
    chunks = retrieve(question)
    if not chunks or chunks[0]["distance"] > MAX_DISTANCE:
        return {"answer": REFUSAL, "sources": []}
    context = ""
    for c in chunks:
        context += "[{}] {} - {}\n{}\n\n".format(c["doc_id"], c["title"], c["heading"], c["text"])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(refusal=REFUSAL)},
        {"role": "user", "content": "Policy excerpts:\n\n" + context + "\nQuestion: " + question},
    ]
    text = call_llm(messages)
    sources = []
    seen = set()
    for c in chunks:
        if c["doc_id"] in seen:
            continue
        seen.add(c["doc_id"])
        sources.append({
            "doc_id": c["doc_id"],
            "title": c["title"],
            "heading": c["heading"],
            "snippet": c["text"][:300],
            "link": "/docs/" + c["doc_id"],
        })
    return {"answer": text, "sources": sources}
