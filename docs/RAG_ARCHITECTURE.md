
# DocMind — RAG Architecture

## 1. What is RAG?

RAG stands for Retrieval-Augmented Generation.

It is a technique that combines two processes:

1. **Retrieval:** Finds relevant information from uploaded documents.
2. **Generation:** Uses a Large Language Model (LLM) to generate an answer based on the retrieved information.

DocMind uses RAG to allow users to upload PDF documents and ask questions about their contents.

Instead of relying only on the LLM's general knowledge, DocMind retrieves relevant information from the uploaded documents and provides it to the LLM as context.

## 2. How RAG Works in DocMind

DocMind follows two main workflows:

### A. Document Ingestion

1. The user uploads PDF documents.
2. PyPDFLoader extracts text from the PDFs page by page.
3. CharacterTextSplitter divides the extracted text into smaller chunks.
4. Hugging Face Sentence Transformers converts the chunks into vector embeddings.
5. ChromaDB stores the embeddings, document text, and associated metadata.

### B. Question Answering

1. The user enters a question through the Streamlit interface.
2. The question is converted into an embedding using the same embedding model.
3. ChromaDB performs similarity search to retrieve the most relevant document chunks.
4. The retriever returns the top four matching chunks.
5. LangChain's RetrievalQA chain passes the retrieved context to the Groq-hosted LLM.
6. The LLM generates an answer using the retrieved context.
7. DocMind displays the answer and the retrieved source information.

## 3. Technologies Used

| Component | Technology | Purpose |
|---|---|---|
| User Interface | Streamlit | Provides the interactive chatbot |
| Orchestration | LangChain | Connects retrieval and generation |
| PDF Extraction | PyPDFLoader | Extracts PDF text |
| Text Splitting | CharacterTextSplitter | Divides text into chunks |
| Embeddings | Hugging Face Sentence Transformers | Converts text into vectors |
| Vector Database | ChromaDB | Stores and retrieves document vectors |
| LLM | Groq API | Generates natural-language answers |

## 4. RAG Workflow Summary

**PDF Upload → Text Extraction → Text Chunking → Embedding Generation → ChromaDB Storage → User Question → Similarity Search → Context Retrieval → LLM Generation → Answer with Sources**

## 5. Important Implementation Details

- Embedding model: `sentence-transformers/all-mpnet-base-v2`
- Chunk size: `2000`
- Chunk overlap: `500`
- Vector database: ChromaDB
- Retrieval method: Similarity search
- Number of retrieved chunks: `4`
- LLM: `openai/gpt-oss-120b`
- LLM temperature: `0.0`

## 6. Key Concept

RAG does not mean training a new language model on the uploaded PDFs.

Instead, it retrieves relevant information from the document collection at question time and supplies that information to the existing LLM as context.

This allows DocMind to answer questions using information from user-provided documents.
