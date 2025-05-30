import logging
from langchain import hub
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from vectorstore import init_vectorstore

logger = logging.getLogger(__name__)

prompt = hub.pull("rlm/rag-prompt")
llm = init_chat_model(model="gpt-4o-mini", model_provider="openai")
vector_store = init_vectorstore(collection_name="blog_agents")


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""

    retrieved_docs = vector_store.similarity_search(query, k=2)

    serialized = "\n\n".join(
        f"Source: {doc.metadata}\n Content: {doc.page_content}"
        for doc in retrieved_docs)

    return serialized, retrieved_docs


def query_or_respond(state: MessagesState):
    """Generate tool-call for retrieval or respond."""

    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])

    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


def generate(state: MessagesState):
    """ Generate answer using the retrieved content"""

    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )

    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system") or (
                message.type == "ai" and not message.tool_calls)
    ]

    input_messages = [SystemMessage(system_message_content)] + conversation_messages

    response = llm.invoke(input_messages)

    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


def build_graph(**kwargs):
    """ Build graph """

    logger.info("Building graph")

    tools = ToolNode([retrieve])

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        source="query_or_respond",
        path=tools_condition,
        path_map={END: END, "tools": "tools"})

    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile(**kwargs)

    return graph


def ex_01():
    """ ... """

    graph = build_graph()

    input_message = "Hello"
    output = graph.invoke(input={"messages": [{"role": "user", "content": input_message}]})

    for m in output['messages']:
        m.pretty_print()
    # ================================ Human Message =================================
    #
    # Hello
    # ================================== Ai Message ==================================
    #
    # Hello! How can I assist you today?

    input_message = "What is Task Decomposition?"
    output = graph.invoke(input={"messages": [{"role": "user", "content": input_message}]})

    for m in output['messages']:
        m.pretty_print()


def ex_02():
    """ Persist the chat history """

    memory = MemorySaver()
    graph = build_graph(checkpointer=memory)

    # Specify an ID for the thread
    config = {"configurable": {"thread_id": "abc123"}}

    input_message = "What is Task Decomposition?"
    output = graph.invoke(
        input={"messages": [{"role": "user", "content": input_message}]},
        config=config)

    for m in output['messages']:
        m.pretty_print()

    # Note that the query generated by the model in the second question
    # incorporates the conversational context.
    input_message = "Can you look up some common ways of doing it?"
    output = graph.invoke(
        input={"messages": [{"role": "user", "content": input_message}]},
        config=config)

    for m in output['messages']:
        m.pretty_print()
