import hashlib
import requests
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


def fetch_wellfound_jobs(keyword: str) -> list:
    """
    Scrape Wellfound (AngelList) for PM startup roles.
    """
    jobs = []

    keyword_slug = keyword.replace(" ", "-").lower()
    url = f"https://wellfound.com/jobs?q={keyword.replace(' ', '+')}&role=product-manager"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.select("[class*='JobListing'], [data-test='JobListing'], div[class*='job-listing']")

        for card in job_cards:
            try:
                title_el = card.select_one("a[class*='title'], h2, h3, [class*='JobTitle']")
                company_el = card.select_one("[class*='company'], [class*='startup-link']")
                location_el = card.select_one("[class*='location'], [class*='Location']")
                link_el = card.select_one("a[href*='/jobs/']")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                location = location_el.get_text(strip=True) if location_el else "Remote/India"
                href = link_el.get("href", "") if link_el else ""
                job_url = f"https://wellfound.com{href}" if href.startswith("/") else href or url

                job_id = "wellfound_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "platform": "Wellfound"
                })

            except Exception as e:
                print(f"Error parsing Wellfound card: {e}")
                continue

    except Exception as e:
        print(f"❌ Error fetching Wellfound jobs: {e}")

    return jobs


def run_wellfound_monitor():
    """Monitor Wellfound for startup PM roles."""
    print("🔍 Checking Wellfound for new jobs...")

    # Wellfound is best for specific PM keywords
    pm_keywords = [
        "product manager", "associate product manager",
        "product analyst", "growth product manager"
    ]

    for keyword in pm_keywords:
        jobs = fetch_wellfound_jobs(keyword)
        print(f"  Found {len(jobs)} jobs for '{keyword}'")

        for job in jobs:
            if is_job_seen(job["job_id"]):
                continue

            title_lower = job["title"].lower()
            if not any(kw in title_lower for kw in RELEVANT_TITLE_KEYWORDS):
                print(f"  ⏭️ Skipping (not relevant): {job['title']}")
                save_job(**job)
                continue

            eligible, reason = scan_job(job)
            if not eligible:
                print(f"  ⏭️ Skipping (experience required): {job['title']}")
                save_job(**job)
                continue

            save_job(**job)
            print(f"🆕 New job: {job['title']} at {job['company']}")

            send_job_alert(
                platform=f"Wellfound 🟡\n📋 {reason}",
                title=job["title"],
                company=job["company"],
                location=job["location"],
                url=job["url"],
                applied=False
            )
