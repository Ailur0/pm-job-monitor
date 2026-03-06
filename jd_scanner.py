"""
jd_scanner.py
-------------
Scrapes the full Job Description from a job URL and determines
if the role is genuinely open to freshers (0 experience).
"""

import re
import requests
from bs4 import BeautifulSoup


# ============================================================
# EXPERIENCE DISQUALIFIERS — skip job if any of these found
# ============================================================
EXPERIENCE_BLOCKLIST = [
    r"\b[2-9]\+?\s*years?\s*(of\s*)?(experience|exp)\b",
    r"\b1[0-9]\+?\s*years?\s*(of\s*)?(experience|exp)\b",
    r"\bminimum\s+[2-9]\s*years?\b",
    r"\bat\s+least\s+[2-9]\s*years?\b",
    r"\b[2-9]\s*-\s*[0-9]+\s*years?\s*(of\s*)?(experience|exp)\b",
    r"\b(2|3|4|5|6|7|8|9|10)\+\s*yrs\b",
    r"\bprior\s+work\s+experience\s+required\b",
    r"\bmust\s+have\s+[2-9]\s*years?\b",
]

# ============================================================
# FRESHER QUALIFIERS — confirms the role is for freshers
# ============================================================
FRESHER_ALLOWLIST = [
    r"\bfresher[s]?\b",
    r"\b0[\s-]*[–-][\s-]*1\s*year[s]?\b",
    r"\bno\s+experience\s+required\b",
    r"\bno\s+prior\s+experience\b",
    r"\bentry[\s-]level\b",
    r"\brecent\s+graduate[s]?\b",
    r"\bnewly\s+graduated\b",
    r"\b0\s+years?\s*(of\s*)?(experience|exp)\b",
    r"\bopen\s+to\s+fresher[s]?\b",
    r"\bwelcome\s+fresher[s]?\b",
    r"\binternship\b",
    r"\btrainee\b",
    r"\bapm\s+program\b",
    r"\bgraduate\s+program\b",
    r"\bcampus\s+hire\b",
    # PPO specific
    r"\bppo\b",
    r"\bpre[\s-]placement\s+offer\b",
    r"\bpre[\s-]placement\s+opportunity\b",
    r"\bfull[\s-]time\s+offer\b",
    r"\bconvert(ed|ible)?\s+to\s+full[\s-]time\b",
    r"\bintern.*full[\s-]time\b",
]


def fetch_jd_text(url: str) -> str:
    """
    Fetch and return the plain text of a job description page.
    Returns empty string if fetch fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Try to find the JD section specifically
        jd_selectors = [
            # Internshala
            ".internship_details", ".job-description", "#internship_details",
            # Naukri
            ".job-desc", ".dang-inner-html", ".jd-desc",
            # LinkedIn
            ".description__text", ".job-description",
            # Generic
            "[class*='description']", "[class*='job-detail']", "main", "article"
        ]

        for selector in jd_selectors:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator=" ", strip=True)
                if len(text) > 100:  # Valid JD should have substance
                    return text.lower()

        # Fallback: entire page text
        return soup.get_text(separator=" ", strip=True).lower()

    except Exception as e:
        print(f"    ⚠️ Could not fetch JD from {url}: {e}")
        return ""


def is_fresher_eligible(jd_text: str, job_title: str = "") -> tuple[bool, str]:
    """
    Analyse JD text and determine if the role is open to freshers.

    Returns:
        (is_eligible: bool, reason: str)
    """
    if not jd_text:
        # If we can't fetch JD, allow it through with a warning
        return True, "⚠️ Could not read JD — verify manually"

    # Step 1: Check for disqualifying experience requirements
    for pattern in EXPERIENCE_BLOCKLIST:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            snippet = jd_text[max(0, match.start()-30):match.end()+30].strip()
            return False, f"❌ Requires experience: '...{snippet}...'"

    # Step 2: Check for fresher-friendly signals
    for pattern in FRESHER_ALLOWLIST:
        match = re.search(pattern, jd_text, re.IGNORECASE)
        if match:
            snippet = jd_text[max(0, match.start()-20):match.end()+20].strip()
            return True, f"✅ Fresher-friendly: '...{snippet}...'"

    # Step 3: No clear signal either way — allow through with note
    return True, "⚠️ No experience requirement mentioned — looks okay"


def scan_job(job: dict) -> tuple[bool, str]:
    """
    Full pipeline: fetch JD → scan → return eligibility.

    Args:
        job: dict with at least 'url' and 'title' keys

    Returns:
        (is_eligible: bool, reason: str)
    """
    print(f"    🔎 Scanning JD: {job['title']} @ {job['company']}")
    jd_text = fetch_jd_text(job["url"])
    eligible, reason = is_fresher_eligible(jd_text, job.get("title", ""))
    print(f"    {reason}")
    return eligible, reason
