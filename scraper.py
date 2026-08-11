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

PLUGIN_URL = "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Falbayelectric&tabs=timeline&width=340&height=500&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true"

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

def check_if_exists(control_no):
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=substation&substation=il.*{control_no}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200 and len(res.json()) > 0:
            return True
    except Exception as e:
        print(f"Error checking Supabase: {e}")
    return False

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
    control_no = f"UIAUG{datetime.now().strftime('%Y')}-{datetime.now().strftime('%H%M%S')}"

    sub_match = re.search(r'SUBSTATION\s*AFFECTED\s*[:|-]\s*(.*?)(?=REASON|DATE|$)', raw_text, re.IGNORECASE | re.DOTALL)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*?)(?=DATE|Control|$)', raw_text, re.IGNORECASE | re.DOTALL)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*?)(?=\n|$)', raw_text, re.IGNORECASE)
    if date_match:
        date_val = date_match.group(1).strip()
        
    ctrl_match = re.search(r'(UIAUG\w+)', raw_text, re.IGNORECASE)
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

def scrape_facebook_plugin():
    scraper = cloudscraper.create_scraper(delay=10)
    
    try:
        print("Kumukunekta sa Facebook Page Plugin...")
        response = scraper.get(PLUGIN_URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            full_text = soup.get_text(separator='\n')
            
            if "POWER ADVISORY" in full_text:
                chunks = full_text.split("POWER ADVISORY")
                print(f"May nakitang {len(chunks)-1} na post sa feed.")
                
                # Suriin ang hanggang 3 pinakabagong post
                limit = min(4, len(chunks))
                for i in range(1, limit):
                    latest_post = "POWER ADVISORY " + chunks[i][:600]
                    formatted, ctrl_no = format_advisory(latest_post)
                    
                    # I-check kung nakasulat na sa database para hindi ma-double
                    if not check_if_exists(ctrl_no):
                        print(f"\n[BAGONG POST NAKITA]: {ctrl_no}")
                        print(formatted)
                        save_to_supabase(formatted)
                        send_telegram_alert(formatted)
                    else:
                        print(f"Naka-save na sa database ang post na may Control No: {ctrl_no}")
            else:
                print("Walang kasalukuyang POWER ADVISORY sa plugin feed.")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_facebook_plugin()
