import ingest
from app import app


def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_chat_requires_question():
    client = app.test_client()
    resp = client.post("/chat", json={})
    assert resp.status_code == 400


def test_split_sections():
    text = "# Title\n\n## A\nalpha\n\n## B\nbeta"
    assert ingest.split_sections(text) == [("A", "alpha"), ("B", "beta")]


def test_chunk_text():
    text = " ".join(["word"] * 700)
    chunks = ingest.chunk_text(text)
    assert len(chunks) == 3
    assert all(len(c.split()) <= 300 for c in chunks)


def test_build_chunks():
    chunks = ingest.build_chunks()
    assert len(chunks) > 100
    docs = {c["doc_id"] for c in chunks}
    assert len(docs) == 20
