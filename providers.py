"""
Unified call_model() — Gemini only for now.
To add OpenAI or Anthropic later, add their if-blocks here and nowhere else.
"""
import os
import time
from google import genai
from google.genai import errors

_gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))


def _call_with_retry(fn, max_retries=3, base_delay=2):
    """Retry a function call on transient 503 (overloaded) or 429 (rate limit) errors."""
    for attempt in range(max_retries):
        try:
            return fn()
        except errors.ServerError:
            if attempt == max_retries - 1:
                raise
            wait = base_delay * (2 ** attempt)
            print(f"\n[Server busy (503), retrying in {wait}s... attempt {attempt + 1}/{max_retries}]")
            time.sleep(wait)
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                wait = base_delay * (2 ** attempt)
                print(f"\n[Rate limited (429), retrying in {wait}s... attempt {attempt + 1}/{max_retries}]")
                time.sleep(wait)
            else:
                raise


def call_model(provider: str, model: str, messages: list[dict]) -> tuple[str, dict]:
    """
    messages: list of {"role": "system"|"user"|"assistant", "content": str}
    Returns (response_text, usage) where usage has "input_tokens"/"output_tokens".
    """
    if provider == "gemini":
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        convo = [m for m in messages if m["role"] != "system"]

        # Gemini uses "user"/"model" roles, not "user"/"assistant"
        contents = [
            {
                "role": "user" if m["role"] == "user" else "model",
                "parts": [{"text": m["content"]}],
            }
            for m in convo
        ]

        config = {"system_instruction": system_msg} if system_msg else None

        resp = _call_with_retry(lambda: _gemini_client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        ))

        text = resp.text
        usage = {
            "input_tokens": resp.usage_metadata.prompt_token_count,
            "output_tokens": resp.usage_metadata.candidates_token_count,
        }
        return text, usage

    raise ValueError(f"Unknown provider: {provider!r}. Currently only 'gemini' is supported.")