"""
    Test with `streamlit run src/app.py`
"""

import streamlit as st
from rag import build_graph

# TODO: check how many times we rerun this part of the code
# TODO: for now, we will just record the messages but won't pass them to the model
graph = build_graph()


def run():
    st.title("LLM RAG")

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
            output = graph.invoke(
                input={"messages": [{"role": "user", "content": prompt}]})
            output_message = output["messages"][-1].content
            st.markdown(output_message)

        st.session_state.messages.append({"role": "assistant", "content": output_message})


if __name__ == "__main__":
    run()
