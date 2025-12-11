# resume_matcher.py
import re
from sklearn.feature_extraction.text import CountVectorizer

def extract_keywords(text, top_n=40):
    # crude: split words, remove stopwords (keep it simple)
    text = text.lower()
    tokens = re.findall(r"\b[a-zA-Z\+\#\-\_]+\b", text)
    # filter tiny/common words (improve later)
    tokens = [t for t in tokens if len(t) > 2]
    # frequency
    from collections import Counter
    c = Counter(tokens)
    return [w for w,_ in c.most_common(top_n)]

def compare_resume_jd(resume_text, jd_text, top_n=30):
    jd_k = extract_keywords(jd_text, top_n=top_n)
    resume_k = extract_keywords(resume_text, top_n=top_n)
    missing = [k for k in jd_k if k not in resume_k]
    # also detect missing "impact metrics" — naive heuristic
    missing_metrics = "No numeric impact detected" if not re.search(r"\d+", resume_text) else ""
    return {"jd_keywords": jd_k, "resume_keywords": resume_k, "missing_keywords": missing, "missing_metrics": missing_metrics}
