import hashlib
import requests
from config import JOB_KEYWORDS, JOB_LOCATIONS, RELEVANT_TITLE_KEYWORDS
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


def fetch_naukri_jobs(keyword: str, location: str = "") -> list:
    """
    Fetch Naukri jobs using their internal search API.
    More reliable than HTML scraping.
    """
    jobs = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.naukri.com/",
        "appid": "109",
        "systemid": "Naukri",
    }

    params = {
        "noOfResults": 20,
        "urlType": "search_by_keyword",
        "searchType": "adv",
        "keyword": keyword,
        "location": location,
        "experience": 0,
        "sort": "1",  # Sort by date (newest first)
        "pageNo": 1,
    }

    try:
        response = requests.get(
            "https://www.naukri.com/jobapi/v3/search",
            params=params,
            headers=headers,
            timeout=15
        )
        data = response.json()
        job_list = data.get("jobDetails", [])

        for job in job_list:
            title = job.get("title", "")
            company = job.get("companyName", "Unknown")
            placeholders = job.get("placeholders", [])
            location_text = placeholders[0].get("label", location) if placeholders else location
            job_url = job.get("jdURL", "")
            if job_url and not job_url.startswith("http"):
                job_url = "https://www.naukri.com" + job_url

            job_id = "naukri_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location_text,
                "url": job_url,
                "platform": "Naukri"
            })

    except Exception as e:
        print(f"❌ Error fetching Naukri jobs: {e}")

    return jobs


def run_naukri_monitor():
    """Monitor Naukri for new fresher PM jobs and send alerts."""
    print("🔍 Checking Naukri for new jobs...")

    for keyword in JOB_KEYWORDS:
        for location in JOB_LOCATIONS:
            jobs = fetch_naukri_jobs(keyword, location)
            print(f"  Found {len(jobs)} jobs for '{keyword}' in {location}")

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
                print(f"🆕 New fresher-eligible PM job: {job['title']} at {job['company']}")

                send_job_alert(
                    platform=f"Naukri\n📋 {reason}",
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    url=job["url"],
                    applied=False
                )
