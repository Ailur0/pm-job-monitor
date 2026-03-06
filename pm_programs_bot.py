"""
pm_programs_bot.py
------------------
Monitors APM Programs, PM Fellowships, and Rotational Programs
specifically designed for freshers/new grads.

These are HIGH VALUE opportunities — structured programs with
mentorship, training, and clear career paths.
"""

import hashlib
import requests
from bs4 import BeautifulSoup
from database import is_job_seen, save_job
from telegram_alerts import send_job_alert
from jd_scanner import scan_job


# ============================================================
# KNOWN APM / PM FELLOWSHIP PROGRAMS
# These are checked directly via their career pages or APIs
# ============================================================
PM_PROGRAMS = [

    # --- INDIAN COMPANIES ---
    {
        "name": "Razorpay APM Program",
        "company": "Razorpay",
        "url": "https://jobs.lever.co/razorpay",
        "ats": "lever",
        "search_terms": ["apm", "associate product", "product fellow"],
    },
    {
        "name": "Swiggy APM Program",
        "company": "Swiggy",
        "url": "https://boards-api.greenhouse.io/v1/boards/swiggy/jobs",
        "ats": "greenhouse",
        "search_terms": ["apm", "associate product", "product fellow", "product trainee"],
    },
    {
        "name": "Meesho PM Fellowship",
        "company": "Meesho",
        "url": "https://jobs.lever.co/meesho",
        "ats": "lever",
        "search_terms": ["apm", "associate product", "product fellow", "product intern"],
    },
    {
        "name": "CRED APM",
        "company": "CRED",
        "url": "https://jobs.lever.co/cred",
        "ats": "lever",
        "search_terms": ["apm", "associate product", "product manager"],
    },
    {
        "name": "Groww APM",
        "company": "Groww",
        "url": "https://jobs.lever.co/groww",
        "ats": "lever",
        "search_terms": ["apm", "associate product", "product intern"],
    },
    {
        "name": "Zepto PM Program",
        "company": "Zepto",
        "url": "https://jobs.lever.co/zepto",
        "ats": "lever",
        "search_terms": ["product manager", "associate product", "apm"],
    },
    {
        "name": "Zomato APM",
        "company": "Zomato",
        "url": "https://www.zomato.com/careers",
        "ats": "direct",
        "search_terms": ["apm", "associate product", "product fellow"],
    },
    {
        "name": "PhonePe PM Program",
        "company": "PhonePe",
        "url": "https://www.phonepe.com/en/careers/",
        "ats": "direct",
        "search_terms": ["apm", "associate product", "product intern"],
    },
    {
        "name": "Freshworks PM Program",
        "company": "Freshworks",
        "url": "https://boards-api.greenhouse.io/v1/boards/freshworks/jobs",
        "ats": "greenhouse",
        "search_terms": ["apm", "associate product", "product fellow", "rotational"],
    },

    # --- GLOBAL COMPANIES WITH INDIA PRESENCE ---
    {
        "name": "Google APM Program",
        "company": "Google",
        "url": "https://careers.google.com/jobs/results/?q=associate+product+manager&location=India",
        "ats": "direct_google",
        "search_terms": ["associate product manager", "apm"],
    },
    {
        "name": "Microsoft PM Internship",
        "company": "Microsoft",
        "url": "https://jobs.careers.microsoft.com/global/en/search?q=product+manager+intern&lc=India",
        "ats": "direct",
        "search_terms": ["product manager intern", "apm"],
    },
    {
        "name": "Amazon PMT Internship",
        "company": "Amazon",
        "url": "https://www.amazon.jobs/en/search?base_query=product+manager+intern&loc_query=India",
        "ats": "direct",
        "search_terms": ["product manager", "apm", "rotational"],
    },

    # --- PROGRAM-SPECIFIC PAGES ---
    {
        "name": "Flipkart GCA Program",
        "company": "Flipkart",
        "url": "https://www.flipkartcareers.com/#!/joblist",
        "ats": "direct",
        "search_terms": ["product", "gca", "graduate", "rotational"],
    },
    {
        "name": "Paytm APM",
        "company": "Paytm",
        "url": "https://paytm.com/careers",
        "ats": "direct",
        "search_terms": ["apm", "associate product", "product intern"],
    },
]

