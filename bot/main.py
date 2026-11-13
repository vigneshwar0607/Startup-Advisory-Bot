"""Daily entry point: work out the day, write the lesson with Claude, archive it, send it on WhatsApp.

Usage:
  python -m bot.main                     # normal daily run
  python -m bot.main --day 15            # force a day number
  python -m bot.main --dry-run           # generate + archive, do not send
  python -m bot.main --day 15 --resend   # resend an archived lesson without calling Claude
  python -m bot.main --index             # build only the 90-day index PDF (lessons/course-index.pdf)

Day 1 is set automatically the first time the bot sends a real lesson (saved in lessons/.course_start).
Set the COURSE_START_DATE variable (YYYY-MM-DD) to override it.
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from .syllabus import (COURSE_DAYS, SYLLABUS, day_number, erupee_box_topic, module_for, today_ist,
                       topic_for)

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "lessons"


def course_start(on: date, live: bool) -> date:
    if os.getenv("COURSE_START_DATE"):
        return date.fromisoformat(os.environ["COURSE_START_DATE"])
    marker = ARCHIVE / ".course_start"
    if marker.exists():
        return date.fromisoformat(marker.read_text().strip())
    if live:  # first real send = Day 1
        ARCHIVE.mkdir(exist_ok=True)
        marker.write_text(on.isoformat() + "\n")
    return on


def quiz_context(day: int, mode: str) -> str:
    if mode == "revision_quiz" and day <= COURSE_DAYS:
        prev = [d for d in range(1, day) if SYLLABUS[d][1] not in ("QUIZ", "QUIZ_FINAL")]
        covered = prev[-6:] if day > 7 else prev
        older = [d for d in prev if d not in covered]
        lines = [f"- Day {d}: {SYLLABUS[d][0]}" for d in covered]
        txt = "Topics to quiz (mostly these, the last week):\n" + "\n".join(lines)
        if older:
            txt += "\nAlso include 2 questions from earlier days: " + "; ".join(SYLLABUS[d][0] for d in older[-12:])
        return txt + "\n"
    if mode == "final_exam":
        return "All 90 course topics:\n" + "\n".join(
            f"- Day {d}: {SYLLABUS[d][0]}" for d in range(1, COURSE_DAYS + 1)) + "\n"
    return ""


def archive(day: int, lesson, on: date) -> Path:
    ARCHIVE.mkdir(exist_ok=True)
    stem = ARCHIVE / f"day-{day:03d}"
    stem.with_suffix(".md").write_text(f"# {lesson.title}\n\n_{on.isoformat()}_\n\n{lesson.markdown}\n", encoding="utf-8")
    stem.with_suffix(".whatsapp.txt").write_text(lesson.whatsapp + "\n", encoding="utf-8")
    stem.with_suffix(".json").write_text(json.dumps(
        {"day": day, "date": on.isoformat(), "title": lesson.title,
         "takeaway": lesson.takeaway, "action": lesson.action}, ensure_ascii=False, indent=2), encoding="utf-8")
    return stem


def load_archived(day: int):
    from .claude_client import Lesson
    stem = ARCHIVE / f"day-{day:03d}"
    meta = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))
    md = stem.with_suffix(".md").read_text(encoding="utf-8").split("\n", 4)[-1]
    return Lesson(meta["title"], meta["takeaway"], meta["action"],
                  stem.with_suffix(".whatsapp.txt").read_text(encoding="utf-8").strip(), md)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resend", action="store_true", help="send the archived lesson for --day without calling Claude")
    ap.add_argument("--index", action="store_true", help="only build lessons/course-index.pdf")
    ap.add_argument("--generate-only", action="store_true",
                    help="write and archive today's lesson but do not send (the workflow sends after pushing)")
    args = ap.parse_args(argv)
    dry = args.dry_run or os.getenv("DRY_RUN", "").lower() == "true"

    on = today_ist()
    start = course_start(on, live=not dry and not args.index and not args.resend)
    day = args.day or day_number(start, on)

    from .render_pdf import markdown_to_pdf
    if args.index:
        ARCHIVE.mkdir(exist_ok=True)
        out = markdown_to_pdf("", "", str(ARCHIVE / "course-index.pdf"), current_day=max(day, 1), index_only=True)
        print(f"[ok] {out}")
        return 0

    topic, mode = topic_for(day)
    module = module_for(day)
    erupee = erupee_box_topic(day)
    print(f"[info] Day {day} ({on}) — {module} — {mode}: {topic}\n[info] e₹ box: {erupee}")

    stem = ARCHIVE / f"day-{day:03d}"
    if args.resend and stem.with_suffix(".json").exists():
        lesson = load_archived(day)
        print(f"[info] using archived {stem.name}")
    else:
        from .prompt import build_user_prompt
        prompt = build_user_prompt(day, on.strftime("%d %B %Y"), topic, mode, module, erupee,
                                   quiz_context(day, mode))
        lesson = _load_generator()(prompt)
        archive(day, lesson, on)
    pdf_path = str(stem.with_suffix(".pdf"))
    if not os.path.exists(pdf_path) or not args.resend:
        markdown_to_pdf(lesson.title, lesson.markdown, pdf_path, current_day=day)
    print(f"[ok] archived {stem.name}.md / .pdf / .whatsapp.txt")

    if dry or args.generate_only:
        print("[info] not sending (dry run / generate-only).\n----- WhatsApp text -----\n" + lesson.whatsapp)
        return 0

    from .senders import send_all
    send_all(lesson, day, pdf_path, pdf_link(day))
    return 0


def _load_generator():
    """AI_PROVIDER=gemini (free, default) or claude (paid)."""
    if os.getenv("AI_PROVIDER", "gemini").lower() == "claude":
        from .claude_client import generate_lesson
    else:
        from .gemini_client import generate_lesson
    return generate_lesson


def pdf_link(day: int) -> str | None:
    """Public link to today's PDF in the repo (GitHub shows PDFs in the browser). Needs a public repo."""
    base = os.getenv("LESSON_LINK_BASE")
    if not base and os.getenv("GITHUB_REPOSITORY"):
        branch = os.getenv("GITHUB_REF_NAME", "main")
        base = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/blob/{branch}/lessons"
    return f"{base.rstrip('/')}/day-{day:03d}.pdf" if base else None


if __name__ == "__main__":
    sys.exit(main())
