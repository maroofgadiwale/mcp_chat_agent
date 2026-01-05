# Program to implement MCP chatbot:
import asyncio
import json
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    ToolMessage,
    HumanMessage,
    AIMessage,
)

# ---------------- ENV ----------------
load_dotenv()

# ---------------- MCP SERVERS ----------------
SERVERS = {
    "Demo": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "python",
            "C:/Users/shifa/OneDrive/Desktop/mcp-server-demo/main.py",
        ],
    },
    "twitter-mcp": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@enescinar/twitter-mcp"],
        "env": {
            "API_KEY": os.environ.get("API_KEY"),
            "API_SECRET_KEY": os.environ.get("API_SECRET_KEY"),
            "ACCESS_TOKEN": os.environ.get("ACCESS_TOKEN"),
            "ACCESS_TOKEN_SECRET": os.environ.get("ACCESS_TOKEN_SECRET"),
        },
    },
}

# ---------------- STREAMLIT CONFIG ----------------
st.set_page_config(
    page_title="MCP Chatbot",
    page_icon="🧰",
    layout="centered",
)

st.title("🧰 MCP AI Chatbot")
st.caption("maroofgadiwale")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = None
    st.session_state.tools = None
    st.session_state.named_tools = None

# ---------------- INIT MCP ----------------
async def init_mcp():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    return client, tools, named_tools

# ---------------- LLM ----------------
def get_llm(tools):
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )
    return llm.bind_tools(tools, tool_choice="auto")

SYSTEM_PROMPT = SystemMessage(
    content="""
You are an assistant with access only to the provided tools.
If a question can be answered without tools, answer directly.
Never invent tools.
If no final response, return Success!
"""
)

# ---------------- ASYNC CHAT HANDLER ----------------
async def process_chat(user_input):
    # Init MCP once
    if st.session_state.client is None:
        client, tools, named_tools = await init_mcp()
        st.session_state.client = client
        st.session_state.tools = tools
        st.session_state.named_tools = named_tools

    llm = get_llm(st.session_state.tools)

    messages = [SYSTEM_PROMPT]

    # Add history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_input))

    # First LLM call
    response = await llm.ainvoke(messages)

    # If no tool call
    if not getattr(response, "tool_calls", None):
        return response.content

    # Execute tools
    tool_messages = []
    for tc in response.tool_calls:
        tool = st.session_state.named_tools[tc["name"]]
        result = await tool.ainvoke(tc.get("args") or {})
        tool_messages.append(
            ToolMessage(
                tool_call_id=tc["id"],
                content=json.dumps(result),
            )
        )

    # Final LLM call
    final_messages = messages + [response] + tool_messages
    final_response = await llm.ainvoke(final_messages)

    return final_response.content

# ---------------- CHAT UI ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    # User bubble
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant bubble
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = asyncio.run(process_chat(user_input))
            st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
