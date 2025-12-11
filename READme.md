# Interview AI Coach - MVP

## Run locally
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Seed historical docs: `python seed_docs.py`
4. `python app.py` -> open http://localhost:7860

## Deploy on Hugging Face Spaces
1. Create a new Space (Gradio) and link to this repo.
2. Push code to GitHub main branch; the Space auto-deploys.

## Data format
- `data/feedback_docs/*.txt` : previous batch interview feedback
- `data/placement_history/*.csv` : placement history CSVs for analytics

## Handover
- To add new docs: drop `.txt` in `data/feedback_docs/` and run `python seed_docs.py`.
- To reindex: delete `saved_index/` and run seed script.
