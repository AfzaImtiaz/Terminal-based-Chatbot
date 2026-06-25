# Terminal-based-Chatbot
# Terminal LLM Chatbot

A lightweight, terminal-based chatbot powered by Google's Gemini API. It keeps a sliding-window memory of your conversation, tracks token usage and cost in real time, supports custom personas, and includes handy in-chat commands like clearing history and saving/loading conversations.

Built as part of an LLM Bootcamp project — designed to be simple to run, easy to extend, and resilient to the occasional API hiccup.

---

## Features

- **Conversational memory** — keeps track of the chat history with a sliding token-window so old messages get trimmed automatically once a limit is hit.
- **Custom personas** — launch the bot as a specific kind of assistant (e.g. a Python tutor, a writing coach) using a single flag.
- **Color-coded chat** — your messages and the bot's replies are color-coded in the terminal for easy reading.
- **`/clear` command** — wipe the conversation and start fresh without restarting the program.
- **Save & load conversations** — export your chat history to a JSON file and reload it later.
- **Live cost tracking** — see token usage and estimated cost after every message.
- **Automatic retries** — if Gemini's servers are temporarily overloaded (503) or rate-limited (429), the bot automatically retries with backoff instead of crashing.

---

## Requirements

- Python 3.11+
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

---

## Setup

1. **Clone or download this project**, then move into the project folder.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment file:**
   ```bash
   cp .env.example .env      # macOS/Linux
   copy .env.example .env    # Windows (cmd)
   Copy-Item .env.example .env   # Windows (PowerShell)
   ```

4. **Add your API key** to `.env`:
   ```
   GEMINI_API_KEY=your-real-api-key-here
   ```

---

## Usage

Run the chatbot:
```bash
python -m chatbot.cli
```

### Optional flags

| Flag | Description | Example |
|---|---|---|
| `--provider` | Choose the model provider (currently only `gemini`) | `--provider gemini` |
| `--system` | Set a custom system prompt | `--system "You are a helpful assistant."` |
| `--persona` | Launch the bot as a specific assistant persona (overrides `--system`) | `--persona "You are a Python tutor."` |
| `--max-tokens` | Set the sliding-window token budget before old messages are trimmed | `--max-tokens 4000` |

**Example:**
```bash
python -m chatbot.cli --persona "You are a Python tutor."
```

---

## In-Chat Commands

| Command | Description |
|---|---|
| `/help` | Show the list of available commands |
| `/cost` | Show total tokens used and total cost so far |
| `/clear` | Wipe conversation history and start fresh (keeps your persona/system prompt) |
| `/save <file>` | Save the conversation to a JSON file (default: `conversation.json`) |
| `/load <file>` | Load a previously saved conversation |
| `/quit` | Exit the chatbot |

---

## Project Structure

```
chatbot/
├── cli.py          # Main REPL loop — handles input, commands, and display
├── memory.py       # Sliding-window conversation memory and token trimming
├── providers.py    # Model API calls (Gemini), with retry logic for transient errors
├── pricing.py       # Cost calculation based on token usage
.env.example         # Template for your environment variables
requirements.txt     # Python dependencies
```

---

## Troubleshooting

**`API key not valid`**
Your `.env` file likely still has placeholder text, or the key was copied incorrectly. Double-check there are no quotes or extra spaces around the key.

**`429 RESOURCE_EXHAUSTED` (limit: 0)**
Your Google Cloud project may not have free-tier quota for that specific model. Try a different model (e.g. `gemini-2.0-flash-lite`) or generate a new API key in a fresh project at [aistudio.google.com](https://aistudio.google.com/apikey).

**`503 UNAVAILABLE`**
Google's servers are temporarily overloaded. The bot will automatically retry a few times — if it still fails, just wait a moment and try again.

---

## Notes

This project is built to be provider-agnostic at its core — `providers.py` is structured so additional providers (like OpenAI or Anthropic) can be added later without touching the rest of the codebase.
