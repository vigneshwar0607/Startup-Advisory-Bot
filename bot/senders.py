"""WhatsApp delivery: Meta WhatsApp Cloud API (official) or CallMeBot (free, own number only)."""
import os
import re
import time

import requests

TIMEOUT = 60


def _one_line(s: str, limit: int) -> str:
    """Template parameters may not contain newlines, tabs or 4+ spaces."""
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def _chunks(text: str, size: int) -> list[str]:
    parts, buf = [], ""
    for para in text.split("\n\n"):
        candidate = f"{buf}\n\n{para}" if buf else para
        if len(candidate) <= size:
            buf = candidate
            continue
        if buf:
            parts.append(buf)
        while len(para) > size:
            parts.append(para[:size])
            para = para[size:]
        buf = para
    if buf:
        parts.append(buf)
    return parts


# ---------------------------------------------------------------- Meta Cloud API
class MetaSender:
    def __init__(self):
        self.token = os.environ["META_ACCESS_TOKEN"]
        self.phone_id = os.environ["META_PHONE_NUMBER_ID"]
        self.to = [n.strip().lstrip("+") for n in os.environ["WHATSAPP_TO"].split(",") if n.strip()]
        self.template = os.getenv("META_TEMPLATE_NAME", "daily_lesson")
        self.lang = os.getenv("META_TEMPLATE_LANG", "en")
        ver = os.getenv("META_GRAPH_VERSION", "v23.0")
        self.base = f"https://graph.facebook.com/{ver}/{self.phone_id}"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def _upload_pdf(self, path: str) -> str:
        with open(path, "rb") as fh:
            r = requests.post(f"{self.base}/media", headers=self.headers, timeout=TIMEOUT,
                              data={"messaging_product": "whatsapp", "type": "application/pdf"},
                              files={"file": (os.path.basename(path), fh, "application/pdf")})
        r.raise_for_status()
        return r.json()["id"]

    def _post(self, payload: dict) -> requests.Response:
        return requests.post(f"{self.base}/messages", headers=self.headers, json=payload, timeout=TIMEOUT)

    def send(self, lesson, day: int, pdf_path: str) -> None:
        media_id = self._upload_pdf(pdf_path)
        filename = os.path.basename(pdf_path)
        for to in self.to:
            # 1) Template message (works any time; this is the business-initiated message)
            payload = {
                "messaging_product": "whatsapp", "to": to, "type": "template",
                "template": {
                    "name": self.template, "language": {"code": self.lang},
                    "components": [
                        {"type": "header", "parameters": [
                            {"type": "document", "document": {"id": media_id, "filename": filename}}]},
                        {"type": "body", "parameters": [
                            {"type": "text", "text": str(day)},
                            {"type": "text", "text": _one_line(lesson.title.split(":", 1)[-1], 120)},
                            {"type": "text", "text": _one_line(lesson.takeaway, 250)},
                            {"type": "text", "text": _one_line(lesson.action, 250)},
                        ]},
                    ],
                },
            }
            r = self._post(payload)
            if r.status_code >= 300:
                raise RuntimeError(f"Template send to {to} failed: {r.status_code} {r.text}")
            print(f"[ok] template + PDF sent to {to}")

            # 2) Full text version — only delivered if you messaged the bot in the last 24h.
            if os.getenv("META_SEND_FULL_TEXT", "true").lower() == "true":
                for part in _chunks(lesson.whatsapp, 4000):
                    r = self._post({"messaging_product": "whatsapp", "to": to, "type": "text",
                                    "text": {"body": part, "preview_url": False}})
                    if r.status_code >= 300:
                        print(f"[info] full text not sent to {to} (24h window closed is normal): {r.text[:200]}")
                        break
                else:
                    print(f"[ok] full text sent to {to}")


# ---------------------------------------------------------------- CallMeBot
class CallMeBotSender:
    URL = "https://api.callmebot.com/whatsapp.php"

    def __init__(self):
        self.phone = os.environ["CALLMEBOT_PHONE"]
        self.apikey = os.environ["CALLMEBOT_APIKEY"]

    def send(self, lesson, day: int, pdf_path: str) -> None:  # noqa: ARG002 (no attachments on CallMeBot)
        parts = _chunks(lesson.whatsapp, 1500)
        for i, part in enumerate(parts, 1):
            text = part if len(parts) == 1 else f"({i}/{len(parts)})\n{part}"
            r = requests.get(self.URL, timeout=TIMEOUT,
                             params={"phone": self.phone, "apikey": self.apikey, "text": text})
            if r.status_code >= 300 or "error" in r.text.lower()[:300]:
                raise RuntimeError(f"CallMeBot failed: {r.status_code} {r.text[:300]}")
            time.sleep(4)  # be gentle with the free service
        print(f"[ok] CallMeBot sent {len(parts)} message(s)")


def get_sender():
    provider = os.getenv("WHATSAPP_PROVIDER", "meta").lower()
    if provider == "meta":
        return MetaSender()
    if provider == "callmebot":
        return CallMeBotSender()
    raise ValueError(f"Unknown WHATSAPP_PROVIDER: {provider}")
