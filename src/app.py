import os
import uuid
import logging

import streamlit as st
from rag import build_graph
from langgraph.checkpoint.postgres import PostgresSaver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

POSTGRES_CONN_STRING = os.environ['POSTGRES_CONN_STRING']


def initialize_session_state():
    """Initialize Streamlit session state variables."""

    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = uuid.uuid4()
        logger.info(f"Created new thread: {st.session_state['thread_id']}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    """Display existing chat messages."""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(prompt: str, postgres_conn: str) -> str | None:
    """Process user input and return assistant response."""
    try:
        with PostgresSaver.from_conn_string(postgres_conn) as checkpointer:
            graph = build_graph(checkpointer=checkpointer)

            output = graph.invoke(
                input={"messages": [{"role": "user", "content": prompt}]},
                config={"configurable": {"thread_id": st.session_state["thread_id"]}}
            )

            if not output or "messages" not in output or not output["messages"]:
                st.error("❌ No response generated")
                return None

            response_content = output["messages"][-1].content
            logger.info(f"Generated response for thread {st.session_state['thread_id']}")
            return response_content

    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        st.error(f"❌ An error occurred: {str(e)}")
        return None


def run():
    st.title("LLM RAG")

    initialize_session_state()

    display_chat_history()

    # Accept user input
    if prompt := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response = process_user_input(prompt, POSTGRES_CONN_STRING)

            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("❌ Failed to generate response.")


if __name__ == "__main__":
    run()
