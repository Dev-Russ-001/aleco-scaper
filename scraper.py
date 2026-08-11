import os
import re
import requests
import feedparser
import unicodedata
from datetime import datetime

# Supabase Credentials
SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

# Telegram Credentials
TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

# Ang iyong RSS Feed Link
RSS_URL = "https://rss.app/feeds/XHUW4sV40A2meINV.xml"

def send_telegram_alert(formatted_message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": formatted_message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def check_if_exists(control_no):
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=substation&substation=il.*{control_no}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and len(res.json()) > 0:
            return True
    except Exception as e:
        print(f"Supabase check error: {e}")
    return False

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
    # Linisin at i-normalize ang unicode characters para mabasa nang maayos ng regex
    clean_text = unicodedata.normalize('NFKD', raw_text)
    
    substation = "Albay Area Feeder"
    reason = "Maintenance/Repair Work"
    date_val = datetime.now().strftime('%B %d, %Y')
    control_no = f"EIAUG{datetime.now().strftime('%Y')}-{datetime.now().strftime('%H%M%S')}"

    sub_match = re.search(r'SUBSTATION\s*AFFECTED\s*[:|-]\s*(.*?)(?=REASON|DATE|$)', clean_text, re.IGNORECASE | re.DOTALL)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*?)(?=DATE|Control|$)', clean_text, re.IGNORECASE | re.DOTALL)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*?)(?=\n|Time|Control|$)', clean_text, re.IGNORECASE | re.DOTALL)
    if date_match:
        date_val = date_match.group(1).strip()
        
    ctrl_match = re.search(r'Control\s*Number\s*[:|-]\s*([A-Za-z0-9-]+)', clean_text, re.IGNORECASE)
    if ctrl_match:
        control_no = ctrl_match.group(1).strip()

    formatted_message = f"""‼𝙋O𝙒𝙀𝙍 𝘼𝘿𝙑𝙄𝑺𝙊𝙍𝙔
𝑺𝑼𝑩𝑺𝑻𝑨𝑻𝑰𝑶𝑵 𝑨𝑭𝑭𝑬𝑪𝑻𝑬𝑫: {substation}
𝑹𝑬𝑨𝑺𝑶𝑵: {reason}
𝑫𝑨𝑻𝑬: {date_val}
𝘾𝙤𝙣𝙩𝙧𝙤𝙡 𝙉𝙪𝙢𝙗𝙚𝙧: {control_no}

𝐑𝐄𝐌𝐈𝐍𝐃𝐄𝐑: All works may be finished ahead of schedule and power may be restored earlier than planned and/or announced. 
For safety purposes, please ALWAYS CONSIDER our lines as ENERGIZED.
𝙉𝙤𝙩𝙚: An unscheduled service disruption is in effect, necessary to facilitate the coop’s ongoing technical work. We are sorry for any inconvenience caused"""
    return formatted_message, control_no

def scrape_rss():
    print("Binabasa ang RSS feed...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Walang nahanap na entries sa RSS feed o mali ang link.")
        return

    print(f"May nakitang {len(feed.entries)} na post sa RSS feed.")
    
    for entry in feed.entries[:3]:
        content = entry.get('description', '') or entry.get('summary', '')
        
        # I-normalize ang buong content para pantay na masuri
        normalized_content = unicodedata.normalize('NFKD', content).upper()
        
        if "ADVISORY" in normalized_content or "SUBSTATION" in normalized_content:
            formatted, ctrl_no = format_advisory(content)
            
            if not check_if_exists(ctrl_no):
                print(f"\n[BAGONG ADVISORY NAKITA]: {ctrl_no}")
                print(formatted)
                save_to_supabase(formatted)
                send_telegram_alert(formatted)
            else:
                print(f"Naka-save na sa database ang post na may Control No: {ctrl_no}")
        else:
            print("May post sa feed pero hindi ito Power Advisory.")

if __name__ == "__main__":
    scrape_rss()
