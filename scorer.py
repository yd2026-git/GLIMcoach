# scorer.py
import re
from transformers import pipeline

# use a transformer text generation model (Flan-T5)
LLM_MODEL = "google/flan-t5-base"  # CPU friendly for Spaces (use flan-t5-large if you want more quality)
generator = pipeline("text2text-generation", model=LLM_MODEL, max_length=256)

def detect_rambling(answer_text, threshold_words=120):
    words = len(answer_text.split())
    return words > threshold_words, words

def detect_missing_metrics(answer_text):
    # simple heuristic: look for % or numbers or "x times"
    if re.search(r"\b\d+%|\b\d+\b", answer_text):
        return False
    return True

def detect_star(answer_text):
    # look for Situation/Task/Action/Result keywords
    keywords = ["situation", "task", "action", "result", "context", "challenge", "impact"]
    found = sum(1 for k in keywords if k in answer_text.lower())
    return found >= 2

def generate_structured_feedback(q, answer, top_docs=[]):
    heuristics = []
    rambling, wcount = detect_rambling(answer)
    if rambling:
        heuristics.append(f"Answer is long ({wcount} words) and may be rambling — aim for more concise structure.")
    if detect_missing_metrics(answer):
        heuristics.append("No numeric impact/metrics found — add measurable outcomes if possible.")
    if not detect_star(answer):
        heuristics.append("STAR structure not evident — add Situation, Action and measurable Result.")

    # Use LLM to convert heuristics + context to a friendly summary + 3 improvement steps
    context = "\n".join([f"- {d['doc']['text'][:300]}" for d in top_docs])
    prompt = f"""You are an encouraging interview coach. Question: {q}\nCandidate answer: {answer}\nContext snippets:\n{context}\n\nHeuristics:\n{chr(10).join(heuristics)}\n\nProvide:
1) A 2-sentence summary (strengths)
2) 2-3 weaknesses (one-liners)
3) Three practical things to work on before next attempt.
Respond clearly and politely."""
    out = generator(prompt)[0]["generated_text"]
    return {"heuristics": heuristics, "llm_feedback": out}
