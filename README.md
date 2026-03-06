# 🤖 PM Job Monitor Bot

A free, automated job monitor that checks **Internshala, Naukri, and LinkedIn** every 5 minutes for fresher-friendly **Product Management** and **Project Management** roles — and sends instant **Telegram alerts** so you can be among the first to apply.

Runs 24/7 on **GitHub Actions** — no server, no credit card needed.

---

## ✨ Features

- 🔍 **Monitors 3 platforms** — Internshala, Naukri, LinkedIn simultaneously
- 📋 **Reads full Job Descriptions** — skips roles that require 2+ years experience
- 🎯 **Title relevance filter** — only alerts for PM/Project Manager roles, no irrelevant noise
- 💼 **PPO detection** — flags internships with Pre-Placement Offer opportunities
- 🔥 **Priority alerts** — highlights roles tagged "fresher", "APM", "trainee", "entry level"
- 📱 **Instant Telegram alerts** — get notified on your phone the moment a job is posted
- 🚫 **No duplicates** — tracks seen jobs in a database so you never get alerted twice
- ⏰ **Runs every 5 minutes** — via GitHub Actions cron, completely free

---

## 📁 File Structure

```
pm-job-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml       # GitHub Actions — runs every 5 mins
├── main.py                   # Local runner (for testing on your laptop)
├── run_once.py               # Used by GitHub Actions — runs one cycle and exits
├── config.py                 # All settings and keywords
├── jd_scanner.py             # Reads JDs and filters by experience requirements
├── internshala_bot.py        # Internshala scraper
├── naukri_bot.py             # Naukri scraper (API-based)
├── linkedin_bot.py           # LinkedIn scraper
├── database.py               # SQLite — tracks seen/applied jobs
├── telegram_alerts.py        # Sends Telegram notifications
├── requirements.txt          # Python dependencies
└── .gitignore
```

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

After 24–48 hours, GitHub will automatically start running it every 5 minutes on its own.

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

# Toggle platforms
MONITOR_INTERNSHALA = True
MONITOR_NAUKRI = True
MONITOR_LINKEDIN = True
```

---

## 📱 Telegram Alert Format

```
🔔 NEW JOB — Apply Now!
💼 PPO OPPORTUNITY   ← shown for PPO internships

📌 Associate Product Manager Intern
🏢 Razorpay
📍 Bangalore
🌐 Internshala
📋 ✅ Fresher-friendly: '...open to freshers and recent graduates...'

🔗 View Job → [link]
```

---

## 🧠 How JD Filtering Works

Every new job found goes through this pipeline before you're alerted:

```
New job detected
      ↓
Title relevance check  →  skip if not PM/Project related
      ↓
Fetch full JD text
      ↓
Blocklist check        →  skip if "2+ years", "senior", "VP" etc.
      ↓
Allowlist check        →  approve if "fresher", "0-1 years", "PPO" etc.
      ↓
Send Telegram alert with reason
```

---

## ⚠️ Notes

- GitHub Actions cron schedules may take **24–48 hours** to activate on new repos
- LinkedIn has bot detection — occasional empty results are normal
- Naukri uses an internal API which may change over time
- This bot is for **alert only** — you apply manually via the link in the Telegram message

---

## 📄 License

MIT — free to use and modify.
