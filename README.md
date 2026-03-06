# 🤖 PM Job Monitor Bot

A free, automated job monitor that checks **7 platforms + 15 company career pages** every 30 minutes for fresher-friendly **Product Management**, **Project Management** roles and **APM Programs** — and sends instant **Telegram alerts** so you can be among the first to apply.

Runs 24/7 on **GitHub Actions** — no server, no credit card needed.

---

## ✨ Features

- 🔍 **Monitors 7 platforms** — Internshala, Naukri, LinkedIn, Unstop, Wellfound, Company Career Pages, PM Programs
- 🏢 **15 company career pages** — catches jobs 24-48hrs before they appear on job boards
- 🎯 **APM Program tracking** — monitors Razorpay, Swiggy, CRED, Meesho, Groww, Google, Amazon and more for structured PM programs
- 📋 **Reads full Job Descriptions** — skips roles that require 2+ years experience
- 🎯 **Title relevance filter** — only alerts for PM/Project Manager roles, no irrelevant noise
- 📅 **Date filter** — skips old job postings, only alerts for recent ones
- 💼 **PPO detection** — flags internships with Pre-Placement Offer opportunities
- 🔥 **Priority alerts** — highlights roles tagged "fresher", "APM", "trainee", "entry level"
- 📱 **Instant Telegram alerts** — get notified on your phone the moment a job is posted
- 🚫 **No duplicates** — tracks seen jobs in SQLite database, never alerts twice
- ⏰ **Runs every 30 minutes** — via GitHub Actions cron, completely free

---

## 📁 File Structure

```
pm-job-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml         # GitHub Actions — runs every 30 mins
├── run_once.py                 # Used by GitHub Actions — runs one cycle and exits
├── main.py                     # Local runner (for testing on your laptop)
├── config.py                   # All settings, keywords and toggles
├── jd_scanner.py               # Reads JDs and filters by experience requirements
├── database.py                 # SQLite — tracks seen/applied jobs
├── telegram_alerts.py          # Sends Telegram notifications
│
├── internshala_bot.py          # Internshala scraper (with date filter)
├── naukri_bot.py               # Naukri scraper (API-based)
├── linkedin_bot.py             # LinkedIn scraper (entry level + intern filter)
├── unstop_bot.py               # Unstop scraper (great for PPO internships)
├── wellfound_bot.py            # Wellfound/AngelList (startup PM roles)
├── career_pages_bot.py         # 15 company career pages (Lever + Greenhouse APIs)
├── pm_programs_bot.py          # APM Programs & PM Fellowships
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🌐 Platforms Monitored

| Platform | Method | Best For |
|---|---|---|
| **Internshala** | HTML scraping | Fresher jobs & internships |
| **Naukri** | Internal JSON API | High volume Indian job market |
| **LinkedIn** | HTML scraping | Entry level, last 1hr filter |
| **Unstop** | Public API | PPO internships, competitions |
| **Wellfound** | HTML scraping | Startup PM roles |
| **Career Pages** | Lever/Greenhouse APIs + scraping | Jobs 24-48hrs before job boards |
| **PM Programs** | Lever/Greenhouse APIs + scraping | APM programs & fellowships |

---

## 🏢 Company Career Pages

### Via Lever API
Zepto, CRED, Meesho, Groww, Razorpay, BrowserStack, Postman, Chargebee

### Via Greenhouse API
Swiggy, Freshworks, Clevertap, Darwinbox

### Direct Scraping
Zomato, PhonePe, Paytm, Flipkart, Google, Microsoft, Amazon

> To add more companies, just add an entry to the `COMPANIES` list in `career_pages_bot.py`.

---

## 🎯 APM Programs Tracked

| Company | Program |
|---|---|
| Razorpay | APM Program |
| Swiggy | APM Program |
| CRED | APM |
| Meesho | PM Fellowship |
| Groww | APM |
| Zepto | PM Program |
| Zomato | APM |
| PhonePe | PM Program |
| Freshworks | PM Program |
| Flipkart | GCA Program |
| Paytm | APM |
| Google | APM Program (India) |
| Microsoft | PM Internship (India) |
| Amazon | PMT Internship (India) |

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/pm-job-monitor.git
cd pm-job-monitor
```

