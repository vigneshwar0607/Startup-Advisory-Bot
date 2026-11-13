# Startup Advisory — daily WhatsApp lesson bot

Every morning (06:47 IST) this repo:

1. Works out today's lesson number in the **90-day course**. Day 1 is the first day the bot sends a real lesson.
2. Asks **Google Gemini (free tier, with Google Search)** to write the lesson. Every lesson ends with a short **Digital Rupee today** box: the latest RBI e₹ news, plus one e₹ concept.
3. Saves it in `lessons/` as Markdown, a WhatsApp-text version and a plain black-and-white PDF. **Page 1 of every PDF is the full 90-day index, with today's day marked ▶.**
4. Sends it to your WhatsApp through **CallMeBot (free)**, with a link to the PDF. You can forward the message and link to anyone.

## The 90-day course

| Days | Module |
|---|---|
| 1–13 | Required Information & Foundations: onboarding checklist, entity choice, DPIIT, tax benefits, compliance, data room |
| 14–28 | Valuations: legal triggers and signatories, DCF, VC method, pre-revenue methods, CCPS/ESOP valuation, becoming an RV |
| 29–42 | Seed Funding Requirements: instruments, s.42 private placement, angels, Seed Fund, StartupTN/TANSEED, term sheets, cap tables |
| 43–55 | Merchant Banking for Funding: SEBI MB rules, when an MB is mandatory, SME and main-board IPOs, AIFs, restated financials |
| 56–70 | Cross-Border Transactions: FEMA/FDI, pricing, FIRMS reporting, ODI, flips, GIFT City, DTAA, ECB |
| 71–90 | Growth, Exits & Your Practice: virtual CFO, ESOPs, exits, GST, pricing, ICAI rules, three capstone cases, final exam, launch plan |

- **Digital Rupee (e₹):** six full lessons (Days 12, 27, 53, 68, 76, 88), plus the daily box.
- **Revision quizzes:** every 7th day, with a final exam on Day 89.
- **After Day 90:** daily real-world case studies, still with a quiz every 7th day.

The full topic list is in `bot/syllabus.py`. Edit it there to change the course.

**Default setup is 100% free: no card, no payment anywhere.**
- Gemini API free tier: no card needed
- CallMeBot: free WhatsApp sending to your own number
- GitHub Actions: free for public repos

Paid upgrades are built in if you ever want them (`AI_PROVIDER=claude`, `WHATSAPP_PROVIDER=meta`).

```
bot/syllabus.py       90-day course, modules, daily e₹ topics, day rule
bot/prompt.py         the lesson brief the AI follows
bot/gemini_client.py  FREE: Gemini + Google Search grounding
bot/claude_client.py  paid option: Claude + web search
bot/render_pdf.py     page 1 index + lesson -> PDF
bot/senders.py        CallMeBot (free) or Meta Cloud API (paid)
bot/main.py           the daily run
.github/workflows/daily-lesson.yml   the schedule
```

---

## Free setup (about 20 minutes, one time)

### 1. Repo must be **public**
The WhatsApp message links to the day's PDF in this repo. A public repo lets that link open on your phone, and for anyone you forward it to, without logging in. It also keeps GitHub Actions free.

To switch: **Settings → General → scroll to Danger Zone → Change visibility → Public**.

Your keys stay hidden: secrets are never visible, even in a public repo. Only the code and the lessons become public.

### 2. Free Gemini key → secret `GEMINI_API_KEY`
1. Go to **aistudio.google.com** and sign in with your Google account.
2. Click **Get API key**, then **Create API key**. Let it create a new project if asked.
3. Copy the key, which starts with `AIza`. **Don't** click anything about billing or "upgrade". Staying on the free tier means you can never be charged.

### 3. Free CallMeBot key → secrets `CALLMEBOT_PHONE` and `CALLMEBOT_APIKEY`
1. Open **callmebot.com** and go to the WhatsApp API page. Save the phone number shown there in your contacts. If the page says the bot is full, check back in a day or two.
2. From your WhatsApp, send that contact exactly: `I allow callmebot to send me messages`
3. Within about 2 minutes you get a reply containing **your apikey** (a number).
4. `CALLMEBOT_PHONE` is your own number with + and country code, e.g. `+919876543210`.

### 4. Add the secrets to GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Name | Value |
|---|---|
| `GEMINI_API_KEY` | from step 2 |
| `CALLMEBOT_PHONE` | `+91...` your number |
| `CALLMEBOT_APIKEY` | from step 3 |

Also check **Settings → Actions → General → Workflow permissions → Read and write permissions → Save**. This lets the bot save each lesson so its PDF link works.

### 5. Test it
1. Go to **Actions → Daily Startup Advisory lesson → Run workflow**, tick **dry_run** and run it. Then open `lessons/` and look at the PDF.
2. Run it again **without** dry_run. You should get the WhatsApp message, and that day becomes **Day 1**.

From then on it runs every morning at about 06:47 IST.

---

## Optional variables (Settings → Secrets and variables → Actions → Variables)

| Name | Default | Purpose |
|---|---|---|
| `GEMINI_MODEL` | newest stable "flash" model on your key | pin a model if Google renames things |
| `COURSE_START_DATE` | blank | Blank means Day 1 is the first real send (saved in `lessons/.course_start`). Set YYYY-MM-DD to restart or shift. |
| `AI_PROVIDER` | `gemini` | `claude` = paid Claude API (needs secret `ANTHROPIC_API_KEY`) |
| `WHATSAPP_PROVIDER` | `callmebot` | `meta` = official API with PDF attached (paid per message; needs `META_ACCESS_TOKEN`, `META_PHONE_NUMBER_ID`, `WHATSAPP_TO` and an approved `daily_lesson` template whose body starts "Day {{1}} of 90: {{2}}") |

## Day-to-day
- **Course index only:** Run workflow with `index_only` ticked. This builds `lessons/course-index.pdf`.
- **Resend a day:** Run workflow with `day = 15` and tick `resend`. This uses the saved lesson, with no AI call.
- **Archive:** `lessons/` keeps every lesson as `.md`, `.pdf` and `.whatsapp.txt`.
- **Pause:** Actions → the workflow → `...` → **Disable workflow**.
- **Tests:** `pip install -r requirements.txt pytest pypdf && python -m pytest -q`

## Limits of the free setup
- **CallMeBot** is a free hobby service. It sends text only, only to your own number, and can occasionally be slow or down. If a day fails, re-run it with `resend`.
- **Gemini free tier:** Google sets the daily limits and can change them. One lesson a day is far below them. On the free tier, Google may use prompts to improve its products. The lessons contain no private data, so this is fine here.
- Quality: Gemini Flash is good, but it is less careful than Claude at checking legal references. Treat each lesson as study material, not a legal opinion, and verify section numbers before using them with clients.
- Forwarding lessons to friends is fine. Before posting them publicly as a CA, keep ICAI's advertising rules in mind.
