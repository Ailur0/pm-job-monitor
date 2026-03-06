import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_alert(message: str):
    """Send an instant alert to your Telegram."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print(f"[ALERT - No Telegram configured] {message}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"✅ Telegram alert sent!")
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")


def send_job_alert(platform: str, title: str, company: str, location: str, url: str, applied: bool = False):
    """Send a formatted job alert."""
    status = "✅ *AUTO-APPLIED*" if applied else "🔔 *NEW JOB — Apply Now!*"

    # Flag PPO roles
    ppo_flag = ""
    if any(kw in title.lower() for kw in ["ppo", "pre placement", "pre-placement"]):
        ppo_flag = "\n💼 *PPO OPPORTUNITY*"
    elif any(kw in platform.lower() for kw in ["ppo", "pre placement"]):
        ppo_flag = "\n💼 *PPO OPPORTUNITY*"

    message = f"""
{status}{ppo_flag}

📌 *{title}*
🏢 {company}
📍 {location}
🌐 {platform}

🔗 [View Job]({url})
"""
    send_telegram_alert(message)
