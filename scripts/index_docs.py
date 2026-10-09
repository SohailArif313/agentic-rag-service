from app.config import get_settings
from app.rag.indexing import index_docs_folder
from app.rag.vector_store import get_vector_store

settings = get_settings()
vector_store = get_vector_store(settings)

indexed = index_docs_folder(settings, vector_store)
print(f"Indexed {indexed} chunks")
print(f"Total chunks in Chroma: {len(vector_store.get()['ids'])}")