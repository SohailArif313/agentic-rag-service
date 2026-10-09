from langchain_chroma import Chroma

from app.config import Settings
from app.rag.chunker import split_documents
from app.rag.loader import load_documents
from app.rag.vector_store import index_documents


def index_docs_folder(settings: Settings, vector_store: Chroma) -> int:
    documents = load_documents(settings.docs_dir)
    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    return index_documents(vector_store, chunks)


def is_index_empty(vector_store: Chroma) -> bool:
    return len(vector_store.get(limit=1)["ids"]) == 0