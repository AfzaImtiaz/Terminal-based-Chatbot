"""
Multi-provider CLI chatbot with sliding-window memory and live cost tracking.
Run with: python -m chatbot.cli
"""
import argparse
from dotenv import load_dotenv
load_dotenv()  # reads .env file so GEMINI_API_KEY is available
from colorama import Fore, Style, init as colorama_init
from chatbot.memory import ConversationManager
from chatbot.providers import call_model
from chatbot.pricing import compute_cost

colorama_init(autoreset=True)  # makes colors work on Windows terminals too

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
}

HELP_TEXT = """
Commands:
  /cost                Show running token usage and total spend
  /save <file>         Save conversation history to a JSON file (default: conversation.json)
  /load <file>         Load conversation history from a JSON file
  /clear               Wipe conversation history and start fresh (keeps persona/system prompt)
  /summary             Ask the model to summarize the conversation so far in 3 bullet points
  /quit                Exit
"""


def run(provider: str, system_prompt: str, max_tokens: int, input_fn=input, print_fn=print):
    """
    Core REPL loop. input_fn/print_fn are injectable so tests can run
    without touching real stdin/stdout.
    """
    model = DEFAULT_MODELS[provider]
    memory = ConversationManager(system_prompt=system_prompt, max_tokens=max_tokens)
    total_cost = 0.0
    total_tokens_used = 0

    print_fn(f"Chatting with {provider} ({model}). Type /help for commands.")

    while True:
        try:
            user_input = input_fn(Fore.WHITE + "you> " + Style.RESET_ALL).strip()
        except (EOFError, KeyboardInterrupt):
            print_fn("\nbye.")
            return

        if not user_input:
            continue
        if user_input == "/quit":
            return
        if user_input == "/help":
            print_fn(HELP_TEXT)
            continue
        if user_input == "/cost":
            print_fn(f"Total tokens used: {total_tokens_used} | Total cost: ${total_cost:.6f}")
            continue
        if user_input == "/clear":
            memory = ConversationManager(system_prompt=system_prompt, max_tokens=max_tokens)
            print_fn("Conversation history cleared. Starting fresh.")
            continue
        if user_input.startswith("/save"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) == 2 else "conversation.json"
            memory.save(path)
            print_fn(f"Saved to {path}")
            continue
        if user_input.startswith("/load"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) == 2 else "conversation.json"
            memory.load(path)
            print_fn(f"Loaded from {path}")
            continue

        memory.add("user", user_input)
        reply, usage = call_model(provider, model, memory.messages)
        memory.add("assistant", reply)

        cost = compute_cost(model, usage)
        total_cost += cost
        total_tokens_used += usage["input_tokens"] + usage["output_tokens"]

        print_fn(Fore.GREEN + f"\n{provider}> {reply}" + Style.RESET_ALL)
        print_fn(
            f"   [{usage['input_tokens']}in / {usage['output_tokens']}out tokens | "
            f"${cost:.6f} this turn | ${total_cost:.6f} total]\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Gemini CLI chatbot with memory")
    parser.add_argument("--provider", default="gemini", choices=DEFAULT_MODELS.keys())
    parser.add_argument(
        "--system", default="You are a helpful, concise assistant.",
        help="System prompt (overridden by --persona if both are given)"
    )
    parser.add_argument(
        "--persona", default=None,
        help='Launch as a specific assistant persona, e.g. --persona "You are a Python tutor."'
    )
    parser.add_argument(
        "--max-tokens", type=int, default=3000,
        help="Sliding-window token budget before old messages get dropped"
    )
    args = parser.parse_args()

    system_prompt = args.persona if args.persona else args.system
    run(args.provider, system_prompt, args.max_tokens)


if __name__ == "__main__":
    main()