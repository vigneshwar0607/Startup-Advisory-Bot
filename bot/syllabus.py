"""90-day Startup Advisory course: modules, daily topics, the daily Digital Rupee (e₹) box, and the day rule."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
COURSE_DAYS = 90

# (first_day, last_day, module title)
MODULES = [
    (1, 13, "Module 1 — Required Information & Foundations"),
    (14, 28, "Module 2 — Valuations"),
    (29, 42, "Module 3 — Seed Funding Requirements"),
    (43, 55, "Module 4 — Merchant Banking for Funding"),
    (56, 70, "Module 5 — Cross-Border Transactions"),
    (71, 90, "Module 6 — Growth, Exits & Your Practice"),
]

# day: (short title for the index, full brief for the lesson writer)
SYLLABUS: dict[int, tuple[str, str]] = {
    # Module 1 — Required information & foundations
    1: ("India's startup ecosystem & the CA's services map",
        "India's startup ecosystem and where a CA fits: a services map beyond audit and tax"),
    2: ("Client onboarding: the startup information checklist",
        "Startup Advisory required information: the onboarding checklist (KYC, incorporation documents, cap table, "
        "founder details, contracts, IP, bank, tax registrations) and how to request it"),
    3: ("Choosing the entity: Pvt Ltd vs LLP vs OPC",
        "Choosing the entity and structuring: Pvt Ltd vs LLP vs OPC, holding structures, investor preferences"),
    4: ("DPIIT recognition & Startup India benefits",
        "DPIIT recognition: eligibility, application process, documents, and Startup India benefits"),
    5: ("Startup tax benefits under the Income-tax Act, 2025",
        "Startup tax holiday, loss carry-forward and ESOP tax deferral under the Income-tax Act, 2025, mapped to "
        "the old 1961 Act provisions (80-IAC, 79, 192)"),
    6: ("Founders' agreement, vesting & founder shareholding",
        "Founders' agreement, vesting, reverse vesting, good/bad leaver and founder shareholding"),
    7: ("Week 1 revision quiz", "QUIZ"),
    8: ("AoA/SHA clauses investors expect; statutory registers",
        "Articles of Association and shareholders' agreement clauses investors expect, and the statutory registers "
        "a startup must maintain"),
    9: ("Startup compliance calendar",
        "Startup compliance calendar: ROC, GST, TDS, PF/ESI, labour law self-certification, DPIIT annual items"),
    10: ("Intellectual property basics for startups",
         "IP basics for startups: trademarks, patents, Startup India IPR facilitation, assigning founder-created IP "
         "to the company"),
    11: ("Accounting & MIS set-up for early-stage startups",
         "Setting up accounting, chart of accounts and monthly MIS for an early-stage startup"),
    12: ("[e₹] Digital Rupee 101: what RBI's CBDC is",
         "Digital Rupee (e₹) 101: what RBI's central bank digital currency is, e₹-R vs e₹-W, legal basis, how it "
         "differs from UPI, bank deposits and crypto, and current pilot status"),
    13: ("The investor-ready data room",
         "Building an investor-ready data room: folder structure, documents, common gaps"),
    # Module 2 — Valuations
    14: ("Week 2 revision quiz", "QUIZ"),
    15: ("When valuation is legally required & who signs",
         "When a valuation is legally needed: Companies Act (Registered Valuer), FEMA pricing, Income-tax FMV rules "
         "under the 2025 Act and Income-tax Rules, 2026, and who can sign each"),
    16: ("Valuation standards & report structure",
         "Valuation standards (ICAI Valuation Standards, IVS) and how a valuation report is structured"),
    17: ("DCF for startups (worked example)", "DCF for startups with a worked example"),
    18: ("VC method & First Chicago method", "VC method and First Chicago method with worked examples"),
    19: ("Pre-revenue methods: Scorecard, Berkus, RFS",
         "Pre-revenue valuation methods: Scorecard, Berkus, Risk-Factor Summation"),
    20: ("Comparable transactions & revenue multiples",
         "Comparable transactions and revenue multiples: sourcing data, adjustments"),
    21: ("Week 3 revision quiz", "QUIZ"),
    22: ("Valuing CCPS, convertible notes & iSAFE",
         "Valuing CCPS, CCDs, convertible notes and iSAFE notes; conversion mechanics"),
    23: ("ESOP valuation & Ind AS 102 accounting",
         "ESOP valuation and accounting under Ind AS 102 and the ICAI Guidance Note; perquisite FMV"),
    24: ("Becoming an IBBI Registered Valuer",
         "Becoming an IBBI Registered Valuer (Securities or Financial Assets): eligibility, exam, RVO course, costs"),
    25: ("Full valuation worked example", "Full startup valuation worked example: triangulate methods and reconcile"),
    26: ("Valuation disputes & lessons from case law",
         "Valuation disputes and lessons from Indian case law (legacy angel-tax, FEMA pricing, Companies Act)"),
    27: ("[e₹] Fintech & payments startups: rules & value",
         "Fintech and payments startups (UPI, payment aggregators, e₹ use cases): RBI regulation and what drives "
         "their valuation"),
    28: ("Week 4 revision quiz", "QUIZ"),
    # Module 3 — Seed funding requirements
    29: ("Funding stages & instrument choice",
         "Funding stages and instruments: equity, CCPS, CCDs, convertible notes, iSAFE"),
    30: ("Friends & family money: s.42 & deposit traps",
         "Raising from friends and family: private placement rules (Companies Act s.42), the deposit rules trap, "
         "convertible note exemption for DPIIT startups"),
    31: ("Angel investors, angel networks & SEBI Angel Funds",
         "Angel investors, angel networks and Angel Funds under SEBI AIF Regulations"),
    32: ("Startup India Seed Fund Scheme", "Startup India Seed Fund Scheme: eligibility, process, instruments"),
    33: ("StartupTN, TANSEED & other grants",
         "State and central grants: StartupTN, TANSEED, and other schemes relevant to Tamil Nadu startups"),
    34: ("Term sheet clauses explained", "Term sheet clauses: liquidation preference, anti-dilution, ESOP pool, "
                                        "protective provisions, drag/tag"),
    35: ("Week 5 revision quiz", "QUIZ"),
    36: ("Cap table & dilution modelling", "Cap table and dilution modelling across rounds (worked example)"),
    37: ("Financial model & pitch deck review", "Building the financial model and reviewing a pitch deck"),
    38: ("Private placement process: PAS-4, PAS-3 & timelines",
         "Private placement process step by step: offer letter (PAS-4), separate bank account, allotment, PAS-3, "
         "timelines and penalties"),
    39: ("Issuing CCPS/CCDs: approvals & mechanics",
         "Issuing CCPS/CCDs: board and shareholder approvals, terms, filings"),
    40: ("Due diligence: vendor-side & buy-side",
         "Due diligence: vendor-side (investor-ready) and buy-side checklists"),
    41: ("Debt for startups: venture debt & CGSS",
         "Debt options for startups: venture debt, Credit Guarantee Scheme for Startups, revenue-based financing"),
    42: ("Week 6 revision quiz", "QUIZ"),
    # Module 4 — Merchant banking requirements for funding
    43: ("Merchant bankers in India: role & SEBI regulation",
         "Merchant bankers in India: role and SEBI (Merchant Bankers) Regulations, including the latest amendments"),
    44: ("When a merchant banker is mandatory vs optional",
         "When funding or valuation work legally needs a SEBI-registered merchant banker (FEMA, ESOP FMV, swaps, "
         "IPOs, open offers) versus a CA or Registered Valuer"),
    45: ("MB valuation reports vs RV reports vs CA certificates",
         "Merchant banker valuation reports vs Registered Valuer reports vs CA certificates: scope, liability, cost"),
    46: ("SME IPO platforms: eligibility", "SME IPO platforms (NSE Emerge, BSE SME): eligibility and recent changes"),
    47: ("SME IPO process & the lead manager's role",
         "SME IPO process and the merchant banker's role: due diligence, underwriting, market making"),
    48: ("Main-board IPO for startups: ICDR essentials",
         "Main-board IPO for new-age startups: SEBI ICDR essentials, DRHP, lock-ins, KPI disclosures"),
    49: ("Week 7 revision quiz", "QUIZ"),
    50: ("Rights issues & preferential allotments with an MB",
         "Rights issues and preferential allotments, and where a merchant banker is involved"),
    51: ("AIFs, accredited investors & SEBI rules",
         "Fundraising from AIFs and accredited investors: SEBI framework and the CA's role"),
    52: ("Working with a merchant banker: what CAs certify",
         "Working with a merchant banker: engagement, due diligence, and the CA certificates they need"),
    53: ("[e₹] Wholesale CBDC & corporate treasury",
         "e₹ for businesses: wholesale CBDC (e₹-W) pilots, programmability and settlement, and what they mean for "
         "corporate treasury and funding"),
    54: ("Crowdfunding & Social Stock Exchange: what's legal",
         "Equity crowdfunding in India and the Social Stock Exchange: what is legal and what is not"),
    55: ("Restated financials & KPI certification",
         "Restated financial statements and KPI certification for offer documents"),
    # Module 5 — Cross-border transactions
    56: ("Week 8 revision quiz", "QUIZ"),
    57: ("FEMA & FDI framework for startups",
         "FEMA framework for startups: NDI Rules, FDI policy, automatic vs approval route, Press Note 3"),
    58: ("FDI pricing guidelines & valuation certificates",
         "FDI pricing guidelines and valuation certificates for issue and transfer of shares"),
    59: ("FIRMS reporting: FC-GPR, FC-TRS, FLA, LSF",
         "Reporting on the FIRMS portal: FC-GPR, FC-TRS, annual FLA return, late submission fees"),
    60: ("Downstream investment & ODI basics",
         "Downstream investment rules and Overseas Direct Investment basics for startups"),
    61: ("Convertible notes from foreign investors",
         "Convertible notes and iSAFE from non-resident investors under FEMA"),
    62: ("FVCI & foreign portfolio investment", "Foreign Venture Capital Investors and foreign portfolio investment"),
    63: ("Week 9 revision quiz", "QUIZ"),
    64: ("Flips & reverse flips (externalisation)", "Flips and reverse flips: tax and FEMA angles, recent cases"),
    65: ("GIFT City IFSC for startups & funds", "GIFT City IFSC for startups and funds: options and incentives"),
    66: ("Transfer pricing basics for startup groups",
         "Transfer pricing basics for startups with overseas parents or subsidiaries"),
    67: ("Paying abroad: DTAA, withholding, Form 15CA/CB",
         "Cross-border payments by startups: DTAA, withholding tax under the 2025 Act, Form 15CA/15CB equivalents"),
    68: ("[e₹] Cross-border payments & CBDC experiments",
         "Cross-border payments and CBDC: RBI's cross-border e₹ and payment-linkage experiments, LRS, export "
         "receivables"),
    69: ("External Commercial Borrowings for startups", "External Commercial Borrowings (ECB) for startups"),
    70: ("Week 10 revision quiz", "QUIZ"),
    # Module 6 — Growth, exits & building the practice
    71: ("Designing a Virtual CFO service",
         "Designing a Virtual CFO service: MIS, burn rate, runway, unit economics, board packs"),
    72: ("ESOP design, pools & buybacks", "ESOP design, pool sizing, vesting and ESOP buybacks"),
    73: ("Exits: secondaries, M&A & share swaps",
         "Exits: secondary sales, M&A, share-swap valuation, tax on exit"),
    74: ("GST for startups: SaaS exports, LUT, place of supply",
         "GST for startups: SaaS exports, LUT, place of supply, common errors"),
    75: ("Pricing your services & engagement letters",
         "Pricing your services: retainers vs transaction fees, engagement letters, scope control"),
    76: ("[e₹] Offline, programmable & DBT uses of e₹",
         "e₹ adoption: offline e₹, programmable payments, government transfers, and advisory opportunities for CAs"),
    77: ("Week 11 revision quiz", "QUIZ"),
    78: ("Getting clients ethically: incubators & referrals",
         "Getting clients ethically: incubators (IIT Madras ecosystem, StartupTN), networking, LinkedIn, referrals"),
    79: ("ICAI rules on advertising & social media",
         "ICAI rules on advertising, solicitation, websites and social media for CAs"),
    80: ("Your service toolkit: templates & checklists",
         "Building your service toolkit: templates, checklists, standard reports"),
    81: ("Working with VCs, angel networks, CSs & lawyers",
         "Building a referral network with VCs, angel networks, company secretaries and lawyers"),
    82: ("Winding up a startup: strike-off & fast-track exit",
         "Closing a startup: strike-off, fast-track exit, voluntary liquidation under IBC"),
    83: ("Regulatory watch: RBI, SEBI, MCA, CBDT updates",
         "Regulatory watch: the latest RBI, SEBI, MCA and CBDT changes affecting startups and how to track them"),
    84: ("Week 12 revision quiz", "QUIZ"),
    85: ("Capstone 1: onboarding a startup end-to-end",
         "Capstone case: onboarding a new startup client end-to-end"),
    86: ("Capstone 2: seed round from term sheet to FC-GPR",
         "Capstone case: a seed round with a foreign investor, from term sheet to FC-GPR"),
    87: ("Capstone 3: valuation & merchant-banker-led round",
         "Capstone case: a Series A needing valuation reports and a merchant banker"),
    88: ("[e₹] State of the Digital Rupee & what to watch",
         "Digital Rupee capstone: current state of e₹, latest RBI data and what CAs should watch"),
    89: ("Final exam (all modules)", "QUIZ_FINAL"),
    90: ("Your 90-day practice launch plan", "Your 90-day launch plan for a startup advisory practice"),
}

# Rotating topic for the short daily "Digital Rupee today" box (cycles every 30 days, deeper each cycle).
ERUPEE_DAILY = [
    "What a CBDC is and why RBI issued one", "e₹-R (retail) vs e₹-W (wholesale)",
    "RBI's Concept Note on CBDC — key design choices", "Legal basis: RBI Act changes making e₹ legal tender",
    "Two-tier distribution through banks", "e₹ wallets, tokens and denominations",
    "Privacy and anonymity design", "Offline e₹", "Programmable e₹", "Paying a UPI QR with e₹",
    "Non-bank participation in the e₹ pilot", "e₹-W and inter-bank settlement",
    "Cross-border CBDC projects India is part of", "e₹ vs stablecoins vs crypto — and the VDA tax angle",
    "How a business should record e₹ in its books", "KYC and AML for e₹",
    "Why e₹ pays no interest", "Holding and transaction limits", "Merchant acceptance of e₹",
    "e₹ for government transfers and subsidies", "e-CNY, digital euro and other CBDCs compared",
    "Risk of bank disintermediation", "CBDC and monetary policy", "Cybersecurity of e₹",
    "Audit evidence for e₹ transactions", "GST and invoicing when paid in e₹",
    "Startup opportunities built on e₹", "Latest RBI e₹ circulation and pilot statistics",
    "RBI's e₹ roadmap", "Client FAQ: should my business accept e₹?",
]


def today_ist() -> date:
    return datetime.now(IST).date()


def day_number(start: date, on: date) -> int:
    """Day 1 = start date."""
    return (on - start).days + 1


def module_for(n: int) -> str:
    for a, b, name in MODULES:
        if a <= n <= b:
            return name
    return "After the course — case studies & revision"


def erupee_box_topic(n: int) -> str:
    cycle = (n - 1) // len(ERUPEE_DAILY)
    base = ERUPEE_DAILY[(n - 1) % len(ERUPEE_DAILY)]
    return base if cycle == 0 else f"{base} (revisit {cycle + 1}: go one level deeper than before)"


def topic_for(n: int) -> tuple[str, str]:
    """Return (topic brief, mode). mode: syllabus | revision_quiz | final_exam | case_study."""
    if n < 1:
        raise ValueError(f"Day {n} is before the course start date")
    if n in SYLLABUS:
        short, full = SYLLABUS[n]
        if full == "QUIZ":
            return f"{short}: mixed questions on the previous days' topics", "revision_quiz"
        if full == "QUIZ_FINAL":
            return "Final exam covering all six modules", "final_exam"
        return full, "syllabus"
    if n % 7 == 0:
        return "Revision quiz covering earlier topics (mixed, all modules)", "revision_quiz"
    return (
        "Practical case study: one real, recent Indian startup funding round, valuation dispute, merchant-banking "
        "or cross-border deal, or regulatory change (search recent news and pick one)",
        "case_study",
    )


def index_rows() -> list[tuple[str, int | None, str]]:
    """Rows for the index page: ('module', None, title) or ('day', n, short title)."""
    rows = []
    for a, b, name in MODULES:
        rows.append(("module", None, name))
        rows.extend(("day", d, SYLLABUS[d][0]) for d in range(a, b + 1))
    return rows


assert sorted(SYLLABUS) == list(range(1, COURSE_DAYS + 1)), "syllabus must cover days 1-90"
