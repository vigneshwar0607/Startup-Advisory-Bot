"""FREE option: Google Gemini API (AI Studio key, free tier) with Google Search grounding.

No SDK needed — plain REST calls, so Google's library changes can't break the bot.
"""
import os
import re
import time

import requests

from .claude_client import Lesson, parse_reply
from .prompt import SYSTEM

API = "https://generativelanguage.googleapis.com/v1beta"
SKIP = ("lite", "image", "tts", "audio", "live", "embedding", "vision", "thinking-exp", "learnlm", "gemma", "robotics")


def _version_key(name: str) -> tuple:
    nums = [int(x) for x in re.findall(r"\d+", name.split("/")[-1])[:3]]
    stable = 0 if ("preview" in name or "exp" in name) else 1
    return (*nums, stable)


def pick_model(key: str) -> str:
    """GEMINI_MODEL if set, else the newest stable 'flash' text model this key can use (flash = free tier)."""
    if os.getenv("GEMINI_MODEL"):
        return os.environ["GEMINI_MODEL"].removeprefix("models/")
    r = requests.get(f"{API}/models", params={"key": key, "pageSize": 1000}, timeout=60)
    r.raise_for_status()
    names = [m["name"] for m in r.json().get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", [])
             and "flash" in m["name"] and not any(s in m["name"] for s in SKIP)]
    if not names:
        raise RuntimeError("No Gemini flash model available for this key; set GEMINI_MODEL")
    return max(names, key=_version_key).removeprefix("models/")


def _sources_footer(data: dict) -> str:
    chunks = (data.get("candidates", [{}])[0].get("groundingMetadata", {}) or {}).get("groundingChunks", []) or []
    seen, lines = set(), []
    for c in chunks:
        web = c.get("web") or {}
        title, uri = web.get("title"), web.get("uri")
        if title and uri and title not in seen:
            seen.add(title)
            lines.append(f"- [{title}]({uri})")
    return ("\n\nGoogle Search pages used (links redirect via Google):\n" + "\n".join(lines[:12])) if lines else ""


def generate_lesson(user_prompt: str) -> Lesson:
    key = os.environ["GEMINI_API_KEY"]
    model = pick_model(key)
    print(f"[info] model: {model} (Gemini free tier)")
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 16000},
    }
    last = None
    for attempt in range(4):
        r = requests.post(f"{API}/models/{model}:generateContent", params={"key": key}, json=body, timeout=300)
        if r.status_code in (429, 500, 503) and attempt < 3:
            wait = 30 * (attempt + 1)
            print(f"[warn] Gemini {r.status_code}; retrying in {wait}s")
            time.sleep(wait)
            last = r
            continue
        r.raise_for_status()
        data = r.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
        lesson = parse_reply(text)
        lesson.markdown += _sources_footer(data)
        return lesson
    raise RuntimeError(f"Gemini failed: {last.status_code if last else '?'} {last.text[:300] if last else ''}")
