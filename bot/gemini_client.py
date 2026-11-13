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


def candidate_models(key: str) -> list[str]:
    """Models to try, best first. GEMINI_MODEL (comma list allowed) goes first if set.

    Newest models often have little or no free-tier quota, so we fall back through older 'flash'
    models and finally 'flash-lite' models until one answers.
    """
    pinned = [m.strip().removeprefix("models/") for m in os.getenv("GEMINI_MODEL", "").split(",") if m.strip()]
    r = requests.get(f"{API}/models", params={"key": key, "pageSize": 1000}, timeout=60)
    r.raise_for_status()
    names = [m["name"].removeprefix("models/") for m in r.json().get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]]
    lite_skip = tuple(x for x in SKIP if x != "lite")
    full = sorted((n for n in names if not any(x in n for x in SKIP)), key=_version_key, reverse=True)
    lite = sorted((n for n in names if "lite" in n and not any(x in n for x in lite_skip)),
                  key=_version_key, reverse=True)
    ordered = pinned + [n for n in full + lite if n not in pinned]
    if not ordered:
        raise RuntimeError("No Gemini flash model available for this key; set GEMINI_MODEL")
    return ordered[: int(os.getenv("GEMINI_MAX_MODELS", "8"))]


def pick_model(key: str) -> str:
    return candidate_models(key)[0]


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


NO_SEARCH_NOTE = ("\n\nIMPORTANT: live web search is unavailable for this lesson. Write from your own knowledge, "
                  "mark any section number, figure, date or scheme detail you are not certain of as "
                  "'(unverified — check the official source)', and list official sources to check in Sources.")


def _try(model: str, key: str, body: dict) -> tuple[dict | None, str]:
    """One model, up to 2 attempts. Returns (json, '') or (None, reason)."""
    for attempt in range(2):
        r = requests.post(f"{API}/models/{model}:generateContent", params={"key": key}, json=body, timeout=300)
        if r.ok:
            return r.json(), ""
        reason = f"{r.status_code} {r.text[:300]}"
        hard_quota = r.status_code == 429 and ("limit: 0" in r.text or "PerDay" in r.text)
        if r.status_code in (429, 500, 503) and attempt == 0 and not hard_quota:
            print(f"[warn] {model}: {r.status_code}; retrying in 20s")
            time.sleep(20)
            continue
        if r.status_code in (400, 404, 429, 500, 503):
            return None, reason  # move on to the next model
        r.raise_for_status()
    return None, reason


def generate_lesson(user_prompt: str) -> Lesson:
    key = os.environ["GEMINI_API_KEY"]
    models = candidate_models(key)
    errors = []
    # pass 1: with Google Search grounding; pass 2 (last resort): without it
    for with_search in (True, False):
        body = {
            "systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt + ("" if with_search else NO_SEARCH_NOTE)}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 16000},
        }
        if with_search:
            body["tools"] = [{"google_search": {}}]
        for model in models:
            print(f"[info] trying {model} ({'with' if with_search else 'without'} Google Search)")
            data, reason = _try(model, key, body)
            if data is None:
                print(f"[warn] {model} unavailable: {reason[:200]}")
                errors.append(f"{model}: {reason[:120]}")
                continue
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts)
            try:
                lesson = parse_reply(text)
            except ValueError as exc:
                print(f"[warn] {model} reply unusable ({exc}); trying next model")
                errors.append(f"{model}: {exc}")
                continue
            lesson.markdown += _sources_footer(data)
            print(f"[ok] lesson written by {model}")
            return lesson
    raise RuntimeError("All Gemini models failed (free quota?). Details:\n" + "\n".join(errors[-8:]))