### 2. Set up Telegram Bot (2 mins)
1. Open Telegram → search **@BotFather** → type `/newbot`
2. Give it a name → copy the **bot token**
3. Search **@userinfobot** → start it → copy your **Chat ID**
4. Message your new bot once (click Start) so it can send you messages

### 3. Add GitHub Secrets
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID from @userinfobot |

### 4. Enable GitHub Actions write permissions
Go to **Settings → Actions → General → Workflow permissions**
→ Select **Read and write permissions** → Save

### 5. Make repo public (for unlimited free minutes)
Go to **Settings → Danger Zone → Change visibility → Make public**

> Your Telegram credentials are safe — they live in GitHub Secrets, never in the code.

### 6. Trigger the first run
Go to **Actions** tab → **PM Job Monitor Bot** → **Run workflow**

---

## 🖥️ Running Locally

```bash
pip install -r requirements.txt
python main.py
```

Set your Telegram credentials directly in `config.py` for local runs.

---

## ⚙️ Configuration

All settings are in `config.py`:

```python
# Add or remove job keywords
JOB_KEYWORDS = [
    "product manager",
    "associate product manager",
    "project coordinator",
    # add more here...
]

# Change locations
JOB_LOCATIONS = ["Work From Home", "Bangalore", "Hyderabad"]

# Toggle platforms on/off
MONITOR_INTERNSHALA = True
MONITOR_NAUKRI = True
MONITOR_LINKEDIN = True
MONITOR_UNSTOP = True
MONITOR_WELLFOUND = True
MONITOR_CAREER_PAGES = True
MONITOR_PM_PROGRAMS = True
```

---

## 📱 Telegram Alert Formats

**Regular job:**
```
🔔 NEW JOB — Apply Now!

📌 Associate Product Manager Intern
🏢 Razorpay
📍 Bangalore
🌐 Internshala
📋 ✅ Fresher-friendly: '...open to freshers...'

🔗 View Job → [link]
```

**PPO Internship:**
```
🔔 NEW JOB — Apply Now!
💼 PPO OPPORTUNITY

📌 Product Intern (PPO)
🏢 Swiggy
📍 Bangalore
🌐 Unstop 🟠
```

**APM Program:**
```
🎯 PM PROGRAM — Razorpay APM Program

📌 Associate Product Manager
🏢 Razorpay
📍 Bangalore
📋 ✅ Fresher-friendly: '...new graduates...'
```

---

## 🧠 How JD Filtering Works

Every new job goes through this pipeline before you're alerted:

```
New job detected
      ↓
Date check         →  skip if posted more than 24hrs ago (Internshala)
      ↓
Title relevance    →  skip if not PM/Project/APM related
      ↓
Fetch full JD text
      ↓
Blocklist check    →  skip if "2+ years", "senior", "VP" etc.
      ↓
Allowlist check    →  approve if "fresher", "0-1 years", "PPO", "intern" etc.
      ↓
Send Telegram alert with reason snippet
```

---

## 🔁 How Duplicate Prevention Works

Every job gets a unique ID from its URL:
```python
job_id = "internshala_" + hashlib.md5(job_url.encode()).hexdigest()[:10]
```
This is saved to `jobs.db` after every alert. On the next run, already-seen jobs are silently skipped. The database is committed back to the repo after every GitHub Actions run so memory persists across runs.

---

## ⚠️ Notes

- GitHub Actions cron may run every **30-60 mins** on free accounts due to runner availability
- LinkedIn has bot detection — occasional empty results are normal
- Naukri uses an internal API which may change over time
- This bot is **alert only** — you apply manually via the link in Telegram
- Career page scrapers may break if companies redesign their sites

---

## 📄 License

MIT — free to use and modify.
