import hashlib
import requests
from bs4 import BeautifulSoup
from config import JOB_KEYWORDS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


def fetch_unstop_jobs(keyword: str) -> list:
    """
    Scrape Unstop for PM/Project management fresher roles.
    """
    jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://unstop.com/",
    }

    params = {
        "search": keyword,
        "oppType": "jobs,internship",
        "page": 1,
        "size": 20,
        "sort": "recent",
    }

    try:
        response = requests.get(
            "https://unstop.com/api/public/opportunity/search-result",
            params=params,
            headers=headers,
            timeout=15
        )
        data = response.json()
        items = data.get("data", {}).get("data", [])

        for item in items:
            title = item.get("title", "")
            org = item.get("organisation", {})
            company = org.get("name", "Unknown") if org else "Unknown"
            location = item.get("location", "Not specified") or "Work From Home"
            slug = item.get("public_url", "") or str(item.get("id", ""))
            job_url = f"https://unstop.com/{slug}" if slug else "https://unstop.com"

            job_id = "unstop_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "platform": "Unstop"
            })

    except Exception as e:
        print(f"❌ Error fetching Unstop jobs: {e}")

    return jobs


def run_unstop_monitor():
    """Monitor Unstop for new fresher PM/Project jobs."""
    print("🔍 Checking Unstop for new jobs...")

    for keyword in JOB_KEYWORDS:
        jobs = fetch_unstop_jobs(keyword)
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
                platform=f"Unstop 🟠\n📋 {reason}",
                title=job["title"],
                company=job["company"],
                location=job["location"],
                url=job["url"],
                applied=False
            )
