import json
import re
import statistics
import sys
import time

sys.path.insert(0, ".")

from dotenv import load_dotenv

load_dotenv()

import rag

JUDGE_PROMPT = """You are grading a RAG system for a company policy assistant.
Given policy excerpts, a question, and the system's answer, reply with JSON only, no other text:
{"grounded": true or false, "citations_correct": true or false}
grounded = every factual claim in the answer is supported by the excerpts, with nothing invented or contradicted.
citations_correct = the doc ids cited in square brackets in the answer are the documents that actually contain the supporting text."""


def judge(question, context, answer_text):
    messages = [
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": "Excerpts:\n" + context + "\n\nQuestion: " + question + "\n\nAnswer: " + answer_text},
    ]
    for attempt in range(3):
        try:
            reply = rag.call_llm(messages)
            match = re.search(r"\{.*\}", reply, re.DOTALL)
            return json.loads(match.group(0))
        except Exception as e:
            print("judge attempt", attempt + 1, "failed:", e)
            time.sleep(10)
    return {}


def normalize(text):
    return text.lower().replace(" ", " ").replace("‑", "-").replace("’", "'")


def main():
    with open("eval/questions.json", encoding="utf-8") as f:
        questions = json.load(f)
    rows = []
    latencies = []
    for q in questions:
        start = time.time()
        result = rag.answer(q["question"])
        latency = time.time() - start
        latencies.append(latency)
        answer_text = result["answer"]
        row = {"question": q["question"], "answer": answer_text, "latency": round(latency, 2)}
        if q.get("expect_refusal"):
            row["refusal_ok"] = "i can only answer" in answer_text.lower()
        else:
            row["match"] = any(g.lower() in normalize(answer_text) for g in q["gold"])
            chunks = rag.retrieve(q["question"])
            context = "\n\n".join("[" + c["doc_id"] + "] " + c["text"] for c in chunks)
            verdict = judge(q["question"], context, answer_text)
            row["grounded"] = bool(verdict.get("grounded", False))
            row["citations_correct"] = bool(verdict.get("citations_correct", False))
        rows.append(row)
        print(q["question"], "->", row["latency"], "s")
        time.sleep(2)

    answered = [r for r in rows if "grounded" in r]
    refusals = [r for r in rows if "refusal_ok" in r]
    lat_sorted = sorted(latencies)
    p50 = statistics.median(lat_sorted)
    p95 = lat_sorted[max(0, round(0.95 * (len(lat_sorted) - 1)))]

    summary = {
        "questions": len(rows),
        "groundedness": round(100 * sum(r["grounded"] for r in answered) / len(answered), 1),
        "citation_accuracy": round(100 * sum(r["citations_correct"] for r in answered) / len(answered), 1),
        "partial_match": round(100 * sum(r["match"] for r in answered) / len(answered), 1),
        "refusal_accuracy": round(100 * sum(r["refusal_ok"] for r in refusals) / len(refusals), 1) if refusals else None,
        "latency_p50_s": round(p50, 2),
        "latency_p95_s": round(p95, 2),
    }
    print(json.dumps(summary, indent=2))

    lines = []
    lines.append("# Evaluation Results")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append("| Questions | " + str(summary["questions"]) + " |")
    lines.append("| Groundedness | " + str(summary["groundedness"]) + "% |")
    lines.append("| Citation accuracy | " + str(summary["citation_accuracy"]) + "% |")
    lines.append("| Partial match vs gold | " + str(summary["partial_match"]) + "% |")
    lines.append("| Refusal accuracy (off-topic) | " + str(summary["refusal_accuracy"]) + "% |")
    lines.append("| Latency p50 | " + str(summary["latency_p50_s"]) + " s |")
    lines.append("| Latency p95 | " + str(summary["latency_p95_s"]) + " s |")
    lines.append("")
    lines.append("## Per-question results")
    lines.append("")
    lines.append("| Question | Latency (s) | Grounded | Citations OK | Match | Answer |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        if "refusal_ok" in r:
            grounded = "-"
            cit = "-"
            match = "refusal " + ("OK" if r["refusal_ok"] else "FAIL")
        else:
            grounded = "yes" if r["grounded"] else "no"
            cit = "yes" if r["citations_correct"] else "no"
            match = "yes" if r["match"] else "no"
        answer_short = r["answer"].replace("\n", " ").replace("|", "/")[:120]
        lines.append("| " + r["question"] + " | " + str(r["latency"]) + " | " + grounded + " | " + cit + " | " + match + " | " + answer_short + " |")
    with open("eval/results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote eval/results.md")


if __name__ == "__main__":
    main()
