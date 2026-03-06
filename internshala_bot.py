import hashlib
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job

# Only alert jobs posted within this many hours
MAX_JOB_AGE_HOURS = 24


def parse_posted_date(date_text: str) -> datetime | None:
    """
    Parse Internshala's posted date text into a datetime.
    Examples: 'Posted 2 hours ago', 'Posted today', 'Posted 1 day ago', 'Posted 3 days ago'
    Returns None if unparseable (treat as recent to be safe).
    """
    if not date_text:
        return None

    text = date_text.lower().strip()
    now = datetime.now()

    if "just now" in text or "today" in text or "hour" in text or "minute" in text:
        return now  # Very recent

    if "1 day ago" in text or "yesterday" in text:
        return now - timedelta(days=1)

    # "2 days ago", "3 days ago" etc.
    import re
    match = re.search(r"(\d+)\s+day", text)
    if match:
        days = int(match.group(1))
        return now - timedelta(days=days)

    # "1 week ago" etc — definitely old
    if "week" in text or "month" in text:
        return now - timedelta(days=30)

    return None  # Unknown — treat as recent


def is_recently_posted(date_text: str, max_hours: int = MAX_JOB_AGE_HOURS) -> bool:
    """Returns True if job was posted within max_hours."""
    posted_at = parse_posted_date(date_text)
    if posted_at is None:
        return True  # Unknown date — let it through
    age = datetime.now() - posted_at
    return age.total_seconds() / 3600 <= max_hours


def fetch_internshala_jobs(keyword: str) -> list:
    """
    Scrape Internshala for new fresher jobs matching keyword.
    Only returns jobs posted within MAX_JOB_AGE_HOURS.
    """
    jobs = []
    keyword_slug = keyword.replace(" ", "-")
    url = f"https://internshala.com/jobs/{keyword_slug}-jobs"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.select(".individual_internship")

        for card in job_cards:
            try:
                title_el = card.select_one(".job-title-href, .profile")
                company_el = card.select_one(".company_name, .company-name")
                location_el = card.select_one(".location_link, .locations-td")
                link_el = card.select_one("a.job-title-href, a.view_detail_button")

                # --- DATE FILTER ---
                # Internshala shows posted date in these elements
                date_el = card.select_one(
                    ".posted-by-container span, "
                    ".status-inactive, "
                    "[class*='posted'], "
                    ".d-none"
                )
                date_text = date_el.get_text(strip=True) if date_el else ""

                # Also check the full card text for date hints
                card_text = card.get_text(" ", strip=True).lower()
                for phrase in ["posted today", "posted just now", "hours ago",
                               "minutes ago", "days ago", "day ago", "week ago"]:
                    if phrase in card_text:
                        date_text = phrase
                        break

                if not is_recently_posted(date_text):
                    print(f"  📅 Skipping old posting: {title_el.get_text(strip=True) if title_el else 'Unknown'} ({date_text})")
                    continue

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                location = location_el.get_text(strip=True) if location_el else "Not specified"
                job_url = "https://internshala.com" + link_el.get("href", "")

                job_id = "internshala_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "platform": "Internshala",
                    "date_text": date_text or "unknown"
                })

            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

    except Exception as e:
        print(f"❌ Error fetching Internshala jobs: {e}")

    return jobs


def run_internshala_monitor(auto_apply: bool = False):
    """Monitor Internshala for new fresher PM jobs and send alerts."""
    print("🔍 Checking Internshala for new jobs...")

    for keyword in JOB_KEYWORDS:
        jobs = fetch_internshala_jobs(keyword)
        print(f"  Found {len(jobs)} recent jobs for '{keyword}'")

        for job in jobs:
            if is_job_seen(job["job_id"]):
                continue

            # Title relevance check
            title_lower = job["title"].lower()
            if not any(kw in title_lower for kw in RELEVANT_TITLE_KEYWORDS):
                print(f"  ⏭️ Skipping (not PM-relevant): {job['title']}")
                save_job(**job)
                continue

            # JD experience check
            eligible, reason = scan_job(job)
            if not eligible:
                print(f"  ⏭️ Skipping (experience required): {job['title']}")
                save_job(**job)
                continue

            save_job(**job)
            print(f"🆕 New fresher-eligible job: {job['title']} at {job['company']}")

            send_job_alert(
                platform=f"Internshala\n📋 {reason}",
                title=job["title"],
                company=job["company"],
                location=job["location"],
                url=job["url"],
                applied=False
            )
