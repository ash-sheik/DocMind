
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader
)

from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import chromadb

from src.config import (
    DOCS_DIR,
    VECTOR_DB_PATH,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL
)


# --------------------------------------------------
# DOCUMENT INGESTION
# --------------------------------------------------

def ingest_documents():
    """
    Load PDF documents, split their text into chunks,
    generate embeddings and store them in ChromaDB.
    """

    # Step 1: Find PDF files
    pdf_files = list(DOCS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(
            "No PDF documents found in docs_dir."
        )

    print(f"Found {len(pdf_files)} PDF document(s).")

    # Step 2: Load PDF documents
    loader = DirectoryLoader(
        path=str(DOCS_DIR),
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()

    if not documents:
        raise ValueError(
            "No readable PDF pages found."
        )

    print(f"Total pages loaded: {len(documents)}")

    # Step 3: Initialize text splitter
    text_splitter = CharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # Step 4: Split documents into chunks
    text_chunks = text_splitter.split_documents(documents)

    if not text_chunks:
        raise ValueError(
            "No text chunks were generated from the PDFs."
        )

    print(f"Total chunks created: {len(text_chunks)}")

    # Step 5: Generate embeddings
    embedding = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # Step 6: Initialize ChromaDB
    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH)
    )

    # Delete the previous collection before rebuilding
    # This prevents duplicate document chunks.
    try:
        client.delete_collection(
            name=COLLECTION_NAME
        )
        print("Previous collection removed.")
    except Exception:
        print("No previous collection found. Creating a new one.")

    # Step 7: Store documents in ChromaDB
    vector_store = Chroma.from_documents(
        documents=text_chunks,
        embedding=embedding,
        persist_directory=str(VECTOR_DB_PATH),
        collection_name=COLLECTION_NAME
    )

    print("Documents successfully stored in ChromaDB!")

    # Step 8: Return ingestion statistics
    return {
        "total_files": len(pdf_files),
        "total_pages": len(documents),
        "total_chunks": len(text_chunks),
        "vector_store": vector_store
    }
