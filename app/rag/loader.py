from pathlib import Path

from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def load_documents(docs_dir: str | Path) -> list[Document]:
    docs_path = Path(docs_dir)
    if not docs_path.is_dir():
        raise FileNotFoundError(f"Docs folder not found: {docs_path}")

    documents: list[Document] = []
    for file_path in sorted(docs_path.rglob("*")):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = file_path.read_text(encoding="utf-8")
        if not text.strip():
            continue

        documents.append(
            Document(page_content=text, metadata={"source": file_path.name})
        )

    return documents