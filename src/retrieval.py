
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA

from src.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    TEMPERATURE,
    VECTOR_DB_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)


# --------------------------------------------------
# RETRIEVAL CHAIN INITIALIZATION
# --------------------------------------------------

def create_retrieval_chain():
    """
    Load the existing ChromaDB vector store,
    initialize the Groq language model,
    and create a RetrievalQA chain.
    """

    # Step 1: Initialize Hugging Face embeddings
    embedding = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # Step 2: Connect to the existing ChromaDB
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding,
        persist_directory=str(VECTOR_DB_PATH)
    )

    # Step 3: Create the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Step 4: Initialize Groq LLM
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        api_key=GROQ_API_KEY
    )

    # Step 5: Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


# --------------------------------------------------
# QUESTION ANSWERING
# --------------------------------------------------

def ask_question(qa_chain, question):
    """
    Accept a user question and return:
    1. Generated answer
    2. Retrieved source documents
    """

    # Validate user input
    if not question or not question.strip():
        raise ValueError(
            "Please enter a question."
        )

    # Execute the retrieval and question-answering chain
    response = qa_chain.invoke({
        "query": question.strip()
    })

    # Return answer and source documents
    return {
        "answer": response["result"],
        "sources": response["source_documents"]
    }
