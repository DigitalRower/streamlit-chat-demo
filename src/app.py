import streamlit as st 
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic import APIError, APIConnectionError, APITimeoutError

load_dotenv() # reads .env from current directory

client = Anthropic() # reads ANTHROPIC_API_KEY from env automatically

SYSTEM_PROMPT = """You are a code explainer. When the user pastes code,
explain it line by line in plain English. Be concise — no preamble,
no "Sure! Here's the explanation." Just the explanation itself.
If the input is not code, ask the user to paste a code snippet.

Always structure your response exactly as follows:
1. The code line or expression
2. Indented explanation of what it does
3. TL;DR: one sentence summary at the end

Here are examples of how to respond:

User: `x = 5`
Assistant:
x = 5

  Assigns the integer 5 to a variable named x.
  After this runs: x holds the value 5.

TL;DR: Stores the number 5 in a variable.

User: `print("hello")`
Assistant:
print("hello")

  Calls Python's built-in print function with the string "hello".
  After this runs: the text hello appears in the terminal.

TL;DR: Prints the word hello to the screen.
"""

# Keep the most recent N turns to prevent unbounded cost growth and
# context window overflow. 20 turns ≈ 10 user/assistant exchanges,
# which is plenty for a code explainer's typical session.
HISTORY_CAP = 20

def ask_claude(messages: list) -> str:
    """Send full conversation history to Claude, return assistant text.
    Raises APIError on Anthropic API failures - caller should handle. 
    """
    recent_messages = messages[-HISTORY_CAP:]

    full_response = ""
    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=recent_messages,
    ) as stream:
        # stream.text_stream yields text deltas; join them into full response
        return "".join(stream.text_stream)

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