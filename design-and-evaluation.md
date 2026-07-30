# Design and Evaluation

## Architecture

```
                 ingest time                              query time
docs/*.md --> split by ## headings --> word chunks    question --> Cohere embed (search_query)
                     |                                        |
             Cohere embed (search_document)             ChromaDB top-4 cosine search
                     |                                        |
             ChromaDB (local, persistent)          prompt = system rules + chunks + citations
                                                              |
                                                   OpenAI chat model --> answer + sources
```

## Design decisions and why

**No framework (no LangChain).** The pipeline is four small functions: embed, retrieve, prompt, call LLM. Writing it directly keeps the code readable, debuggable, and free of dependency churn. A framework would add abstraction without adding capability at this scale.

**Embeddings: Cohere `embed-english-v3.0`.** Free trial tier, strong retrieval quality, and an explicit `input_type` split (`search_document` vs `search_query`) which measurably improves retrieval versus symmetric embeddings. No local model download needed, which keeps deploys small.

**Vector store: ChromaDB (local, persistent).** The corpus is ~150 chunks, so a local store is the right size: zero cost, zero network hops on retrieval, and the index is just a folder (`chroma_db/`) that can be rebuilt in seconds. Cosine distance is configured explicitly (`hnsw:space: cosine`) to match how embedding similarity is normally measured.

**Chunking: by markdown heading, then 300-word windows with 50-word overlap.** Policies are naturally organized by `##` sections (one rule per section), so heading-based splitting keeps each chunk semantically whole — a chunk is "the carryover rule", not half of one rule and half of another. The word-window fallback only kicks in for long sections. The document title and heading are prepended to the text at embedding time so chunks carry their context.

**Retrieval: top k=4.** With ~150 focused chunks, the right chunk is almost always in the top 2; k=4 adds headroom for questions that span policies (e.g. per diem appears in both travel and expense policies) while keeping the prompt small and cheap.

**LLM: OpenAI `gpt-4o-mini` by default, via the Chat Completions API.** The project started on OpenRouter free-tier models, but two problems surfaced in practice: free model IDs rotate (an earlier Llama 3.3 free model was retired mid-project), and the free tier caps at 50 requests/day without credits — which a single eval run nearly exhausts. Switching to OpenAI trades "free" for reliable: `gpt-4o-mini` costs well under a cent per question, follows the citation format consistently, and has generous rate limits. The model stays configurable via the `OPENAI_MODEL` env var, and because the pipeline calls the API with plain `requests`, the swap touched one function.

**Prompt format.** The system prompt pins four rules: answer only from the provided excerpts, cite every fact with its doc id in square brackets (e.g. `[pto-policy]`), refuse with a fixed sentence when the excerpts don't contain the answer, and stay under 150 words. Each excerpt is labeled with its doc id, title, and section heading so the model can cite correctly.

**Guardrails.**
1. Distance gate: if the best retrieved chunk has cosine distance above 0.7, the app refuses without calling the LLM at all (saves a call, can't hallucinate).
2. Prompt-level refusal: the LLM is instructed to refuse when the excerpts don't answer the question.
3. Output length: `max_tokens=400` plus the 150-word instruction.
4. `temperature=0` for deterministic, conservative answers.

## Evaluation approach

The eval set (`eval/questions.json`) has 22 questions: 20 policy questions covering PTO, sick leave, remote work, expenses, travel, security, passwords, privacy, parental leave, equipment, reviews, conflicts of interest, procurement, and holidays — plus 2 deliberately off-topic questions to test the refusal guardrail.

`python eval/evaluate.py` runs every question through the live pipeline and reports:

- **Groundedness** (information quality, required): an LLM judge receives the retrieved excerpts, the question, and the answer, and checks that every claim in the answer is supported by the excerpts.
- **Citation accuracy** (information quality, required): the same judge checks that the doc ids cited in the answer are the documents that actually contain the supporting text.
- **Partial match** (optional): whether the answer contains the short gold answer (e.g. "20" for PTO days).
- **Refusal accuracy**: whether the two off-topic questions get the refusal response.
- **Latency p50/p95** (system metric, required): wall-clock time from request to answer across all 22 queries.

The run is deterministic: no sampling, fixed question order, temperature 0.

## Results

Full per-question results are in `eval/results.md`. Summary of the run on 2026-07-30 with `nvidia/nemotron-3-super-120b-a12b:free`:

| Metric | Value |
|---|---|
| Questions | 22 (20 policy + 2 off-topic) |
| Groundedness | 80.0% (see note) |
| Citation accuracy | 80.0% (see note) |
| Partial match vs gold | 95.0% (see note) |
| Refusal accuracy (off-topic) | 100.0% |
| Latency p50 | 3.25 s |
| Latency p95 | 8.47 s |

**Note on the 80% scores.** All four questions marked "not grounded" were judge-call failures, not answer failures: the OpenRouter free tier rate-limited or garbled the judge responses, and a failed judge scores conservatively as `grounded=false`. Inspecting those four answers in `eval/results.md` (receipt threshold, incident reporting window, home office stipend, holiday count) shows each one is correct, matches the gold answer, and cites the right document — so measured groundedness on successfully judged questions is 16/16 (100%). The single partial-match miss was also an artifact: the model emitted a non-breaking space inside "24 hours", defeating substring matching. Both artifacts are fixed (judge retries with backoff, unicode normalization before matching) for the next run.

**Free-tier constraint discovered during evaluation.** OpenRouter's free models allow 50 requests/day without credits; one full eval run (~40 LLM calls: 20 answers + 20 judge calls) nearly exhausts it. This is what motivated switching the LLM to OpenAI (see the LLM design decision above). The two off-topic questions cost zero LLM calls because the retrieval distance gate refuses before generation.
