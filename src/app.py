import streamlit as st 
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic import APIError, APIConnectionError, APITimeoutError

load_dotenv() # reads .env from current directory

client = Anthropic() # reads ANTHROPIC_API_KEY from env automatically

SYSTEM_PROMPT = """You are a code explainer. When the user pastes code,
explain it line by line in plain English. Be concise — no preamble,
no "Sure! Here's the explanation." Just the explanation itself.
If the input is not code, ask the user to paste a code snippet."""

# Keep the most recent N turns to prevent unbounded cost growth and
# context window overflow. 20 turns ≈ 10 user/assistant exchanges,
# which is plenty for a code explainer's typical session.
HISTORY_CAP = 20

def ask_claude(messages: list) -> str:
    """Send full conversation history to Claude, return assistant text.
    Raises APIError on Anthropic API failures - caller should handle. 
    """
    recent_messages = messages[-HISTORY_CAP:]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=recent_messages,
    )
    return response.content[0].text

# Streamlit UI
st.title("Code Explainer")
st.caption("Paste a code snippet, get a line-by-line explanation.")

# Initialize chat history once per session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay history on every rerun (Streamlit reruns on every interaction)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# React to user input
if user_input := st.chat_input("Paste your code here..."):
    # Display user turn immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Append user turn BEFORE calling Claude so it's included in history sent
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Send full conversation history (not just latest message)
        with st.spinner("Thinking..."):
            answer = ask_claude(st.session_state.messages) 
    except (APIError, APIConnectionError, APITimeoutError) as e:
        # Roll back the user message we just appended — we don't want a
        # user turn in history with no corresponding assistant response,
        # because the next API call would send incomplete pairs.
        st.error(f"Couldn't reach Claude: {e}")
        st.session_state.messages.pop()
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.session_state.messages.pop()
        st.stop()

    # Display assistant turn
    with st.chat_message("assistant"):
        st.write(answer)

    # Append assistant turn to history for next rerun
    st.session_state.messages.append({"role": "assistant", "content": answer })