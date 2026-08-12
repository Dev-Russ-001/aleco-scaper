import os
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

# Supabase Credentials
SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

# Telegram Credentials
TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

# Ang iyong FetchRSS Feed Link
RSS_URL = "https://rss.app/feeds/XHUW4sV40A2meINV.xml"

def send_telegram_alert(formatted_message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": formatted_message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_existing_post_times():
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=post_time"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return [row.get('post_time') for row in res.json()]
    except Exception as e:
        print(f"Supabase fetch times error: {e}")
    return []

def save_to_supabase(advisory_text, post_datetime, image_url):
    url = f"{SUPABASE_URL}/rest/v1/advisories"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "substation": advisory_text, 
        "post_time": post_datetime,
        "image_url": image_url
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Supabase error: {e}")

def maintain_database_limit():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=id&order=post_time.asc"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 15:
                excess = len(data) - 15
                for i in range(excess):
                    oldest_id = data[i]['id']
                    requests.delete(f"{SUPABASE_URL}/rest/v1/advisories?id=eq.{oldest_id}", headers=headers)
    except Exception as e:
        print(f"Error maintaining limit: {e}")

@app.route("/")
def scrape_rss():
    try:
        print("Binabasa ang FetchRSS feed...")
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            return "OK", 200

        existing_times = get_existing_post_times()
        sorted_entries = sorted(
            feed.entries, 
            key=lambda x: x.get('published_parsed') or (9999, 12, 31, 23, 59, 59, 0, 0, 0), 
            reverse=True
        )
        
        new_posts = []
        for entry in sorted_entries[:15]:
            raw_content = entry.get('description', '') or entry.get('summary', '')
            published_parsed = entry.get('published_parsed')
            
            if published_parsed:
                dt = datetime(*published_parsed[:6]) + timedelta(hours=8)
                post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
                iso_post_time = dt.isoformat()
            else:
                dt = datetime.now()
                post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
                iso_post_time = dt.isoformat()

            soup_html = BeautifulSoup(raw_content, 'html.parser')
            img_tag = soup_html.find('img')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
            content = soup_html.get_text(separator='\n').strip()
            
            if not content and not image_url:
                continue

            if iso_post_time in existing_times:
                break 
            else:
                full_card_message = f"{content}\n\n🕒 Posted on: {post_date_str}"
                new_posts.append({
                    'full_card_message': full_card_message,
                    'iso_post_time': iso_post_time,
                    'post_date_str': post_date_str,
                    'image_url': image_url
                })

        if new_posts:
            for post in reversed(new_posts):
                save_to_supabase(post['full_card_message'], post['iso_post_time'], post['image_url'])
                telegram_notification = f"""⚡ALBAY UPDATE⚡
May bago pong post sa page:

🕒 Oras: {post['post_date_str']}
📝 Detalye: Power Advisory Tripping.
Bisitahin ang website: https://albaypowertripping.oneapp.dev/"""
                send_telegram_alert(telegram_notification)
            maintain_database_limit()
        
        return "OK", 200

    except Exception as e:
        print(f"Error sa scrape route: {e}")
        return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
