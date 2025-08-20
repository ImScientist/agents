import uuid
import streamlit as st
from rag import build_graph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgres://postgres:pwd@localhost:5432/postgres"


@st.cache_resource
def build_graph_with_inmemory_checkpointer():
    checkpointer = InMemorySaver()
    return build_graph(checkpointer=checkpointer)

# TODO: initialize this graph only if a particular condition is met
graph_inmemory = build_graph_with_inmemory_checkpointer()


def run():
    st.title("LLM RAG")

    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = uuid.uuid4()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Insert your question here"):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
                graph = build_graph(checkpointer=checkpointer)
                output = graph.invoke(
                    input={"messages": [{"role": "user", "content": prompt}]},
                    config={"configurable": {"thread_id": st.session_state["thread_id"]}}
                )

            # removed
            # output = graph.invoke(
            #     input={"messages": [{"role": "user", "content": prompt}]},
            #     config={"configurable": {"thread_id": st.session_state["thread_id"]}}
            # )
            output_message = output["messages"][-1].content
            st.markdown(output_message)

        st.session_state.messages.append({"role": "assistant", "content": output_message})


if __name__ == "__main__":
    run()
