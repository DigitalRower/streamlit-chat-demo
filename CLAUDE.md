# streamlit-chat-demo

## Project purpose
Portfolio project. Streamlit chat app using Anthropic Claude API.
Code explainer use case — takes a code snippet and explains it line by line.

## Stack
- Python 3.13.3
- Streamlit
- Anthropic SDK (claude-haiku-4-5-20251001)
- Deployed on Streamlit Community Cloud

## Key files
- src/app.py — main Streamlit app
- .env / secrets — ANTHROPIC_API_KEY (never commit)
- requirements.txt

## Conventions
- API key via python-dotenv (.env locally) or Streamlit secrets (deployed)
- Conversation history in st.session_state
- Error handling wraps all Anthropic API calls

## Do not
- Commit .env or any file containing the API key
- Modify requirements.txt without noting the change