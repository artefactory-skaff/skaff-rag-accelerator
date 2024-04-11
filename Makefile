ingest_rag:
	poetry run python -m backend.ingest

serve_backend:
	poetry run python -m uvicorn backend.main:app

serve_frontend:
	poetry run python -m streamlit run frontend/front.py