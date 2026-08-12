import os
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
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

def save_to_supabase(advisory_text, post_datetime):
    url = f"{SUPABASE_URL}/rest/v1/advisories"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {"substation": advisory_text, "post_time": post_datetime}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Supabase error: {e}")

def maintain_database_limit():
    """Sinisiguro na laging 15 posts lang ang maximum na nakalagay sa database/site."""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=id&order=post_time.asc"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 15:
                excess = len(data) - 15
                print(f"Database limit exceeded. Deleting {excess} oldest post(s)...")
                for i in range(excess):
                    oldest_id = data[i]['id']
                    delete_url = f"{SUPABASE_URL}/rest/v1/advisories?id=eq.{oldest_id}"
                    requests.delete(delete_url, headers=headers)
    except Exception as e:
        print(f"Error maintaining limit: {e}")

def scrape_rss():
    print("Binabasa ang RSS feed...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Walang nahanap na entries sa RSS feed o mali ang link.")
        return

    sorted_entries = sorted(
        feed.entries, 
        key=lambda x: x.get('published_parsed', (0,0,0,0,0,0)), 
        reverse=True
    )

    print(f"Sinusuri ang mga post mula sa pinakabago...")
    
    new_posts = []
    for entry in sorted_entries[:10]:
        raw_content = entry.get('description', '') or entry.get('summary', '')
        
        published_parsed = entry.get('published_parsed')
        if published_parsed:
            dt_utc = datetime(*published_parsed[:6])
            dt = dt_utc + timedelta(hours=8)
            post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
            iso_post_time = dt.isoformat()
        else:
            dt = datetime.now()
            post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
            iso_post_time = dt.isoformat()

        soup_html = BeautifulSoup(raw_content, 'html.parser')
        content = soup_html.get_text(separator='\n').strip()
        
        if not content:
            continue

        # Kung ang post na ito ay nasa database na, hihinto na ang buong loop
        if check_if_exists(content):
            print(f"Naka-save na sa database ang post na ito. Humihinto na sa pag-check ng mga mas lumang post.")
            break 
        else:
            full_card_message = f"{content}\n\n🕒 Oras ng Post: {post_date_str}"
            new_posts.append({
                'content': content,
                'full_card_message': full_card_message,
                'iso_post_time': iso_post_time,
                'post_date_str': post_date_str
            })

    # Kung may mga bagong post, baligtarin natin ang pagkakasunod (reversed)
    # para ang pinakabagong post ang huling ma-send at mapunta sa pinaka-ibaba ng Telegram chat.
    if new_posts:
        for post in reversed(new_posts):
            print(f"\n[BAGONG POST NAKITA]: {post['post_date_str']}")
            save_to_supabase(post['full_card_message'], post['iso_post_time'])
            
            telegram_notification = f"""⚡ALBAY UPDATE⚡
May bago pong post sa page:

🕒 Oras: {post['post_date_str']}

📝 Detalye: Power Advisory Tripping - Date, Time and Affected Areas. 

Para sa buong detalye, bisitahin ang website: https://albaypowertripping.oneapp.dev/"""

            send_telegram_alert(telegram_notification)
        
        # Linisin ang database pagkatapos mai-save lahat ng bago para laging 15 lang
        maintain_database_limit()

if __name__ == "__main__":
    scrape_rss()
