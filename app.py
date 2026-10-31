
import streamlit as st
from pathlib import Path
import uuid
import chromadb

from src.config import (
    PROJECT_NAME,
    DOCS_DIR,
    VECTOR_DB_PATH,
    COLLECTION_NAME,
    validate_config
)

from src.ingestion import ingest_documents
from src.retrieval import create_retrieval_chain, ask_question


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DocMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #ffffff;
}

.main .block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

h1 {
    color: #30313d;
    font-size: 2.8rem !important;
    font-weight: 750 !important;
}

[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 1rem;
}

[data-testid="stChatInput"] {
    border-radius: 12px;
}

section[data-testid="stSidebar"] {
    background-color: #f7f8fa;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# KNOWLEDGE BASE STATUS
# --------------------------------------------------

def check_knowledge_base():

    """
    Check whether an existing ChromaDB collection
    contains indexed document chunks.
    """

    try:

        client = chromadb.PersistentClient(
            path=str(VECTOR_DB_PATH)
        )

        collection = client.get_collection(
            name=COLLECTION_NAME
        )

        return collection.count() > 0

    except Exception:

        return False


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "chats" not in st.session_state:

    chat_id = str(uuid.uuid4())

    st.session_state.chats = {
        chat_id: {
            "title": "New Chat",
            "messages": []
        }
    }

    st.session_state.active_chat_id = chat_id


if "active_chat_id" not in st.session_state:

    st.session_state.active_chat_id = next(
        iter(st.session_state.chats)
    )


if "qa_chain" not in st.session_state:

    st.session_state.qa_chain = None


if "documents_ready" not in st.session_state:

    st.session_state.documents_ready = (
        check_knowledge_base()
    )


# --------------------------------------------------
# CHAT MANAGEMENT FUNCTIONS
# --------------------------------------------------

def get_active_chat():

    return st.session_state.chats[
        st.session_state.active_chat_id
    ]


def create_new_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.active_chat_id = chat_id


def delete_chat(chat_id):

    if chat_id in st.session_state.chats:

        del st.session_state.chats[chat_id]

    if not st.session_state.chats:

        create_new_chat()

    elif chat_id == st.session_state.active_chat_id:

        st.session_state.active_chat_id = next(
            iter(st.session_state.chats)
        )


def generate_chat_title(question):

    title = question.strip().replace("\n", " ")

    if len(title) > 35:

        return title[:35].rstrip() + "..."

    return title


# --------------------------------------------------
# SOURCE DOCUMENT DISPLAY
# --------------------------------------------------

def display_sources(sources):

    if not sources:
        return

    with st.expander("📄 View source documents"):

        for index, source in enumerate(sources, start=1):

            st.markdown(f"**Source {index}**")

            # Extract source filename
            source_file = Path(
                source.metadata.get("source", "Unknown")
            ).name

            # Extract PDF page number
            page_number = source.metadata.get("page_label")

            if page_number is None:

                page_number = source.metadata.get("page")

                if isinstance(page_number, int):

                    page_number += 1

                elif isinstance(page_number, str):

                    if page_number.isdigit():

                        page_number = int(page_number) + 1

                    else:

                        page_number = "N/A"

            st.write("File:", source_file)

            st.write("Page:", page_number)

            # Display retrieved content
            content = source.page_content

            st.caption(
                content[:500] + "..."
                if len(content) > 500
                else content
            )

            st.divider()


# --------------------------------------------------
# RETRIEVAL INITIALIZATION
# --------------------------------------------------

def get_qa_chain():

    if st.session_state.qa_chain is None:

        validate_config()

        st.session_state.qa_chain = (
            create_retrieval_chain()
        )

    return st.session_state.qa_chain


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🧠 DocMind")

st.caption(
    "AI-Powered Document Intelligence | "
    "Chat with your documents. "
    "Upload PDFs, ask questions and discover insights."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    # ----------------------------------------------
    # CONVERSATION MANAGEMENT
    # ----------------------------------------------

    st.subheader("💬 Conversations")

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()

    # Display existing conversations

    for chat_id, chat in list(
        st.session_state.chats.items()
    ):

        col1, col2 = st.columns([5, 1])

        with col1:

            is_active = (
                chat_id == st.session_state.active_chat_id
            )

            button_label = (
                f"● {chat['title']}"
                if is_active
                else chat["title"]
            )

            if st.button(
                button_label,
                key=f"select_{chat_id}",
                use_container_width=True
            ):

                st.session_state.active_chat_id = chat_id

                st.rerun()

        with col2:

            if st.button(
                "🗑️",
                key=f"delete_{chat_id}"
            ):

                delete_chat(chat_id)

                st.rerun()

    st.divider()

    # ----------------------------------------------
    # DOCUMENT MANAGEMENT
    # ----------------------------------------------

    st.header("📚 DocMind Knowledge Base")

    st.write(
        "Upload PDF documents to create your knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button(
        "Process Documents",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning(
                "Please upload at least one PDF."
            )

        else:

            try:

                validate_config()

                # Save uploaded PDFs

                for uploaded_file in uploaded_files:

                    file_path = DOCS_DIR / Path(
                        uploaded_file.name
                    ).name

                    with open(file_path, "wb") as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )

                # Start ingestion process

                with st.spinner(
                    "Processing documents and generating embeddings..."
                ):

                    result = ingest_documents()

                    # Reset retrieval chain
                    st.session_state.qa_chain = None

                    # Update application status
                    st.session_state.documents_ready = True

                    # Start a fresh conversation
                    st.session_state.chats = {}

                    create_new_chat()

                st.success(
                    "Documents processed successfully!"
                )

                st.write(
                    f"**PDF files:** {result['total_files']}"
                )

                st.write(
                    f"**Pages loaded:** {result['total_pages']}"
                )

                st.write(
                    f"**Chunks created:** {result['total_chunks']}"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Document processing failed: {error}"
                )

    st.divider()

    # ----------------------------------------------
    # APPLICATION STATUS
    # ----------------------------------------------

    st.subheader("Application Status")

    if st.session_state.documents_ready:

        st.success(
            "Knowledge base ready"
        )

    else:

        st.info(
            "Upload and process documents to begin."
        )

    # ----------------------------------------------
    # CLEAR CURRENT CONVERSATION
    # ----------------------------------------------

    if st.button(
        "Clear Current Chat",
        use_container_width=True
    ):

        active_chat = get_active_chat()

        active_chat["messages"] = []

        active_chat["title"] = "New Chat"

        st.rerun()


# --------------------------------------------------
# DISPLAY ACTIVE CONVERSATION
# --------------------------------------------------

active_chat = get_active_chat()

for message in active_chat["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            display_sources(
                message["sources"]
            )


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask your documents anything..."
)


# --------------------------------------------------
# QUESTION PROCESSING
# --------------------------------------------------

if question:

    if not st.session_state.documents_ready:

        st.warning(
            "Please upload and process your PDF documents first."
        )

    else:

        active_chat = get_active_chat()

        # ------------------------------------------
        # USER MESSAGE
        # ------------------------------------------

        if active_chat["title"] == "New Chat":

            active_chat["title"] = generate_chat_title(
                question
            )

        active_chat["messages"].append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        # ------------------------------------------
        # ASSISTANT RESPONSE
        # ------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    qa_chain = get_qa_chain()

                    response = ask_question(
                        qa_chain,
                        question
                    )

                    answer = response["answer"]

                    sources = response["sources"]

                    st.markdown(answer)

                    display_sources(sources)

                    # Save response in current session

                    active_chat["messages"].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as error:

                    error_message = (
                        f"Unable to generate response: {error}"
                    )

                    st.error(error_message)

                    active_chat["messages"].append({
                        "role": "assistant",
                        "content": error_message
                    })
