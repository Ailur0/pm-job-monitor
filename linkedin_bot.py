import hashlib
import requests
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, JOB_LOCATIONS, BLACKLIST_KEYWORDS, PRIORITY_KEYWORDS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


def fetch_linkedin_jobs(keyword: str, location: str) -> list:
    """
    Scrape LinkedIn public job search for PM roles.
    Uses public search endpoint (no login required for listing).
    """
    jobs = []

    params = {
        "keywords": keyword,
        "location": location,
        "f_E": "1,2",        # Entry level + Internship
        "f_TPR": "r3600",    # Posted in last 1 hour (r3600 = 3600 seconds)
        "sortBy": "DD",      # Sort by date
    }

    url = "https://www.linkedin.com/jobs/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.select("div.job-search-card, li.jobs-search-results__list-item")

        for card in job_cards:
            try:
                title_el = card.select_one("h3.base-search-card__title, .job-card-list__title")
                company_el = card.select_one("h4.base-search-card__subtitle, .job-card-container__company-name")
                location_el = card.select_one("span.job-search-card__location, .job-card-container__metadata-item")
                link_el = card.select_one("a.base-card__full-link, a.job-card-list__title")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                location_text = location_el.get_text(strip=True) if location_el else location
                job_url = link_el.get("href", "").split("?")[0] if link_el else ""

                job_id = "linkedin_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "url": job_url,
                    "platform": "LinkedIn"
                })

            except Exception as e:
                print(f"Error parsing LinkedIn card: {e}")
                continue

    except Exception as e:
        print(f"❌ Error fetching LinkedIn jobs: {e}")

    return jobs


def run_linkedin_monitor():
    """Monitor LinkedIn for new PM jobs across all locations."""
    print("🔍 Checking LinkedIn for new PM jobs...")

    for keyword in JOB_KEYWORDS:
        for location in JOB_LOCATIONS:
            jobs = fetch_linkedin_jobs(keyword, location)
            print(f"  Found {len(jobs)} jobs for '{keyword}' in {location}")

            for job in jobs:
                if is_job_seen(job["job_id"]):
                    continue

                # Check blacklist
                title_lower = job["title"].lower()
                if any(bl.lower() in title_lower for bl in BLACKLIST_KEYWORDS):
                    print(f"  ⏭️ Skipping (blacklisted): {job['title']}")
                    continue

                # Title relevance check
                if not any(kw in title_lower for kw in RELEVANT_TITLE_KEYWORDS):
                    print(f"  ⏭️ Skipping (not PM-relevant): {job['title']}")
                    save_job(**job)
                    continue

                # Check if high priority
                is_priority = any(p.lower() in title_lower for p in PRIORITY_KEYWORDS)

                save_job(**job)

                # Scan JD for experience requirements
                eligible, reason = scan_job(job)
                if not eligible:
                    print(f"  ⏭️ Skipping (experience required): {job['title']}")
                    continue

                print(f"{'🔥' if is_priority else '🆕'} Fresher-eligible: {job['title']} at {job['company']}")

                send_job_alert(
                    platform="LinkedIn 🔵" + (" 🔥 PRIORITY" if is_priority else "") + f"\n📋 {reason}",
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    url=job["url"],
                    applied=False
                )


