import streamlit as st
import os
import sys

from src.sales_agent.gemini_agent import send_message
# from src.sales_agent.sales_agent_orchestrator import get_sales_agent_response_from_agent

# parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
# # Add the parent directory to the Python path
# sys.path.insert(0, parent_dir)
# print("parent_dir: ", parent_dir)

st.title("Second Drive Sales Chatbot")

# Initialize rag history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display rag messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input(""):
    # Add user message to rag history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in rag message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in rag message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = send_message(prompt)
        message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})