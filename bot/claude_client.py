"""Calls the Claude API (with web search) and parses the tagged reply."""
import os
import re
from dataclasses import dataclass

import anthropic

from .prompt import SYSTEM

FALLBACK_MODEL = "claude-opus-5-5"


@dataclass
class Lesson:
    title: str
    takeaway: str
    action: str
    whatsapp: str
    markdown: str


def pick_model(client: anthropic.Anthropic) -> str:
    """Use CLAUDE_MODEL if set; otherwise the newest Sonnet the account can see (cheaper), else a fallback."""
    if os.getenv("CLAUDE_MODEL"):
        return os.environ["CLAUDE_MODEL"]
    try:
        models = list(client.models.list(limit=100))  # newest first
        for m in models:
            if "sonnet" in m.id:
                return m.id
        if models:
            return models[0].id
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] could not list models ({exc}); using {FALLBACK_MODEL}")
    return FALLBACK_MODEL


def _tag(text: str, name: str) -> str:
    m = re.search(rf"<{name}>(.*?)</{name}>", text, re.S)
    if not m:
        raise ValueError(f"Claude reply is missing <{name}>")
    return m.group(1).strip()


def parse_reply(text: str) -> Lesson:
    one_line = lambda s: " ".join(s.split())  # noqa: E731
    return Lesson(
        title=one_line(_tag(text, "title")),
        takeaway=one_line(_tag(text, "takeaway")),
        action=one_line(_tag(text, "action")),
        whatsapp=_tag(text, "whatsapp"),
        markdown=_tag(text, "lesson"),
    )


def generate_lesson(user_prompt: str) -> Lesson:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    model = pick_model(client)
    print(f"[info] model: {model}")
    tools = [{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": int(os.getenv("MAX_SEARCHES", "10")),
        "user_location": {"type": "approximate", "city": "Chennai", "country": "IN",
                          "timezone": "Asia/Kolkata"},
    }]
    messages = [{"role": "user", "content": user_prompt}]

    text = ""
    for _ in range(6):  # continue through pause_turn
        resp = client.messages.create(model=model, max_tokens=16000, system=SYSTEM,
                                      tools=tools, messages=messages)
        text += "".join(b.text for b in resp.content if b.type == "text")
        if resp.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": resp.content})

    if resp.stop_reason == "max_tokens":
        print("[warn] reply hit max_tokens; parsing what arrived")
    return parse_reply(text)
