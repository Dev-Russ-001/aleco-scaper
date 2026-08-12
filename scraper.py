import os
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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
    """Kinukuha ang lahat ng post_time mula sa Supabase para masuri ang mga oras."""
    url = f"{SUPABASE_URL}/rest/v1/advisories?select=post_time"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            times = [row.get('post_time') for row in res.json()]
            print(f"Nakuha ang {len(times)} na existing timestamps mula sa Supabase.")
            return times
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
    # Isinama na natin ang image_url dito
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
    print("Binabasa ang FetchRSS feed...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Walang nahanap na entries sa RSS feed o mali ang link.")
        return

    existing_times = get_existing_post_times()

    sorted_entries = sorted(
        feed.entries, 
        key=lambda x: x.get('published_parsed') or (9999, 12, 31, 23, 59, 59, 0, 0, 0), 
        reverse=True
    )

    print(f"Sinusuri ang mga post batay sa oras (timestamp)...")
    
    new_posts = []
    for entry in sorted_entries[:15]:
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
        
        # Kunin ang Image URL mula sa post kung mayroon man
        img_tag = soup_html.find('img')
        image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

        content = soup_html.get_text(separator='\n').strip()
        
        if not content and not image_url:
            continue

        if iso_post_time in existing_times:
            print(f"-> Na-save na ang post na may oras na {post_date_str}. Humihinto na sa pag-check.")
            break 
        else:
            print(f"-> BAGONG POST NAKITA: {post_date_str} (May larawan: {'Oo' if image_url else 'Wala'})")
            full_card_message = f"{content}\n\n🕒 Posted on: {post_date_str}"
            new_posts.append({
                'content': content,
                'full_card_message': full_card_message,
                'iso_post_time': iso_post_time,
                'post_date_str': post_date_str,
                'image_url': image_url
            })

    if new_posts:
        print(f"\nMay kabuuang {len(new_posts)} bagong post ang idadagdag.")
        for post in reversed(new_posts):
            save_to_supabase(post['full_card_message'], post['iso_post_time'], post['image_url'])
            
            telegram_notification = f"""⚡ALBAY UPDATE⚡
May bago pong post sa page:

🕒 Oras: {post['post_date_str']}

📝 Detalye: Power Advisory Tripping - Date, Time and Affected Areas. 

Para sa buong detalye, bisitahin ang website: https://albaypowertripping.oneapp.dev/"""

            send_telegram_alert(telegram_notification)
        
        maintain_database_limit()
    else:
        print("Walang bagong post na nakita. Up-to-date na ang database.")

if __name__ == "__main__":
    scrape_rss()
