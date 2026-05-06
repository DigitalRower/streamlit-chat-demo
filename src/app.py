import streamlit as st 
from dotenv import load_dotenv
from anthropic import Anthropic, APIError

load_dotenv() # reads .env from current directory

client = Anthropic() # reads ANTHROPIC_API_KEY from env automatically

SYSTEM_PROMPT = """You are a code explainer. When the user pastes code,
explain it line by line in plain English. Be concise — no preamble,
no "Sure! Here's the explanation." Just the explanation itself.
If the input is not code, ask the user to paste a code snippet."""

def _ask_claude(messages: list) -> str:
    """Send full conversation history to Claude, return assistant text."""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return response.content[0].text
    except APIError as e:
        return f"API error: {e}"

# Streamlit UI
st.title("Code Explainer")
st.caption("Past a code snippet, get a line-by-line explanation.")

# Initalize chat history once per session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay history on every rerun (Streamlit reruns on every interaction)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# React to user input
if user_input := st.chat_input("Past your code here..."):
    # Display user turn immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Append user turn BEFORE calling Claude so it's included in history sent
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send full conversation history (not just latest message)
    answer = _ask_claude(st.session_state.messages) 

    # Display assistant turn
    with st.chat_message("assistant"):
        st.write(answer)

    # Append assistant turn to history for next rerun
    st.session_state.messages.append({"role": "assistant", "content": answer })