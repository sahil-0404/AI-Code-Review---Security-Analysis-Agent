from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.documents import SEED_DOCUMENTS
from rag.vectordb import get_collection

KB_PATH = Path("knowledge_base")


def ingest_pdfs():
    collection = get_collection()
    existing_sources = {
    meta.get("source")
    for meta in collection.get(include=["metadatas"])["metadatas"]
}

    pdfs = list(KB_PATH.rglob("*.pdf"))

    if not pdfs:
        print("No PDFs found. Using seed documents.")

        ids = []
        docs = []
        metas = []

        for i, item in enumerate(SEED_DOCUMENTS):
            ids.append(f"seed-{i}")
            docs.append(item["text"])
            metas.append(
                {
                    "title": item["title"],
                    "category": item["category"],
                    "source": "seed"
                }
            )

        collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas
        )

        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    index = 0

    for pdf in pdfs:
        if pdf.name in existing_sources:
            print(f"Skipping {pdf.name} (already indexed)")
            continue

        loader = PyPDFLoader(str(pdf))

        pages = loader.load()

        chunks = splitter.split_documents(pages)

        ids = []
        docs = []
        metas = []

        for chunk in chunks:

            ids.append(f"pdf-{index}")

            docs.append(chunk.page_content)

            metas.append(
                {
                    "title": pdf.stem,
                    "category": pdf.parent.name,
                    "source": pdf.name
                }
            )

            index += 1

        collection.add(
            ids=ids,
            documents=docs,
            metadatas=metas
        )


if __name__ == "__main__":
    ingest_pdfs()
    print("Knowledge Base Created Successfully")