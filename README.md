# Code Explainer

Streamlit + Claude chatbot for explaining Python code. Multi-turn conversation with few-shot and structured output patterns.

![Code Explainer demo screenshot](./assets/streamlit-chat-demo.png)

*Claude explaining a Python list comprehension line-by-line with a TL;DR summary.*

---

## Live demo

Base URL: [`https://app-chat-demo.streamlit.app/`](https://app-chat-demo.streamlit.app/)

> **Note on cold starts:** The free tier sleeps after 1 hour 
> of inactivity. First request after idle takes 30–60 seconds. 
> Subsequent requests respond in 2–6 seconds.

---

## What it does

- Multi-turn conversation with Claude with streaming responses
- Few-shot prompting for consistent formatting
- Structured output with TL;DR summaries
- Session state for conversation persistence
- Error handling for API failures with automatic history rollback

---

## How it works

**Session management:** Streamlit's `st.session_state` persists the conversation history across app reruns. Each user message appends to the history, which is sent to Claude in full on each request (capped at 20 turns to prevent cost runaway and context window overflow).

**Streaming responses:** The app uses `client.messages.stream()` with the Anthropic SDK instead of a blocking `create()` call. The full response is accumulated via `"".join(stream.text_stream)` and stored to session state only after the stream completes — ensuring conversation history always contains complete responses, not partial ones.

**Error handling:** API failures (network timeouts, rate limits) are caught and displayed as red banners in the UI, with conversation history rolled back to prevent orphaned user turns.

**System prompt design:** The app uses a code explainer persona — Claude is 
instructed to explain code line-by-line in plain English, with a TL;DR summary 
at the end. The persona was chosen because it naturally produces structured output 
(one explanation per line), makes few-shot examples easy to write, and is 
immediately recognizable as developer tooling to potential clients. The system 
prompt is defined as a module-level constant (`SYSTEM_PROMPT`) so it can be 
versioned and swapped without touching application logic.

---

## Implementation highlights

- Few-shot prompting added for consistent output format
- History capped at 20 turns to prevent cost runaway
- Streaming responses via `client.messages.stream()` — tokens arrive in ~300ms vs 3–8s blocking
- Guard against malformed history: strips leading assistant turns before sending to API
- Session state replay loop explains how Streamlit reruns work
- Structured output ensures line-by-line + TL;DR format

---

## Prompt patterns

**Few-shot prompting:** The system prompt includes two example input/output pairs 
that demonstrate the desired response format. Claude infers the pattern from these 
examples and applies it to new inputs — producing consistent formatting without 
relying on lengthy verbal instructions alone.

**Structured output:** A format constraint explicitly instructs Claude to always 
respond with: (1) the code line or expression, (2) an indented plain-English 
explanation, (3) a TL;DR summary at the end. This ensures responses are 
predictable regardless of input complexity.

**Why both together:** Few-shot examples show Claude what the output should look 
like. Structured output instructions tell Claude what it must include. Using both 
produces more consistent results than either pattern alone.

---

## Limitations

- History cap means conversations (20+ turns) will forget older context
- Code explanations are concise; very long snippets may be truncated
- Streamlit Community Cloud free tier sleeps after 1 hour inactivity
- Streaming complicates error handling mid-response — partial output may 
  briefly appear before an error banner replaces it

---

## Requirements

- Python 3.13+
- Git
- An Anthropic API key ([get one here](https://console.anthropic.com))

Dependencies are listed in `requirements.txt`. See [Tech stack](#tech-stack) below.

---

## Quick start

After setup, run:

    streamlit run src/app.py

Server starts at `http://localhost:8501/`

Paste this snippet to test immediately:

    squares = [x**2 for x in range(10) if x % 2 == 0]

Press Enter. Claude explains it line-by-line with a TL;DR.

---

## Local setup

**Clone and enter the project:**

    git clone https://github.com/digitalrower/streamlit-chat-demo.git
    (or)
    git clone git@github.com:digitalrower/streamlit-chat-demo.git

    cd streamlit-chat-demo

**Pin Python version (requires pyenv):**

    pyenv local 3.13.3
    python --version              # should show Python 3.13.3

**Create and activate a virtual environment:**

    python -m venv .venv
    source .venv/bin/activate     # Mac/Linux
    # Windows: .venv\Scripts\activate

**Install dependencies:**

    pip install -r requirements.txt

**Set up environment variables:**

    cp .env.example .env

Open `.env` and replace the placeholder with your actual Anthropic API key:

    ANTHROPIC_API_KEY=your_actual_api_key_here

---

## Project structure

    streamlit-chat-demo/
    ├── src/
    │   └── app.py           # Streamlit UI and LLM Call app
    ├── .env.example         # Environment variable template
    ├── .gitignore
    ├── requirements.txt
    └── README.md

---

## Tech stack

- [Streamlit](https://streamlit.io/) — User Interface
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) — Claude API client
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment variable management

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key from console.anthropic.com |

See `.env.example` for the template.

---

## License

MIT

