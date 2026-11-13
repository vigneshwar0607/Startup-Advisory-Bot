"""Offline tests: no API keys, no network. Run: python -m pytest -q"""
import os
from datetime import date
from unittest import mock

from bot import main as bot_main
from bot.claude_client import parse_reply
from bot.senders import CallMeBotSender, MetaSender, _one_line
from bot.syllabus import SYLLABUS, day_number, erupee_box_topic, topic_for

FAKE_REPLY = """Some preamble the parser should ignore.
<title>Startup Advisory — Day 15: Funding instruments</title>
<takeaway>Most Indian seed rounds use CCPS, not plain equity,
because investors want preference rights.</takeaway>
<action>List 5 Chennai incubators and note who runs their mentor network.</action>
<whatsapp>*Day 15: Funding instruments*

- Equity: simplest, no preference.
- CCPS: preferred + converts later — the seed default.

_Answers: 1-b, 2-a, 3-c_</whatsapp>
<lesson>## 1. Today in one line

CCPS dominate Indian VC rounds.

## 4. Worked example

| Instrument | Preference | FEMA pricing |
| --- | --- | --- |
| Equity | None | ≥ fair value |
| CCPS | Yes | Conversion price fixed upfront |

## 8. Sources

- [RBI](https://rbi.org.in)
</lesson>"""


def test_day_numbers():
    start = date(2026, 10, 30)
    assert day_number(start, date(2026, 10, 30)) == 1
    assert day_number(start, date(2026, 11, 12)) == 14
    assert day_number(start, date(2026, 11, 13)) == 15
    assert topic_for(15)[1] == "syllabus"
    assert topic_for(35)[1] == "revision_quiz"
    assert topic_for(89)[1] == "final_exam"
    assert topic_for(92)[1] == "case_study"
    assert topic_for(91)[1] == "revision_quiz"
    assert sorted(SYLLABUS) == list(range(1, 91))
    assert sum("[e₹]" in SYLLABUS[d][0] for d in SYLLABUS) == 6


def test_parse_reply():
    lesson = parse_reply(FAKE_REPLY)
    assert lesson.title.endswith("Funding instruments")
    assert "\n" not in lesson.takeaway
    assert "| CCPS |" in lesson.markdown


def test_one_line_param():
    assert _one_line("a\n\tb    c", 50) == "a b c"
    assert len(_one_line("x" * 300, 250)) == 250


def _run_dry(tmp_path):
    with mock.patch.object(bot_main, "ARCHIVE", tmp_path), mock.patch.dict(os.environ, {"COURSE_START_DATE": ""}), \
         mock.patch.object(bot_main, "_load_generator", return_value=lambda prompt: parse_reply(FAKE_REPLY)):
        assert bot_main.main(["--day", "15", "--dry-run"]) == 0
    return tmp_path / "day-015.pdf"


def test_dry_run_builds_pdf(tmp_path):
    pdf = _run_dry(tmp_path)
    assert pdf.exists() and pdf.stat().st_size > 1000
    assert (tmp_path / "day-015.whatsapp.txt").exists()


def test_meta_payload(tmp_path):
    pdf = _run_dry(tmp_path)
    env = {"META_ACCESS_TOKEN": "t", "META_PHONE_NUMBER_ID": "123", "WHATSAPP_TO": "+919800000000"}
    with mock.patch.dict(os.environ, env), mock.patch("bot.senders.requests.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"id": "MEDIA1"}
        MetaSender().send(parse_reply(FAKE_REPLY), 15, str(pdf))
    template_call = post.call_args_list[1].kwargs["json"]
    assert template_call["to"] == "919800000000"
    comps = template_call["template"]["components"]
    assert comps[0]["parameters"][0]["document"]["id"] == "MEDIA1"
    for p in comps[1]["parameters"]:
        assert "\n" not in p["text"]
    assert post.call_args_list[2].kwargs["json"]["type"] == "text"


def test_callmebot_chunks(tmp_path):
    lesson = parse_reply(FAKE_REPLY)
    lesson.whatsapp = "\n\n".join(["para " * 60] * 10)  # ~3000 chars
    env = {"CALLMEBOT_PHONE": "+919800000000", "CALLMEBOT_APIKEY": "k"}
    with mock.patch.dict(os.environ, env), mock.patch("bot.senders.requests.get") as get, \
         mock.patch("bot.senders.time.sleep"):
        get.return_value.status_code = 200
        get.return_value.text = "Message queued"
        CallMeBotSender().send(lesson, 15, "", "https://github.com/u/r/blob/main/lessons/day-015.pdf")
    assert get.call_count >= 2
    assert "day-015.pdf" in get.call_args_list[-1].kwargs["params"]["text"]
    assert all(len(c.kwargs["params"]["text"]) <= 1510 for c in get.call_args_list)


def test_dry_run_pdf_has_index_first(tmp_path):
    pdf = _run_dry(tmp_path)
    from pypdf import PdfReader  # noqa: PLC0415
    reader = PdfReader(str(pdf))
    assert len(reader.pages) >= 2
    first = reader.pages[0].extract_text()
    assert "90-Day Course Index" in first and "Merchant Banking" in first
    assert not (tmp_path / ".course_start").exists()  # dry runs never fix Day 1


def test_quiz_context_and_erupee():
    ctx = bot_main.quiz_context(14, "revision_quiz")
    assert "Day 13" in ctx and "Day 7:" not in ctx
    assert "Day 90" in bot_main.quiz_context(89, "final_exam")
    assert erupee_box_topic(1) != erupee_box_topic(2)
    assert "revisit 2" in erupee_box_topic(31)


def test_first_live_run_sets_day_one(tmp_path):
    from datetime import date  # noqa: PLC0415
    with mock.patch.object(bot_main, "ARCHIVE", tmp_path), mock.patch.dict(os.environ, {"COURSE_START_DATE": ""}):
        assert bot_main.course_start(date(2026, 11, 20), live=True) == date(2026, 11, 20)
        assert bot_main.course_start(date(2026, 11, 25), live=True) == date(2026, 11, 20)


def test_pdf_link_and_gemini_model_pick():
    with mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "vicky/startup-advisory-bot", "GITHUB_REF_NAME": "main",
                                      "LESSON_LINK_BASE": ""}):
        assert bot_main.pdf_link(3) == "https://github.com/vicky/startup-advisory-bot/blob/main/lessons/day-003.pdf"
    from bot import gemini_client  # noqa: PLC0415
    models = {"models": [
        {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-3-flash-preview", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-3-flash", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-3-flash-lite", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-3-pro", "supportedGenerationMethods": ["generateContent"]},
    ]}
    with mock.patch.dict(os.environ, {"GEMINI_MODEL": ""}), mock.patch("bot.gemini_client.requests.get") as get:
        get.return_value.json.return_value = models
        assert gemini_client.pick_model("k") == "gemini-3-flash"


def test_gemini_generate_parses_and_adds_sources():
    from bot import gemini_client  # noqa: PLC0415
    reply = {"candidates": [{"content": {"parts": [{"text": FAKE_REPLY}]},
                             "groundingMetadata": {"groundingChunks": [{"web": {"title": "rbi.org.in", "uri": "https://x"}}]}}]}
    with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k", "GEMINI_MODEL": "gemini-3-flash"}), \
         mock.patch("bot.gemini_client.requests.post") as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = reply
        lesson = gemini_client.generate_lesson("prompt")
    assert "rbi.org.in" in lesson.markdown
    assert post.call_args.kwargs["json"]["tools"] == [{"google_search": {}}]
