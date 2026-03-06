"""
run_once.py
-----------
Used by GitHub Actions. Runs one full monitor cycle and exits.
GitHub Actions triggers this every 5 minutes via cron schedule.

The SQLite database is committed back to the repo after each run
so seen jobs are remembered across runs.
"""

import os
import sys
from datetime import datetime
from database import init_db, get_today_apply_count
from internshala_bot import run_internshala_monitor
from naukri_bot import run_naukri_monitor
from linkedin_bot import run_linkedin_monitor
from config import (
    MONITOR_INTERNSHALA,
    MONITOR_NAUKRI,
    MONITOR_LINKEDIN,
    AUTO_APPLY_INTERNSHALA,
    JOB_KEYWORDS,
    JOB_LOCATIONS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*55}")
    print(f"🤖 PM Job Monitor — {now}")
    print(f"   Keywords : {', '.join(JOB_KEYWORDS[:3])}...")
    print(f"   Locations: {', '.join(JOB_LOCATIONS)}")
    print(f"{'='*55}\n")

    # Validate Telegram config
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in GitHub Secrets.")
        sys.exit(1)

    # Init DB (creates jobs.db if not exists)
    init_db()

    # Run all monitors once
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

    count = get_today_apply_count()
    print(f"\n✅ Cycle complete | Alerts sent today: {count}")


if __name__ == "__main__":
    main()
