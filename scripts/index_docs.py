from app.config import get_settings
from app.rag.chunker import split_documents
from app.rag.loader import load_documents
from app.rag.vector_store import get_vector_store, index_documents

settings = get_settings()

documents = load_documents(settings.docs_dir)
chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
print(f"Documents: {len(documents)}, Chunks: {len(chunks)}")

vector_store = get_vector_store(settings)
indexed = index_documents(vector_store, chunks)
print(f"Indexed {indexed} chunks")
print(f"Total chunks in Chroma: {len(vector_store.get()['ids'])}")