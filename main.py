"""
============================================================
  PM JOB MONITOR BOT — Main Runner
  Monitors Naukri, Internshala & LinkedIn every 5 mins
  for Product Management roles (fresher/intern/APM)
  Sends instant Telegram alerts — you apply manually
============================================================

SETUP INSTRUCTIONS:
1. Install dependencies:
   pip install requests beautifulsoup4 playwright schedule
   playwright install chromium

2. Fill in your details in config.py:
   - Your name, email, phone
   - Telegram bot token + chat ID (for alerts)
   - Your login credentials for each platform

3. Set up Telegram alerts (takes 2 mins):
   - Open Telegram → search @BotFather → /newbot → copy token
   - Search @userinfobot → start → copy your ID
   - Paste both in config.py

4. Run:
   python main.py

5. To run 24/7 on a free server (Oracle Cloud):
   nohup python main.py > bot.log 2>&1 &
============================================================
"""

import schedule
import time
from datetime import datetime
from database import init_db, get_all_applications, get_today_apply_count
from internshala_bot import run_internshala_monitor
from naukri_bot import run_naukri_monitor
from linkedin_bot import run_linkedin_monitor
from telegram_alerts import send_telegram_alert
from config import (
    CHECK_INTERVAL_MINUTES,
    MONITOR_INTERNSHALA,
    MONITOR_NAUKRI,
    MONITOR_LINKEDIN,
    AUTO_APPLY_INTERNSHALA,
    JOB_KEYWORDS,
    JOB_LOCATIONS
)


def run_all_monitors():
    """Run all enabled job monitors."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*55}")
    print(f"🤖 Job Monitor Running — {now}")
    print(f"   Keywords : {', '.join(JOB_KEYWORDS[:3])}...")
    print(f"   Locations: {', '.join(JOB_LOCATIONS)}")
    print(f"{'='*55}")

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
    print(f"\n✅ Cycle complete | Alerts today: {count} | Next in {CHECK_INTERVAL_MINUTES} mins\n")


def send_daily_summary():
    """Send a daily summary to Telegram every morning."""
    apps = get_all_applications()
    total = len(apps)
    message = f"📊 *Daily PM Job Summary*\n\n🔍 Total PM roles found: {total}\n\nKeep going! 🚀"
    send_telegram_alert(message)


def print_stats():
    """Print recent job alerts to console."""
    print("\n📊 Recent Job Alerts:")
    print("-" * 70)
    apps = get_all_applications()
    if not apps:
        print("  No jobs found yet. Bot is running...")
    else:
        for app in apps[:10]:
            title, company, platform, status, seen_at, _ = app
            print(f"  [{platform}] {title} @ {company} — {seen_at}")
    print("-" * 70 + "\n")


if __name__ == "__main__":
    print("🚀 PM Job Monitor Bot Starting...\n")

    # Initialize database
    init_db()

    # Send startup alert to Telegram
    send_telegram_alert(
        f"🚀 *PM Job Monitor Started!*\n\n"
        f"Monitoring: Naukri, Internshala, LinkedIn\n"
        f"Keywords: {', '.join(JOB_KEYWORDS[:4])}\n"
        f"Locations: {', '.join(JOB_LOCATIONS)}\n"
        f"Checking every {CHECK_INTERVAL_MINUTES} mins ⏰"
    )

    # Run immediately on start
    run_all_monitors()
    print_stats()

    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(run_all_monitors)
    schedule.every(1).hours.do(print_stats)
    schedule.every().day.at("09:00").do(send_daily_summary)

    print(f"⏰ Bot is live! Checking every {CHECK_INTERVAL_MINUTES} mins.")
    print(f"📱 You'll get Telegram alerts for every new PM role found.")
    print(f"Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)
