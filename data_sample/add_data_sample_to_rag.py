from pathlib import Path

from backend.rag_components.rag import RAG


config_directory = Path("backend/config.yaml")
rag = RAG(config_directory)

data_sample_path = Path("data_sample/billionaires_csv.csv")
print(rag.load_file(data_sample_path))