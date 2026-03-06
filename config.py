# ============================================================
# CONFIG
# Telegram credentials are read from environment variables
# so they stay secret in GitHub Actions.
# All other settings are hardcoded here safely.
# ============================================================

import os

# --- TELEGRAM ALERTS ---
# Locally: fill in your values directly below
# GitHub Actions: set as Repository Secrets (Settings → Secrets → Actions)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")

# --- JOB KEYWORDS TO MONITOR ---
JOB_KEYWORDS = [
    "product manager",
    "product management intern",
    "associate product manager",
    "APM intern",
    "product analyst",
    "product management trainee",
    "junior product manager",
    "growth product manager",
]

# --- LOCATIONS TO MONITOR ---
JOB_LOCATIONS = ["Work From Home", "Bangalore", "Hyderabad"]

# ============================================================
# SETTINGS — No need to change these
# ============================================================
MONITOR_INTERNSHALA = True
MONITOR_NAUKRI = True
MONITOR_LINKEDIN = True
AUTO_APPLY_INTERNSHALA = False  # Alert only — you apply manually
CHECK_INTERVAL_MINUTES = 5
MAX_APPLIES_PER_DAY = 0        # Not used in alert-only mode

# --- PM TITLE RELEVANCE FILTER ---
# Job title must contain at least one of these to be alerted
RELEVANT_TITLE_KEYWORDS = [
    "product manager", "product management", "associate product",
    "apm", "product analyst", "product intern", "growth product",
    "junior product", "product lead", "product owner",
    "product strategist", "product operations", "product marketing",
    "business analyst", "strategy analyst", "growth analyst",
    "marketing intern", "business intern", "operations intern",
]

# --- EXPERIENCE FILTERS ---
BLACKLIST_KEYWORDS = [
    "5+ years", "10+ years", "senior", "head of product",
    "VP", "director", "lead product", "principal"
]

PRIORITY_KEYWORDS = [
    "fresher", "0 experience", "trainee", "intern",
    "associate", "APM", "entry level", "graduate"
]
