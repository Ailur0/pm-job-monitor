import hashlib
import requests
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


def fetch_internshala_jobs(keyword: str) -> list:
    """
    Scrape Internshala for new fresher jobs matching keyword.
    Returns list of job dicts.
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

        # Find job cards
        job_cards = soup.select(".individual_internship")

        for card in job_cards:
            try:
                title_el = card.select_one(".job-title-href, .profile")
                company_el = card.select_one(".company_name, .company-name")
                location_el = card.select_one(".location_link, .locations-td")
                link_el = card.select_one("a.job-title-href, a.view_detail_button")

                if not title_el or not link_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                location = location_el.get_text(strip=True) if location_el else "Not specified"
                job_url = "https://internshala.com" + link_el.get("href", "")

                # Generate unique ID from URL
                job_id = "internshala_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "platform": "Internshala"
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
        print(f"  Found {len(jobs)} jobs for '{keyword}'")

        for job in jobs:
            if is_job_seen(job["job_id"]):
                continue

            # Title relevance check — must be PM-related
            title_lower = job["title"].lower()
            if not any(kw in title_lower for kw in RELEVANT_TITLE_KEYWORDS):
                print(f"  ⏭️ Skipping (not PM-relevant): {job['title']}")
                save_job(**job)
                continue

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

