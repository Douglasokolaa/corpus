import os
import glob
import cohere
import chromadb
from dotenv import load_dotenv

load_dotenv()

CHUNK_WORDS = 300
OVERLAP_WORDS = 50
EMBED_MODEL = "embed-english-v3.0"


def read_doc(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    doc_id = os.path.splitext(os.path.basename(path))[0]
    title = doc_id
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return doc_id, title, text


def split_sections(text):
    sections = []
    heading = "Introduction"
    lines = []
    for line in text.splitlines():
        if line.startswith("## "):
            if lines:
                sections.append((heading, "\n".join(lines).strip()))
            heading = line[3:].strip()
            lines = []
        elif line.startswith("# "):
            continue
        else:
            lines.append(line)
    if lines:
        sections.append((heading, "\n".join(lines).strip()))
    return [(h, b) for h, b in sections if b]


def chunk_text(text, size=CHUNK_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    if len(words) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
        start += size - overlap
    return chunks


def build_chunks():
    chunks = []
    for path in sorted(glob.glob("docs/*.md")):
        doc_id, title, text = read_doc(path)
        for heading, body in split_sections(text):
            for piece in chunk_text(body):
                chunks.append({"doc_id": doc_id, "title": title, "heading": heading, "text": piece})
    return chunks


def main():
    chunks = build_chunks()
    print(len(chunks), "chunks from docs/")
    co = cohere.Client(os.environ["COHERE_API_KEY"])
    embeddings = []
    for i in range(0, len(chunks), 96):
        batch = chunks[i:i + 96]
        texts = [c["title"] + " - " + c["heading"] + "\n" + c["text"] for c in batch]
        resp = co.embed(texts=texts, model=EMBED_MODEL, input_type="search_document")
        embeddings.extend(resp.embeddings)
        print("embedded", i + len(batch), "/", len(chunks))
    client = chromadb.PersistentClient(path="chroma_db")
    try:
        client.delete_collection("policies")
    except Exception:
        pass
    col = client.create_collection("policies", metadata={"hnsw:space": "cosine"})
    col.add(
        ids=[c["doc_id"] + "-" + str(i) for i, c in enumerate(chunks)],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{"doc_id": c["doc_id"], "title": c["title"], "heading": c["heading"]} for c in chunks],
    )
    print("stored in chroma_db/")


if __name__ == "__main__":
    main()
