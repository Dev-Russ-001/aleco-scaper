import os
import re
import json
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

# Supabase Credentials
SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

# Telegram Credentials
TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

# Gamitin ang mobile version ng tamang page para hindi ma-block at madaling makuha ang posts
FB_PAGE_URL = "https://m.facebook.com/albayelectric/posts/"

def send_telegram_alert(advisory_text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    current_time_str = datetime.now().strftime('%B %d, %Y %I:%M %p')
    message = f"""⚡ALBAY POWER ADVISORY⚡
May bago pong update sa ating mga area:

📝 Detalye:
{advisory_text}

🕒 Oras ng Post: {current_time_str}

Para sa iba pang updates, bisitahin ang aming website: https://albaypowertripping.oneapp.dev/"""

    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Telegram status: {res.status_code}")
    except Exception as e:
        print(f"Error sa Telegram: {e}")

def clean_facebook_text(raw_text):
    match = re.search(r'POWER ADVISORY|MAINTENANCE ADVISORY|INTERRUPTION', raw_text, re.IGNORECASE)
    if match:
        raw_text = raw_text[match.start():]
        
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    stop_words = ['All reactions', 'Like', 'Comment', 'Share', 'See more', 'Send message', 'Full Story']
    
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str == '.' or line_str.isdigit():
            continue
            
        if any(word in line_str for word in stop_words) and len(cleaned_lines) > 5:
            break
            
        cleaned_lines.append(line_str)
            
    return "\n".join(cleaned_lines)

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

def scrape_facebook():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Gagamit ng Mobile User-Agent para sa mas simpleng layout at iwas-block
        context = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 667}
        )
        
        # Basahin ang cookies mula sa GitHub Secrets kung nakalagay
        cookies_env = os.getenv("FB_COOKIES")
        if cookies_env:
            try:
                cookies = json.loads(cookies_env)
                context.add_cookies(cookies)
                print("Cookies successfully loaded!")
            except Exception as e:
                print(f"Error loading cookies: {e}")

        page = context.new_page()
        try:
            page.goto(FB_PAGE_URL, timeout=60000)
            page.wait_for_timeout(8000)
            
            body_text = page.inner_text("body")
            
            pattern = re.compile(r'POWER ADVISORY|MAINTENANCE ADVISORY|INTERRUPTION', re.IGNORECASE)
            
            if pattern.search(body_text):
                lines = body_text.split('\n')
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        chunk = "\n".join(lines[max(0, i):min(len(lines), i+30)])
                        if "Log in" not in chunk and "Create new account" not in chunk:
                            cleaned_chunk = clean_facebook_text(chunk)
                            if len(cleaned_chunk) > 30:
                                print("May nahanap na malinis na advisory!")
                                save_to_supabase(cleaned_chunk)
                                send_telegram_alert(cleaned_chunk)
                                break
            else:
                print("Walang nahanap na advisory pattern sa text.")
                
        except Exception as e:
            print(f"Scraper Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    scrape_facebook()
