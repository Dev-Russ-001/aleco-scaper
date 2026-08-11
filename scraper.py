import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
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
        "text": formatted_message,
        "parse_mode": "Markdown" # Optional kung gagamitin ang custom unicode fonts
    }
    # Kung sakaling magka-issue sa Markdownparse dahil sa special unicode, pwede ring tanggalin ang parse_mode
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

def parse_advisory(raw_text):
    # Default values kung sakaling may makaligtaan
    substation = "N/A"
    reason = "N/A"
    date_val = datetime.now().strftime('%B %d, %Y')
    control_no = f"UI{datetime.now().strftime('%b%Y').upper()}-001"

    # Pag-extract gamit ang regex kung makita ang mga labels sa website text
    sub_match = re.search(r'SUBSTATION\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if date_match:
        date_val = date_match.group(1).strip()

    ctrl_match = re.search(r'Control\s*Number\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if ctrl_match:
        control_no = ctrl_match.group(1).strip()

    # Kung walang specific labels pero may nakuha tayong text block, gawin nating reason o substation
    if substation == "N/A" and len(raw_text) > 20:
        substation = "Albay Area Feeder"
        reason = raw_text[:100]

    # Eksaktong pormat na gusto mo kasama ang mga estilong Unicode fonts
    formatted_message = f"""‼𝙋O𝙒𝙀𝙍 𝘼𝘿𝙑𝙄𝙎𝙊𝙍𝙔
𝑺𝑼𝑩𝑺𝑻𝑨𝑻𝑰𝑶𝑵 𝑨𝑭𝑭𝑬𝑪𝑻𝑬𝑫: {substation}
𝑹𝑬𝑨𝑺𝑶𝑵: {reason}
𝑫𝑨𝑻𝑬: {date_val}
𝘾𝙤𝙣𝙩𝙧𝙤𝙡 𝙉𝙪𝙢1𝙗𝙚𝙧: {control_no}

𝐑𝐄𝐌𝐈𝐍𝐃𝐄𝐑: All works may be finished ahead of schedule and power may be restored earlier than planned and/or announced. 
For safety purposes, please ALWAYS CONSIDER our lines as ENERGIZED.
𝙉𝙤𝙩𝙚: An unscheduled service disruption is in effect, necessary to facilitate the coop’s ongoing technical work. We are sorry for any inconvenience caused"""

    return formatted_message

def scrape_website():
    scraper = cloudscraper.create_scraper(delay=10)
    
    try:
        print(f"Kinukuha ang data mula sa {TARGET_URL} gamit ang cloudscraper...")
        response = scraper.get(TARGET_URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            found = False
            for tag in soup.find_all(['p', 'div', 'span', 'td', 'article']):
                text = tag.get_text(separator=' ', strip=True)
                if any(kw in text.upper() for kw in ['POWER', 'INTERRUPTION', 'ADVISORY', 'FEEDER', 'SUBSTATION']):
                    if len(text) > 30:
                        final_message = parse_advisory(text)
                        print("May nahanap na advisory, ipinapadala...")
                        print(final_message)
                        save_to_supabase(final_message)
                        send_telegram_alert(final_message)
                        found = True
                        break
            
            if not found:
                print("Walang direktang advisory block na natagpuan.")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_website()
