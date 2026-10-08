import sys

from app.config import get_settings
from app.rag.vector_store import get_vector_store, search

query = " ".join(sys.argv[1:])
if not query:
    raise SystemExit('Usage: uv run python -m scripts.search_docs "your question"')

settings = get_settings()
vector_store = get_vector_store(settings)

results = search(vector_store, query, k=3)
for rank, doc in enumerate(results, start=1):
    print(f"#{rank} [{doc.metadata['source']}]")
    print(doc.page_content)
    print("-" * 40)