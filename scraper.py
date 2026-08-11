import os
import re
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

# Supabase Credentials
SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

# Telegram Credentials
TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def send_telegram_alert(formatted_message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": formatted_message
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Telegram status: {res.status_code}")
    except Exception as e:
        print(f"Error sa Telegram: {e}")

def save_to_supabase(advisory_text):
    url = f"{SUPABASE_URL}/rest/v1/advisories"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "substation": advisory_text,
        "post_time": datetime.now().isoformat()
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Supabase save status: {res.status_code}")
    except Exception as e:
        print(f"Error sa Supabase: {e}")

def format_advisory(raw_text):
    substation = "Albay Area Feeder"
    reason = "Maintenance/Repair Work"
    date_val = datetime.now().strftime('%B %d, %Y')
    control_no = f"UIAUG{datetime.now().strftime('%Y')}-001"

    # Pag-extract ng mga detalye mula sa post text
    sub_match = re.search(r'SUBSTATION\s*AFFECTED\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if date_match:
        date_val = date_match.group(1).strip()

    # Eksaktong pormat na gusto mo
    formatted_message = f"""‼𝙋𝙊𝙒𝙀𝙍 𝘼𝘿𝙑𝙄𝙎𝙊𝙍𝙔
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
        browser = p.chromium.launch(headless=True)
        page = browser.new_context().new_page()
        
        print(f"Binubuksan ang {TARGET_URL}...")
        page.goto(TARGET_URL, timeout=60000)
        
        # Hihintayin nating mag-load ang Facebook widget iframe (mga 7 seconds)
        print("Naghihintay na mag-load ang Facebook widget...")
        page.wait_for_timeout(7000)
        
        # Kunin ang buong text na naka-render sa page kabilang ang widget
        full_text = page.inner_text("body")
        
        browser.close()
        
        # Hanapin ang POWER ADVISORY sa loob ng nakuha nating text
        if "POWER ADVISORY" in full_text:
            print("May nahanap na Power Advisory sa News Feed!")
            chunks = full_text.split("POWER ADVISORY")
            
            # Kunin ang pinakabagong post (unang chunk pagkatapos ng split)
            if len(chunks) > 1:
                latest_post = "POWER ADVISORY " + chunks[1][:400] # Kunin ang unang 400 characters ng post
                formatted = format_advisory(latest_post)
                
                print("\n--- FORMATTED ADVISORY ---")
                print(formatted)
                print("--------------------------\n")
                
                save_to_supabase(formatted)
                send_telegram_alert(formatted)
        else:
            print("Walang nakitang 'POWER ADVISORY' sa kasalukuyang news feed.")

if __name__ == "__main__":
    scrape_aleco()
