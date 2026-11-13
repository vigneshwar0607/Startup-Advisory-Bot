"""Delivery channels: Telegram (free, official), Email (free via Gmail), CallMeBot WhatsApp (free, unofficial),
Meta WhatsApp Cloud API (official, paid per message). Every configured channel is used."""
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

    def send(self, lesson, day: int, pdf_path: str, link: str | None = None) -> None:  # noqa: ARG002
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

    def send(self, lesson, day: int, pdf_path: str, link: str | None = None) -> None:  # noqa: ARG002
        text = lesson.whatsapp
        if link:  # CallMeBot can't attach files, so point to the PDF (index + full lesson) instead
            text += f"\n\n*Full lesson + 90-day index (PDF):*\n{link}"
        parts = _chunks(text, 1500)
        for i, part in enumerate(parts, 1):
            text = part if len(parts) == 1 else f"({i}/{len(parts)})\n{part}"
            r = requests.get(self.URL, timeout=TIMEOUT,
                             params={"phone": self.phone, "apikey": self.apikey, "text": text})
            if r.status_code >= 300 or "error" in r.text.lower()[:300]:
                raise RuntimeError(f"CallMeBot failed: {r.status_code} {r.text[:300]}")
            time.sleep(4)  # be gentle with the free service
        print(f"[ok] CallMeBot sent {len(parts)} message(s)")


# ---------------------------------------------------------------- Telegram (free, official)
class TelegramSender:
    """Sends the PDF with a short caption, then the full text. Chat IDs: your user ID and/or @yourchannel."""

    def __init__(self):
        self.token = os.environ["TELEGRAM_BOT_TOKEN"]
        self.chats = [c.strip() for c in os.environ["TELEGRAM_CHAT_ID"].split(",") if c.strip()]
        self.api = f"https://api.telegram.org/bot{self.token}"

    def _call(self, method: str, **kwargs) -> dict:
        r = requests.post(f"{self.api}/{method}", timeout=TIMEOUT, **kwargs)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if not data.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {r.status_code} {r.text[:300]}")
        return data

    def _text(self, chat: str, text: str) -> None:
        try:  # WhatsApp-style *bold* / _italic_ works in Telegram's legacy Markdown
            self._call("sendMessage", data={"chat_id": chat, "text": text, "parse_mode": "Markdown",
                                            "disable_web_page_preview": "true"})
        except RuntimeError:  # unbalanced * or _ -> send as plain text instead
            self._call("sendMessage", data={"chat_id": chat, "text": text, "disable_web_page_preview": "true"})

    def send(self, lesson, day: int, pdf_path: str, link: str | None = None) -> None:  # noqa: ARG002
        caption = _one_line(f"{lesson.title} | Takeaway: {lesson.takeaway} | 15-min action: {lesson.action}", 1000)
        for chat in self.chats:
            with open(pdf_path, "rb") as fh:
                self._call("sendDocument", data={"chat_id": chat, "caption": caption},
                           files={"document": (os.path.basename(pdf_path), fh, "application/pdf")})
            for part in _chunks(lesson.whatsapp, 4000):
                self._text(chat, part)
            print(f"[ok] Telegram sent to {chat}")


# ---------------------------------------------------------------- Email (free with Gmail app password)
class EmailSender:
    def __init__(self):
        self.user = os.environ["EMAIL_USER"]
        self.password = os.environ["EMAIL_APP_PASSWORD"].replace(" ", "")
        self.to = [a.strip() for a in os.getenv("EMAIL_TO", self.user).split(",") if a.strip()]
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))

    def build(self, lesson, pdf_path: str):
        import markdown  # noqa: PLC0415
        from email.message import EmailMessage  # noqa: PLC0415

        msg = EmailMessage()
        msg["Subject"] = lesson.title
        msg["From"] = self.user
        msg["To"] = self.user
        if len(self.to) > 1 or self.to[0] != self.user:
            msg["Bcc"] = ", ".join(self.to)  # recipients don't see each other's addresses
        plain = f"Takeaway: {lesson.takeaway}\n15-minute action: {lesson.action}\n\n{lesson.markdown}"
        msg.set_content(plain)
        html = markdown.markdown(lesson.markdown, extensions=["tables", "sane_lists"])
        msg.add_alternative(
            "<div style='font-family:Arial,sans-serif;font-size:15px;line-height:1.5;color:#000;max-width:720px'>"
            f"<h2>{lesson.title}</h2><p><b>Takeaway:</b> {lesson.takeaway}<br><b>15-minute action:</b> "
            f"{lesson.action}</p><p>PDF (with the 90-day index) attached.</p><hr>"
            f"{html.replace('<table>', '<table border=1 cellpadding=4 style=border-collapse:collapse>')}</div>",
            subtype="html")
        with open(pdf_path, "rb") as fh:
            msg.add_attachment(fh.read(), maintype="application", subtype="pdf",
                               filename=os.path.basename(pdf_path))
        return msg

    def send(self, lesson, day: int, pdf_path: str, link: str | None = None) -> None:  # noqa: ARG002
        import smtplib  # noqa: PLC0415
        msg = self.build(lesson, pdf_path)
        with smtplib.SMTP(self.host, self.port, timeout=TIMEOUT) as smtp:
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.send_message(msg)
        print(f"[ok] email sent to {len(self.to)} recipient(s)")


# ---------------------------------------------------------------- choosing channels
CHANNELS = {
    "telegram": (TelegramSender, "TELEGRAM_BOT_TOKEN"),
    "email": (EmailSender, "EMAIL_APP_PASSWORD"),
    "callmebot": (CallMeBotSender, "CALLMEBOT_APIKEY"),
    "meta": (MetaSender, "META_ACCESS_TOKEN"),
}


def selected_channels() -> list[str]:
    """DELIVERY=telegram,email,... if set; otherwise every channel whose secret is filled in."""
    wanted = os.getenv("DELIVERY") or os.getenv("WHATSAPP_PROVIDER") or ""
    if wanted.strip():
        names = [n.strip().lower() for n in wanted.split(",") if n.strip()]
        unknown = [n for n in names if n not in CHANNELS]
        if unknown:
            raise ValueError(f"Unknown DELIVERY channel(s): {unknown}; use {list(CHANNELS)}")
        return names
    names = [n for n, (_, secret) in CHANNELS.items() if os.getenv(secret)]
    if not names:
        raise RuntimeError("No delivery channel set up: add Telegram, email, CallMeBot or Meta secrets")
    return names


def send_all(lesson, day: int, pdf_path: str, link: str | None = None) -> None:
    """Try every channel; one failing doesn't stop the others. Raises at the end if any failed."""
    failed = []
    for name in selected_channels():
        try:
            CHANNELS[name][0]().send(lesson, day, pdf_path, link)
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {name}: {exc}")
            failed.append(name)
    if failed:
        raise RuntimeError(f"Delivery failed for: {', '.join(failed)} (others were sent)")
