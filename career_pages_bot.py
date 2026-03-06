"""
career_pages_bot.py
-------------------
Monitors career pages of top Indian companies directly.
Uses Lever & Greenhouse public APIs where available,
and HTML scraping for others.

This catches jobs BEFORE they appear on job boards — up to 48hrs earlier.
"""

import hashlib
import requests
from bs4 import BeautifulSoup
from config import RELEVANT_TITLE_KEYWORDS, BLACKLIST_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


# ============================================================
# COMPANY REGISTRY
# Add more companies here anytime!
# ============================================================
COMPANIES = [
    # --- LEVER ATS (clean JSON API) ---
    {"name": "Zepto",       "ats": "lever",      "slug": "zepto"},
    {"name": "CRED",        "ats": "lever",      "slug": "cred"},
    {"name": "Meesho",      "ats": "lever",      "slug": "meesho"},
    {"name": "Groww",       "ats": "lever",      "slug": "groww"},
    {"name": "Razorpay",    "ats": "lever",      "slug": "razorpay"},
    {"name": "BrowserStack","ats": "lever",      "slug": "browserstack"},
    {"name": "Postman",     "ats": "lever",      "slug": "postman"},
    {"name": "Chargebee",   "ats": "lever",      "slug": "chargebee"},

    # --- GREENHOUSE ATS (clean JSON API) ---
    {"name": "Swiggy",      "ats": "greenhouse", "slug": "swiggy"},
    {"name": "Dunzo",       "ats": "greenhouse", "slug": "dunzo"},
    {"name": "Freshworks",  "ats": "greenhouse", "slug": "freshworks"},
    {"name": "Clevertap",   "ats": "greenhouse", "slug": "clevertap"},
    {"name": "Darwinbox",   "ats": "greenhouse", "slug": "darwinbox"},

    # --- DIRECT SCRAPING ---
    {
        "name": "Zomato",
        "ats": "direct",
        "url": "https://www.zomato.com/careers",
        "job_selector": ".job-listing, [class*='job'], [class*='opening']",
        "title_selector": "h3, h4, [class*='title']",
        "link_selector": "a",
    },
    {
        "name": "PhonePe",
        "ats": "direct",
        "url": "https://www.phonepe.com/en/careers/",
        "job_selector": "[class*='job'], [class*='position'], [class*='opening']",
        "title_selector": "h3, h4, [class*='title']",
        "link_selector": "a",
    },
]

# PM-related keywords to filter career page results
PM_FILTER_KEYWORDS = [
    "product manager", "product management", "associate product",
    "apm", "product analyst", "product intern", "growth product",
    "junior product", "product owner", "project manager",
    "project coordinator", "project analyst", "program manager",
    "product lead", "product strategist",
]


def is_pm_role(title: str) -> bool:
    """Check if job title is PM/Project related."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in PM_FILTER_KEYWORDS)


def is_senior_role(title: str) -> bool:
    """Check if role is too senior for a fresher."""
    title_lower = title.lower()
    return any(kw in title_lower for kw in [kw.lower() for kw in BLACKLIST_KEYWORDS])


# ============================================================
# LEVER API
# ============================================================
def fetch_lever_jobs(company: dict) -> list:
    """Fetch jobs from Lever ATS public API."""
    jobs = []
    url = f"https://api.lever.co/v0/postings/{company['slug']}?mode=json"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        for posting in data:
            title = posting.get("text", "")
            if not is_pm_role(title) or is_senior_role(title):
                continue

            job_url = posting.get("hostedUrl", "")
            location = posting.get("categories", {}).get("location", "Not specified")
            job_id = "lever_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company["name"],
                "location": location,
                "url": job_url,
                "platform": f"Career Page 🏢"
            })

    except Exception as e:
        print(f"  ❌ Lever error for {company['name']}: {e}")

    return jobs


# ============================================================
# GREENHOUSE API
# ============================================================
def fetch_greenhouse_jobs(company: dict) -> list:
    """Fetch jobs from Greenhouse ATS public API."""
    jobs = []
    url = f"https://boards-api.greenhouse.io/v1/boards/{company['slug']}/jobs?content=true"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        job_list = data.get("jobs", [])

        for posting in job_list:
            title = posting.get("title", "")
            if not is_pm_role(title) or is_senior_role(title):
                continue

            job_url = posting.get("absolute_url", "")
            location = posting.get("location", {}).get("name", "Not specified")
            job_id = "greenhouse_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company["name"],
                "location": location,
                "url": job_url,
                "platform": f"Career Page 🏢"
            })

    except Exception as e:
        print(f"  ❌ Greenhouse error for {company['name']}: {e}")

    return jobs


# ============================================================
# DIRECT SCRAPING
# ============================================================
def fetch_direct_jobs(company: dict) -> list:
    """Scrape career pages directly via HTML."""
    jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(company["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select(company.get("job_selector", "[class*='job']"))

        for card in cards:
            title_el = card.select_one(company.get("title_selector", "h3"))
            link_el = card.select_one(company.get("link_selector", "a"))

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            if not is_pm_role(title) or is_senior_role(title):
                continue

            href = link_el.get("href", "") if link_el else ""
            if href.startswith("/"):
                base = "/".join(company["url"].split("/")[:3])
                job_url = base + href
            else:
                job_url = href or company["url"]

            job_id = "direct_" + hashlib.md5((company["name"] + title).encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company["name"],
                "location": "India",
                "url": job_url,
                "platform": "Career Page 🏢"
            })

    except Exception as e:
        print(f"  ❌ Direct scrape error for {company['name']}: {e}")

    return jobs


# ============================================================
# MAIN MONITOR
# ============================================================
def fetch_company_jobs(company: dict) -> list:
    """Route to correct fetcher based on ATS type."""
    ats = company.get("ats")
    if ats == "lever":
        return fetch_lever_jobs(company)
    elif ats == "greenhouse":
        return fetch_greenhouse_jobs(company)
    elif ats == "direct":
        return fetch_direct_jobs(company)
    return []


def run_career_pages_monitor():
    """Monitor all company career pages for PM roles."""
    print("🔍 Checking company career pages...")

    for company in COMPANIES:
        jobs = fetch_company_jobs(company)
        if jobs:
            print(f"  Found {len(jobs)} PM jobs at {company['name']}")

        for job in jobs:
            if is_job_seen(job["job_id"]):
                continue

            eligible, reason = scan_job(job)
            if not eligible:
                print(f"  ⏭️ Skipping (experience required): {job['title']} @ {job['company']}")
                save_job(**job)
                continue

            save_job(**job)
            print(f"🆕 New job: {job['title']} at {job['company']}")

            send_job_alert(
                platform=f"{job['platform']} — {job['company']}\n📋 {reason}",
                title=job["title"],
                company=job["company"],
                location=job["location"],
                url=job["url"],
                applied=False
            )
