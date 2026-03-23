"""
Prelude — LLM Client (v1)
Unified wrapper for GPT-4o-mini via OpenAI SDK.
Model: gpt-4o-mini (~$0.26 per 500-agent simulation)
"""

import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_EXTRACTION_MODEL = "gpt-4o"  # used once per brief — worth the quality


def _get_client():
    """Lazy-load OpenAI client. Returns None if no API key configured."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key in ("placeholder", "your_key_here", ""):
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except ImportError:
        logger.error("openai package not installed — run: pip install openai")
        return None


def is_available() -> bool:
    """Return True if LLM calls are possible."""
    return _get_client() is not None


# ─── Core call ───────────────────────────────────────────────────────────────

def call_llm(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 200,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str | None:
    """
    Make a single LLM call. Returns the text response or None on failure.
    Set json_mode=True when you need structured JSON output.
    """
    client = _get_client()
    if client is None:
        return None

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("LLM call failed: %s", exc)
        return None


def call_llm_json(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 300,
    temperature: float = 0.3,
) -> dict | None:
    """
    Make a JSON-mode LLM call. Returns parsed dict or None on failure.
    Uses lower temperature for structured extraction tasks.
    """
    raw = call_llm(system, user, model=model, max_tokens=max_tokens,
                   temperature=temperature, json_mode=True)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("LLM returned invalid JSON: %s", raw[:200])
        return None
