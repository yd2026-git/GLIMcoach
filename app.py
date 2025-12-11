# app.py
import gradio as gr
import json, os, uuid, time
from rag import RAGIndex
from scorer import generate_structured_feedback
from resume_matcher import compare_resume_jd

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# load question bank
with open("data/questions.json", "r", encoding="utf-8") as f:
    QUESTION_BANK = json.load(f)

rag = RAGIndex(index_dir="saved_index")

def list_roles():
    roles = sorted({q["role"] for q in QUESTION_BANK})
    return roles

def pick_question(role, skill_tag):
    # basic: pick random question for the role and skill
    import random
    pool = [q for q in QUESTION_BANK if q["role"]==role and (skill_tag=="Any" or q["tag"]==skill_tag)]
    return random.choice(pool)["text"] if pool else "No question found for this role/tag."

def submit_answer(user_email, role, jd_name, question, answer_text):
    # 1) store transcript
    ts = {"id": str(uuid.uuid4()), "user": user_email, "role": role, "jd": jd_name, "question": question, "answer": answer_text, "time": time.time()}
    os.makedirs("data/transcripts", exist_ok=True)
    with open(f"data/transcripts/{ts['id']}.json", "w", encoding="utf-8") as f:
        json.dump(ts, f, indent=2)
    # 2) RAG retrieve relevant docs from previous feedback
    # if rag.index is empty, skip gracefully
    top_docs = rag.query(answer_text, top_k=5) if rag.index is not None else []
    # 3) scoring + LLM feedback
    feedback = generate_structured_feedback(question, answer_text, top_docs)
    # 4) compute scores (toy)
    clarity = 0.6 if len(answer_text.split())<120 else 0.4
    relevance = 0.8 if "?" not in answer_text else 0.5
    confidence = 0.7  # heuristics placeholder
    # 5) save a small history entry
    hist_dir = "data/history"
    os.makedirs(hist_dir, exist_ok=True)
    with open(f"{hist_dir}/{ts['id']}_meta.json", "w", encoding="utf-8") as f:
        json.dump({"clarity": clarity, "relevance": relevance, "confidence": confidence, "feedback": feedback}, f, indent=2)
    return feedback["llm_feedback"], {"clarity": clarity, "relevance": relevance, "confidence": confidence}

def resume_match_api(resume_text, jd_text):
    return compare_resume_jd(resume_text, jd_text)

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# Campus Interview Coach - MVP")
    with gr.Row():
        user_email = gr.Textbox(label="Your email (for history download)", value="")
        role_select = gr.Dropdown(label="Role", choices=list_roles())
        jd_name = gr.Textbox(label="JD name (paste text identifier)", value="default_jd")
    with gr.Row():
        skill_tag = gr.Dropdown(label="Skill tag", choices=["Any","behavioral","product","tech","estimation"], value="Any")
        ask_btn = gr.Button("Get question")
    question_display = gr.Textbox(label="Question", interactive=False)
    ask_btn.click(lambda r, s: pick_question(r, s), inputs=[role_select, skill_tag], outputs=[question_display])

    answer_input = gr.Textbox(label="Type your answer here (text only for MVP)", lines=6)
    submit_btn = gr.Button("Submit answer")
    feedback_out = gr.Textbox(label="Coach feedback")
    scores_out = gr.JSON(label="Scores (clarity, relevance, confidence)")
    submit_btn.click(submit_answer, inputs=[user_email, role_select, jd_name, question_display, answer_input], outputs=[feedback_out, scores_out])

    gr.Markdown("## Resume to JD quick match")
    resume_input = gr.Textbox(label="Paste resume text", lines=12)
    jd_input = gr.Textbox(label="Paste JD text", lines=12)
    match_btn = gr.Button("Compare")
    match_out = gr.JSON(label="Match result")
    match_btn.click(resume_match_api, inputs=[resume_input, jd_input], outputs=[match_out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