# Also monitor these general program keywords on Internshala/Naukri/LinkedIn
PROGRAM_KEYWORDS = [
    "APM program",
    "associate product manager program",
    "PM fellowship",
    "product management fellowship",
    "product management trainee program",
    "rotational product manager",
    "RPM program",
    "product manager new grad",
    "product management graduate program",
    "product management bootcamp hiring",
    "product management apprenticeship",
]


def fetch_lever_program(program: dict) -> list:
    """Fetch from Lever API and filter by program search terms."""
    jobs = []
    slug = program["url"].replace("https://jobs.lever.co/", "").strip("/")

    try:
        response = requests.get(
            f"https://api.lever.co/v0/postings/{slug}?mode=json",
            timeout=15
        )
        data = response.json()

        for posting in data:
            title = posting.get("text", "").lower()
            if not any(term in title for term in program["search_terms"]):
                continue

            job_url = posting.get("hostedUrl", "")
            location = posting.get("categories", {}).get("location", "India")
            job_id = "program_lever_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": posting.get("text", ""),
                "company": program["company"],
                "location": location,
                "url": job_url,
                "platform": "Career Page 🏢",
                "program_name": program["name"],
            })

    except Exception as e:
        print(f"  ❌ Error fetching {program['name']}: {e}")

    return jobs


def fetch_greenhouse_program(program: dict) -> list:
    """Fetch from Greenhouse API and filter by program search terms."""
    jobs = []
    slug = program["url"].replace(
        "https://boards-api.greenhouse.io/v1/boards/", ""
    ).replace("/jobs", "").strip("/")

    try:
        response = requests.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
            timeout=15
        )
        data = response.json()

        for posting in data.get("jobs", []):
            title = posting.get("title", "").lower()
            if not any(term in title for term in program["search_terms"]):
                continue

            job_url = posting.get("absolute_url", "")
            location = posting.get("location", {}).get("name", "India")
            job_id = "program_gh_" + hashlib.md5(job_url.encode()).hexdigest()[:10]

            jobs.append({
                "job_id": job_id,
                "title": posting.get("title", ""),
                "company": program["company"],
                "location": location,
                "url": job_url,
                "platform": "Career Page 🏢",
                "program_name": program["name"],
            })

    except Exception as e:
        print(f"  ❌ Error fetching {program['name']}: {e}")

    return jobs


def fetch_direct_program(program: dict) -> list:
    """Scrape career page directly."""
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(program["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        # Check if any program keywords appear on the page
        found_terms = [term for term in program["search_terms"] if term in text]
        if not found_terms:
            return jobs

        # Find job links
        links = soup.select("a[href*='job'], a[href*='career'], a[href*='position'], a[href*='apply']")
        for link in links:
            link_text = link.get_text(strip=True).lower()
            if any(term in link_text for term in program["search_terms"]):
                href = link.get("href", "")
                if href.startswith("/"):
                    base = "/".join(program["url"].split("/")[:3])
                    job_url = base + href
                else:
                    job_url = href or program["url"]

                job_id = "program_direct_" + hashlib.md5(
                    (program["company"] + link_text).encode()
                ).hexdigest()[:10]

                jobs.append({
                    "job_id": job_id,
                    "title": link.get_text(strip=True),
                    "company": program["company"],
                    "location": "India",
                    "url": job_url,
                    "platform": "Career Page 🏢",
                    "program_name": program["name"],
                })

    except Exception as e:
        print(f"  ❌ Error fetching {program['name']}: {e}")

    return jobs


def run_pm_programs_monitor():
    """Monitor all PM programs for new openings."""
    print("🔍 Checking PM Programs & Fellowships...")

    for program in PM_PROGRAMS:
        ats = program.get("ats")

        if ats == "lever":
            jobs = fetch_lever_program(program)
        elif ats == "greenhouse":
            jobs = fetch_greenhouse_program(program)
        else:
            jobs = fetch_direct_program(program)

        if jobs:
            print(f"  Found {len(jobs)} openings at {program['name']}")

        for job in jobs:
            if is_job_seen(job["job_id"]):
                continue

            eligible, reason = scan_job(job)
            if not eligible:
                print(f"  ⏭️ Skipping (experience required): {job['title']}")
                save_job(**job)
                continue

            save_job(**job)
            program_name = job.get("program_name", "PM Program")
            print(f"🎯 New program opening: {job['title']} — {program_name}")

            # Programs get a special alert format
            send_job_alert(
                platform=f"🎯 *PM PROGRAM* — {program_name}\n📋 {reason}",
                title=job["title"],
                company=job["company"],
                location=job["location"],
                url=job["url"],
                applied=False
            )
