# Startup Advisory — daily WhatsApp lesson bot

Every morning (06:47 IST) this repo:

1. Works out today's lesson number in the **90-day course**. Day 1 is the first day the bot sends a real lesson.
2. Asks **Google Gemini (free tier, with Google Search)** to write the lesson. Every lesson ends with a short **Digital Rupee today** box: the latest RBI e₹ news, plus one e₹ concept.
3. Saves it in `lessons/` as Markdown, a WhatsApp-text version and a plain black-and-white PDF. **Page 1 of every PDF is the full 90-day index, with today's day marked ▶.**
4. Sends it through every channel you've set up. **Telegram** and **email** get the PDF attached; **WhatsApp via CallMeBot** gets the text plus a link to the PDF. All three are free.

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
- Telegram bot and Gmail: free and official, with the PDF attached
- CallMeBot: free WhatsApp sending to your own number (unofficial)
- GitHub Actions: free for public repos

Paid upgrades are built in if you ever want them (`AI_PROVIDER=claude`; Meta's WhatsApp API).

```
bot/syllabus.py       90-day course, modules, daily e₹ topics, day rule
bot/prompt.py         the lesson brief the AI follows
bot/gemini_client.py  FREE: Gemini + Google Search grounding
bot/claude_client.py  paid option: Claude + web search
bot/render_pdf.py     page 1 index + lesson -> PDF
bot/senders.py        Telegram, Email, CallMeBot (free); Meta Cloud API (paid)
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

### 3. Choose your channels (set up one, two or all three)

The bot sends through every channel whose secrets you add.

#### Telegram (recommended: free, official, PDF attached) → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
1. In Telegram, search for **@BotFather** (blue tick), tap **Start**, then send `/newbot`.
2. Give it a name (e.g. `Startup Advisory Lessons`) and a username ending in `bot` (e.g. `vicky_ca_lessons_bot`).
3. BotFather replies with a **token** like `123456789:AAH...`. That's `TELEGRAM_BOT_TOKEN`.
4. Open your new bot (BotFather gives you a link) and tap **Start**. Bots can't message you until you do this.
5. Search for **@userinfobot**, tap **Start**, and it replies with your **Id** (a number). That's `TELEGRAM_CHAT_ID`.
6. Optional, to share with friends:
   - Create a **Channel** (public, e.g. `@ca_startup_lessons`).
   - In the channel's settings, go to **Administrators → Add Admin**, add your bot, and allow it to post.
   - Set `TELEGRAM_CHAT_ID` to `123456789,@ca_startup_lessons` (your Id, a comma, then the channel).

#### Email (free with Gmail, PDF attached) → `EMAIL_USER`, `EMAIL_APP_PASSWORD`, `EMAIL_TO`
Gmail needs an **app password**, a separate 16-letter password just for the bot. Your real password is never used.
1. Turn on **2-Step Verification**: myaccount.google.com → **Security** → 2-Step Verification. This is required for app passwords.
2. Go to **myaccount.google.com/apppasswords**, name it `lesson-bot`, and click **Create**.
3. Copy the 16-letter password. That's `EMAIL_APP_PASSWORD`. Spaces don't matter.
4. `EMAIL_USER` is your Gmail address.
5. `EMAIL_TO` is optional. It's who receives the lesson, separated by commas, e.g. `you@gmail.com,friend@gmail.com`. It defaults to yourself. Other recipients are BCC'd, so they can't see each other's addresses.

#### WhatsApp via CallMeBot (free, unofficial, text + PDF link) → `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY`
1. Open **callmebot.com** and go to the WhatsApp API page. Save the phone number shown there in your contacts. If the page says the bot is full, check back in a day or two.
2. From your WhatsApp, send that contact exactly: `I allow callmebot to send me messages`
3. Within about 2 minutes you get a reply containing **your apikey**.
4. `CALLMEBOT_PHONE` is your own number with + and country code, e.g. `+919876543210`.
5. CallMeBot is a third-party service that sees the message text. That's fine for these lessons, but never use it for client data.

### 4. Add the secrets to GitHub
Go to **Settings → Secrets and variables → Actions → New repository secret** and add `GEMINI_API_KEY` plus the secrets for the channels you chose:

| Name | Channel | Value |
|---|---|---|
| `GEMINI_API_KEY` | required | from step 2 |
| `TELEGRAM_BOT_TOKEN` | Telegram | from BotFather |
| `TELEGRAM_CHAT_ID` | Telegram | your Id, optionally `,@yourchannel` |
| `EMAIL_USER` | Email | your Gmail address |
| `EMAIL_APP_PASSWORD` | Email | the 16-letter app password |
| `EMAIL_TO` | Email (optional) | recipients, comma-separated |
| `CALLMEBOT_PHONE` | WhatsApp | `+91...` your number |
| `CALLMEBOT_APIKEY` | WhatsApp | from CallMeBot |

Also check **Settings → Actions → General → Workflow permissions → Read and write permissions → Save**. This lets the bot save each lesson so its PDF link works.

### 5. Test it
1. Go to **Actions → Daily Startup Advisory lesson → Run workflow**, tick **dry_run** and run it. Then open `lessons/` and look at the PDF.
2. Run it again **without** dry_run. The lesson should arrive on each channel you set up, and that day becomes **Day 1**. If one channel fails, the others still send, and the run shows a red cross naming the failed channel.

From then on it runs every morning at about 06:47 IST.

---

## Optional variables (Settings → Secrets and variables → Actions → Variables)

| Name | Default | Purpose |
|---|---|---|
| `GEMINI_MODEL` | newest stable "flash" model on your key | pin a model if Google renames things |
| `COURSE_START_DATE` | blank | Blank means Day 1 is the first real send (saved in `lessons/.course_start`). Set YYYY-MM-DD to restart or shift. |
| `AI_PROVIDER` | `gemini` | `claude` = paid Claude API (needs secret `ANTHROPIC_API_KEY`) |
| `DELIVERY` | blank (all configured channels) | Limit channels, e.g. `telegram,email`. Options: `telegram`, `email`, `callmebot`, `meta`. `meta` = official WhatsApp API with PDF attached (paid per message; needs `META_ACCESS_TOKEN`, `META_PHONE_NUMBER_ID`, `WHATSAPP_TO` and an approved `daily_lesson` template whose body starts "Day {{1}} of 90: {{2}}") |

## Day-to-day
- **Course index only:** Run workflow with `index_only` ticked. This builds `lessons/course-index.pdf`.
- **Resend a day:** Run workflow with `day = 15` and tick `resend`. This uses the saved lesson, with no AI call.
- **Archive:** `lessons/` keeps every lesson as `.md`, `.pdf` and `.whatsapp.txt`.
- **Pause:** Actions → the workflow → `...` → **Disable workflow**.
- **Tests:** `pip install -r requirements.txt pytest pypdf && python -m pytest -q`

## Limits of the free setup
- **CallMeBot** is a free hobby service. It sends text only, only to your own number, and can occasionally be slow or down. Telegram and email are the dependable channels. If a day fails, re-run it with `resend`.
- **Gmail** allows a few hundred emails a day from a normal account. That's plenty, but don't use it as a mass mailing list.
- **Gemini free tier:** Google sets the daily limits and can change them. One lesson a day is far below them. On the free tier, Google may use prompts to improve its products. The lessons contain no private data, so this is fine here.
- Quality: Gemini Flash is good, but it is less careful than Claude at checking legal references. Treat each lesson as study material, not a legal opinion, and verify section numbers before using them with clients.
- Forwarding lessons to friends is fine. Before posting them publicly as a CA, keep ICAI's advertising rules in mind.
