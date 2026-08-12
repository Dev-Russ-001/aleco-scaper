import os
import requests
import feedparser
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

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

def check_if_exists(content_snippet):
    # I-check kung naka-save na sa database ang unang bahagi ng post para maiwasan ang duplicate
    encoded_snippet = urllib.parse.quote(content_snippet[:50])
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=substation&substation=il.*{encoded_snippet}"
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

def scrape_rss():
    print("Binabasa at ino-order ang RSS feed (Lahat ng post)...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Walang nahanap na entries sa RSS feed o mali ang link.")
        return

    # I-sort ang entries mula pinakabago hanggang pinakaluma
    sorted_entries = sorted(
        feed.entries, 
        key=lambda x: x.get('published_parsed', (0,0,0,0,0,0)), 
        reverse=True
    )

    print(f"May nakitang {len(sorted_entries)} na post sa RSS feed.")
    
    # Suriin ang mga pinakabagong post
    for entry in sorted_entries[:5]:
        raw_content = entry.get('description', '') or entry.get('summary', '')
        
        published_parsed = entry.get('published_parsed')
        if published_parsed:
            dt = datetime(*published_parsed[:6])
            post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
        else:
            post_date_str = entry.get('published', datetime.now().strftime('%B %d, %Y'))

        soup_html = BeautifulSoup(raw_content, 'html.parser')
        content = soup_html.get_text(separator='\n').strip()
        
        if not content:
            continue

        # Buong nilalaman ng post na isasave sa website/Supabase
        full_card_message = f"{content}\n\n🕒 Oras ng Post: {post_date_str}"

        # Maikling snippet para sa Telegram notification
        snippet = content[:120] + "..." if len(content) > 120 else content
        telegram_notification = f"""⚡ALBAY UPDATE⚡
May bago pong post sa page:

📝 {snippet}

🕒 Oras: {post_date_str}

Para sa buong detalye, bisitahin ang website: https://albaypowertripping.oneapp.dev/"""

        if not check_if_exists(content):
            print(f"\n[BAGONG POST NAKITA]: {post_date_str}")
            save_to_supabase(full_card_message)
            send_telegram_alert(telegram_notification)
        else:
            print(f"Naka-save na sa database ang post na ito.")

if __name__ == "__main__":
    scrape_rss()
