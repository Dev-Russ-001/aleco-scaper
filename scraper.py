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

FB_PAGE_URL = "https://www.facebook.com/share/1EjbKqSETH/"

def send_telegram_alert(advisory_text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    current_time_str = datetime.now().strftime('%B %d, %Y %I:%M %p')
    message = f"""⚡ALBAY POWER ADVISORY⚡
May bago pong update sa ating mga area:

📝 Detalye: Power Advisory Affected Areas 

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

def clean_post_text(raw_text):
    # Hanapin kung saan nagsisimula ang POWER ADVISORY at hiwain mula roon pababa para mawala ang FB header
    match = re.search(r'❗️❗️POWER ADVISORY|NGCP POWER INTERRUPTION', raw_text, re.IGNORECASE)
    if match:
        raw_text = raw_text[match.start():]
        
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    # Mga salitang tatanggalin sa hulihan o gitna (mga reaksyon at share ng FB)
    stop_words = ['All reactions', 'Like', 'Comment', 'Share', 'See more', 'Send message']
    
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str == '.':
            continue
            
        # Kung umabot na sa reaction parts ng post, itigil na ang pagbasa para hindi sumama ang dumi
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
        context = browser.new_context(
            user_agent="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        try:
            page.goto(FB_PAGE_URL, timeout=60000)
            page.wait_for_timeout(8000)
            
            # Kunin ang bawat hiwalay na post container sa Facebook feed
            posts = page.locator('div[role="article"]').all()
            latest_advisory = None
            
            for post in posts:
                post_text = post.inner_text()
                if re.search(r'POWER ADVISORY|MAINTENANCE ADVISORY|INTERRUPTION', post_text, re.IGNORECASE):
                    cleaned = clean_post_text(post_text)
                    if len(cleaned) > 40: # Siguraduhing buo at may laman
                        latest_advisory = cleaned
                        break # Kunin lamang ang pinakabagong post at itigil na
            
            if latest_advisory:
                print("May nahanap na buo at malinis na advisory!")
                save_to_supabase(latest_advisory)
                send_telegram_alert(latest_advisory)
            else:
                print("Walang nahanap na advisory.")
                
        except Exception as e:
            print(f"Scraper Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    scrape_facebook()

