"""
run_once.py — Used by GitHub Actions. Runs one full cycle and exits.
"""

import os
import sys
from datetime import datetime
from database import init_db, get_today_apply_count
from internshala_bot import run_internshala_monitor
from naukri_bot import run_naukri_monitor
from linkedin_bot import run_linkedin_monitor
from unstop_bot import run_unstop_monitor
from wellfound_bot import run_wellfound_monitor
from career_pages_bot import run_career_pages_monitor
from pm_programs_bot import run_pm_programs_monitor
from config import (
    MONITOR_INTERNSHALA, MONITOR_NAUKRI, MONITOR_LINKEDIN,
    MONITOR_UNSTOP, MONITOR_WELLFOUND, MONITOR_CAREER_PAGES,
    MONITOR_PM_PROGRAMS, AUTO_APPLY_INTERNSHALA,
    JOB_KEYWORDS, JOB_LOCATIONS, TELEGRAM_BOT_TOKEN,
)


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"🤖 PM Job Monitor — {now}")
    print(f"   Keywords : {', '.join(JOB_KEYWORDS[:3])}...")
    print(f"   Locations: {', '.join(JOB_LOCATIONS)}")
    print(f"{'='*55}\n")

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ Telegram not configured.")
        sys.exit(1)

    init_db()

    if MONITOR_INTERNSHALA:
        try:
            run_internshala_monitor(auto_apply=AUTO_APPLY_INTERNSHALA)
        except Exception as e:
            print(f"❌ Internshala error: {e}")

    if MONITOR_NAUKRI:
        try:
            run_naukri_monitor()
        except Exception as e:
            print(f"❌ Naukri error: {e}")

    if MONITOR_LINKEDIN:
        try:
            run_linkedin_monitor()
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")

    if MONITOR_UNSTOP:
        try:
            run_unstop_monitor()
        except Exception as e:
            print(f"❌ Unstop error: {e}")

    if MONITOR_WELLFOUND:
        try:
            run_wellfound_monitor()
        except Exception as e:
            print(f"❌ Wellfound error: {e}")

    if MONITOR_CAREER_PAGES:
        try:
            run_career_pages_monitor()
        except Exception as e:
            print(f"❌ Career pages error: {e}")

    if MONITOR_PM_PROGRAMS:
        try:
            run_pm_programs_monitor()
        except Exception as e:
            print(f"❌ PM programs error: {e}")

    count = get_today_apply_count()
    print(f"\n✅ Cycle complete | Alerts sent today: {count}")


if __name__ == "__main__":
    main()
