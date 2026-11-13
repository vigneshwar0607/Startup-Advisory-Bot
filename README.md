# Startup Advisory — daily WhatsApp lesson bot

Every morning (06:47 IST) this repo:

1. Works out today's lesson number in the **90-day course**. Day 1 is the first day the bot sends a real lesson.
2. Asks Claude (with live web search on official sources) to write the lesson. Every lesson ends with a short **Digital Rupee today** box: the latest RBI e₹ news, plus one e₹ concept.
3. Saves it in `lessons/` as Markdown, a WhatsApp-text version and a plain black-and-white PDF. **Page 1 of every PDF is the full 90-day index, with today's day marked ▶.**
4. Sends it to your WhatsApp. The PDF and message can be forwarded to anyone.

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

Everything runs free on GitHub Actions. You only pay for the Claude API, plus Meta's small per-message charge if you use the official route.

```
bot/syllabus.py      90-day course, modules, daily e₹ topics, day rule
bot/prompt.py        the lesson brief Claude follows
bot/claude_client.py Claude API + web search, parses the reply
bot/render_pdf.py    Markdown -> PDF
bot/senders.py       Meta WhatsApp Cloud API, or CallMeBot
bot/main.py          the daily run
.github/workflows/daily-lesson.yml   the schedule
```

---

## Setup (about 45 minutes, one time)

### 1. Put the code on GitHub
1. Create a **private** repo on github.com, for example `startup-advisory-bot`.
2. Upload every file from this folder, keeping the folders. The `.github` folder is hidden on some PCs, so make sure it is included.

### 2. Get a Claude API key
1. Go to console.anthropic.com, sign in and add a small credit balance (for example $10).
2. Under **API Keys**, create a key and copy it.

### 3. Choose how WhatsApp messages are sent

#### Option A — Meta WhatsApp Cloud API (official, recommended)
1. Go to developers.facebook.com, choose **My Apps → Create App → Business**, then add the **WhatsApp** product.
2. Meta gives you a free **test phone number**. On **WhatsApp → API Setup**:
   - copy the **Phone number ID**;
   - under **To**, add your own WhatsApp number and verify it with the code Meta sends. You can add up to 5 recipients this way.
3. **Permanent token.** The token on that page expires in 24 hours. Instead, go to business.facebook.com → **Settings → Users → System users**. Add a system user (Admin), then **Assign assets** (your app plus the WhatsApp account, full control). Click **Generate token** with the permissions `whatsapp_business_messaging` and `whatsapp_business_management`, and set it to never expire. Copy the token.
4. **Create the message template.** In WhatsApp Manager, go to **Message templates → Create**:
   - Category: **Utility** (Meta may re-label it Marketing, which is fine). Name: `daily_lesson`. Language: **English (en)**.
   - Header: **Document**.
   - Body (copy exactly):
     ```
     Day {{1}} of 90: {{2}}

     Today's takeaway: {{3}}

     Your 15-minute action: {{4}}

     The full lesson is in the attached PDF. Forward it to anyone it may help.
     ```
   - Sample values: `15`, `Funding instruments`, `CCPS are the default seed instrument`, `List 5 Chennai incubators`. Upload any PDF as the sample header.
   - Submit it. Approval usually takes minutes to a few hours.
5. Optional: send any message (for example "hi") to the test number from your phone. For 24 hours after that, the bot also sends the full lesson as plain text. Otherwise you get the summary plus the PDF.

#### Option B — CallMeBot (free, your own number only, text only)
1. Follow callmebot.com's WhatsApp instructions: save their number and send the activation phrase. You get an API key back. Their page notes that new sign-ups sometimes pause when the bot is full.
2. Lessons arrive as text, split into a few messages. CallMeBot cannot send the PDF.

### 4. Add your secrets to GitHub
In the repo, go to **Settings → Secrets and variables → Actions**.

**Secrets** (New repository secret):

| Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude key |
| `META_ACCESS_TOKEN` | the permanent token (Option A) |
| `META_PHONE_NUMBER_ID` | the Phone number ID (Option A) |
| `WHATSAPP_TO` | your number with country code, e.g. `919876543210`. For several people, separate with commas. Each must be a verified recipient. |
| `CALLMEBOT_PHONE` | `+919876543210` (Option B only) |
| `CALLMEBOT_APIKEY` | the CallMeBot key (Option B only) |

**Variables** (Variables tab, all optional):

| Name | Default | Purpose |
|---|---|---|
| `WHATSAPP_PROVIDER` | `meta` | set to `callmebot` for Option B |
| `CLAUDE_MODEL` | newest Sonnet on your account | e.g. a Haiku model ID to cut cost, or an Opus ID for top quality |
| `COURSE_START_DATE` | blank | Leave blank: Day 1 is the first real send, saved in `lessons/.course_start`. Set a date (YYYY-MM-DD) to restart or shift the course. |

### 5. Test it
1. Open the **Actions** tab and enable workflows if GitHub asks.
2. Choose **Daily Startup Advisory lesson → Run workflow**, tick **dry_run** and run it. Check the log, and the new files under `lessons/`.
3. Run it again without dry_run. The lesson should arrive on WhatsApp.

From then on it runs every morning on its own.

---

## Day-to-day
- **Course index only:** Run workflow with `index_only` ticked. This builds `lessons/course-index.pdf`, which you can share on its own.
- **Resend a day:** Run workflow with `day = 15` and tick `resend`. This uses the saved lesson and does not call Claude again.
- **Archive:** the `lessons/` folder keeps every lesson as `.md`, `.pdf` and `.whatsapp.txt`. You can share the repo or the files.
- **Pause:** Actions → the workflow → `...` → **Disable workflow**.
- **Run offline tests:** `pip install -r requirements.txt pytest && python -m pytest -q`

## Rough running costs (estimates; check current price pages)
- **GitHub Actions:** free (about 2–4 minutes a day).
- **Claude API:** Sonnet with web search is very roughly $0.15–0.50 per lesson, mostly from search results counted as input tokens plus $10 per 1,000 searches. Capped at 10 searches a day (`MAX_SEARCHES`).
- **Meta:** charges per template message in India at a small per-message rate. See Meta's INR rate card. **CallMeBot:** free.

## Notes
- The lesson brief tells Claude never to invent section numbers and to flag anything it could not verify. Still treat each lesson as study material, not a legal opinion.
- Forwarding the lesson to friends is fine. Before posting it publicly as a CA, keep ICAI's advertising rules in mind.
