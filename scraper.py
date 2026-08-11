import os
import re
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def send_telegram_alert(formatted_message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": formatted_message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def save_to_supabase(advisory_text):
    url = f"{SUPABASE_URL}/rest/v1/advisories"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {"substation": advisory_text, "post_time": datetime.now().isoformat()}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Supabase error: {e}")

def format_advisory(raw_text):
    substation = "Albay Area Feeder"
    reason = "Maintenance/Repair Work"
    date_val = datetime.now().strftime('%B %d, %Y')
    control_no = f"UIAUG{datetime.now().strftime('%Y')}-001"

    sub_match = re.search(r'SUBSTATION\s*AFFECTED\s*[:|-]\s*(.*?)(?=REASON|DATE|$)', raw_text, re.IGNORECASE | re.DOTALL)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*?)(?=DATE|Control|$)', raw_text, re.IGNORECASE | re.DOTALL)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*?)(?=\n|$)', raw_text, re.IGNORECASE)
    if date_match:
        date_val = date_match.group(1).strip()

    formatted_message = f"""‼𝙋O𝙒𝙀𝙍 𝘼𝘿𝙑𝙄𝑺𝙊𝙍𝙔
𝑺𝑼𝑩𝑺𝑻𝑨𝑻𝑰𝑶𝑵 𝑨𝑭𝑭𝑬𝑪𝑻𝑬𝑫: {substation}
𝑹𝑬𝑨𝑺𝑶𝑵: {reason}
𝑫𝑨𝑻𝑬: {date_val}
𝘾𝙤𝙣𝙩𝙧𝙤𝙡 𝙉𝙪𝙢𝙗𝙚𝙧: {control_no}

𝐑𝐄𝐌𝐈𝐍𝐃𝐄𝐑: All works may be finished ahead of schedule and power may be restored earlier than planned and/or announced. 
For safety purposes, please ALWAYS CONSIDER our lines as ENERGIZED.
𝙉𝙤𝙩𝙚: An unscheduled service disruption is in effect, necessary to facilitate the coop’s ongoing technical work. We are sorry for any inconvenience caused"""
    return formatted_message

def scrape_aleco():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Binubuksan ang website gamit ang Playwright browser...")
        page.goto(TARGET_URL, timeout=60000)
        
        print("Naghihintay mag-load ang mga widgets at iframes...")
        page.wait_for_timeout(10000)
        
        # Kunin ang text ng buong main page
        full_text = page.evaluate("() => document.body.innerText")
        
        # Silipin din ang loob ng mga Facebook iframe kung nasaan ang aktwal na posts
        for frame in page.frames:
            try:
                frame_text = frame.evaluate("() => document.body.innerText")
                if frame_text:
                    full_text += "\n" + frame_text
            except Exception:
                pass

        browser.close()

        if "POWER ADVISORY" in full_text:
            print("Tagumpay! May nahanap na Power Advisory.")
            chunks = full_text.split("POWER ADVISORY")
            if len(chunks) > 1:
                latest_post = "POWER ADVISORY " + chunks[1][:600]
                formatted = format_advisory(latest_post)
                print("\n--- FINAL FORMATTED ADVISORY ---")
                print(formatted)
                
                save_to_supabase(formatted)
                send_telegram_alert(formatted)
        else:
            print("Wala pa ring nakitang POWER ADVISORY sa buong pahina o mga iframes.")

if __name__ == "__main__":
    scrape_aleco()
