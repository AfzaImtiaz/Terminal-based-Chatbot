# Multi-Turn CLI Chatbot with Memory

Terminal chatbot powered by Gemini with sliding-window memory and live cost tracking.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your Gemini API key to .env
```

## Run

```bash
python -m chatbot.cli
```

Optional flags:
```bash
python -m chatbot.cli --system "You are a Python tutor." --max-tokens 2000
```

## Commands inside the chat

| Command | What it does |
|---|---|
| `/cost` | Show total tokens used and USD spent |
| `/save` | Save conversation to `conversation.json` |
| `/save myfile.json` | Save to a custom file |
| `/load myfile.json` | Load a previous conversation |
| `/quit` | Exit |

## How the sliding window works

Once the conversation exceeds `--max-tokens` (default 3000), the oldest
messages are dropped automatically so the bot always stays under budget.
Try `--max-tokens 200` and watch it forget early messages — that's it working.
