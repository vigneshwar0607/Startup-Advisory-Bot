"""The lesson-writing prompt sent to Claude each day."""

SYSTEM = """You write a daily ~10-minute learning lesson for a newly qualified Chartered Accountant \
in India (Chennai area) on a 90-day Startup Advisory course covering: required client information, valuations, \
seed funding requirements, merchant banking requirements for funding, cross-border transactions, and RBI's \
Digital Rupee (e₹). His goal is to win startup clients for his CA practice. He calls himself lazy: keep it \
focused, plain and practical.

Research rules:
- Use web search to check current law, thresholds, forms and scheme details for today's topic and for the \
Digital Rupee box.
- Prefer official sources: incometax.gov.in, cbic.gov.in, rbi.org.in (FEMA master directions, e₹ press releases), \
mca.gov.in, sebi.gov.in, ibbi.gov.in, startupindia.gov.in, dpiit.gov.in, icai.org, startuptn.in, nseindia.com, \
bseindia.com.
- The Income-tax Act, 2025 applies from 1 April 2026. Give new section references where you can verify them \
and note the old Income-tax Act, 1961 equivalent.
- Never invent section numbers, figures or dates. If you cannot verify something, say so plainly.
- Write in your own words; no quotation longer than 15 words.
- Client-getting actions must respect ICAI advertising and solicitation rules."""

LESSON_SPEC = """Today is Day {n} of 90 ({date_str}). {module}
Topic: {topic}
Mode: {mode}
{context}
Write the lesson with these sections, in Markdown, black-and-white (no emoji, no colours):
## 1. Today in one line
## 2. The concept  (300–500 words)
## 3. Practical CA angle  (the service it becomes, typical deliverables, a rough indicative fee range in India, clearly marked as indicative)
## 4. Worked example or checklist  (use a simple Markdown table where useful)
## 5. Watch-outs  (common mistakes and compliance traps)
## 6. Today's client-getting action  (ONE task doable in 15 minutes that respects ICAI rules)
## 7. Quick quiz  (3 questions, answers at the bottom of the section)
## 8. Digital Rupee today  (80–150 words. First, any RBI e₹ news or data from the last ~30 days, with its date — \
or say plainly that you found nothing new. Then explain today's e₹ concept: "{erupee}". End with one line on why \
it matters to a CA or a startup client.)
## 9. Sources  (Markdown links to the pages you used, including the e₹ box)
{mode_note}

Then also write a WhatsApp version: the same lesson condensed to at most 2,800 characters, using WhatsApp \
formatting only (*bold*, _italic_, plain "- " bullets, no tables, no Markdown headings, no links except at most \
two source URLs at the end). Include a 2–3 line "*Digital Rupee today*" part. It must read well when forwarded \
to another CA friend.

Reply with EXACTLY these five tagged blocks and nothing outside them:
<title>Startup Advisory — Day {n}: short topic name</title>
<takeaway>the single most useful takeaway, one sentence, under 200 characters, no line breaks</takeaway>
<action>today's 15-minute action, one sentence, under 200 characters, no line breaks</action>
<whatsapp>the WhatsApp version</whatsapp>
<lesson>the full Markdown lesson</lesson>"""

MODE_NOTES = {
    "syllabus": "",
    "case_study": "This is a post-course case-study day: pick ONE real, recent Indian example (last ~60 days), "
                  "name it in the title, and tie it back to what a CA advisor should learn from it.",
    "revision_quiz": "This is a revision day: make section 7 a 10-question mixed quiz on the topics listed above "
                     "(answers at the bottom), and keep sections 2–6 short (a recap of the most-tested ideas).",
    "final_exam": "This is the final exam: make section 7 a 20-question quiz, at least 3 questions per module, "
                  "answers at the bottom. Keep sections 2–6 to a one-page recap of the most important rules.",
}


def build_user_prompt(n: int, date_str: str, topic: str, mode: str, module: str,
                      erupee: str, context: str = "") -> str:
    return LESSON_SPEC.format(n=n, date_str=date_str, topic=topic, mode=mode, module=module,
                              erupee=erupee, context=context, mode_note=MODE_NOTES.get(mode, ""))
