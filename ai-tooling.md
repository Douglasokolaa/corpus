# AI Tooling

## What was used

**Claude Code (Anthropic's CLI coding agent, Fable 5 model)** was used to build this project end to end:

- Scaffolded the whole application from the project brief: Flask app, RAG pipeline (`rag.py`), ingestion script (`ingest.py`), chat UI, tests, and the GitHub Actions workflow.
- Generated the 20-document synthetic policy corpus in `docs/`, with deliberately consistent, concrete facts (day counts, dollar limits, deadlines) so evaluation questions have unambiguous gold answers.
- Wrote the evaluation harness (`eval/evaluate.py`), including the LLM-as-judge prompts for groundedness and citation accuracy, and the 22-question eval set.
- Drafted the documentation (README, this file, design-and-evaluation.md).

## What worked well

- Generating the corpus and the eval set together, so every eval question has a single clearly-supported answer in exactly one policy section. Doing this by hand would have taken longer than writing the app.
- Keeping the pipeline framework-free was easier with AI assistance: the generated code is four small functions instead of a LangChain dependency tree, so it was easy to review and understand every line.
- Test-first CI: the agent wrote tests that run without API keys, so CI passes without secrets.

## What didn't work / needed human judgment

- Free-tier model choice: the project started on OpenRouter free models, but their IDs rotate and the 50 requests/day cap made evaluation impractical, so the LLM was switched to OpenAI `gpt-4o-mini` (kept configurable via the `OPENAI_MODEL` env var). Discovering that constraint required actually running the eval — the model couldn't have predicted it.
- The retrieval distance threshold for the refusal guardrail (0.7 cosine distance) is a judgment call that needs validation against the live eval run rather than something the model can derive.
- API keys and the live evaluation run have to be done by a human, since the keys are personal.
