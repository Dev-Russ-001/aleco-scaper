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

def clean_facebook_text(raw_text):
    """Tinatanggal ang mga hindi kailangang Facebook UI elements tulad ng reactions, likes, at comments"""
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    # Mga salitang gusto nating i-filter out o alisin
    junk_patterns = [
        r'All reactions', r'Like', r'Comment', r'Share', r'See more', 
        r'Albay Electric Cooperative', r'who can comment', r'1d', r'2d', r'3d', r'4d', r'5d', r'6d', r'1w',
        r'ago', r'At'
    ]
    
    for line in lines:
        line_str = line.strip()
        # Huwag isali ang blangko o kaya ay purong numero lang (karaniwan ay reaction counts)
        if not line_str or line_str.isdigit():
            continue
            
        # Suriin kung naglalaman ng Facebook junk words
        is_junk = False
        for pattern in junk_patterns:
            if re.search(pattern, line_str, re.IGNORECASE):
                is_junk = True
                break
                
        if not is_junk:
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
    posts_found = []
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
            
            body_text = page.inner_text("body")
            
            pattern = re.compile(r'POWER ADVISORY|INTERRUPTION|MAINTENANCE|ADVISORY', re.IGNORECASE)
            
            if pattern.search(body_text):
                lines = body_text.split('\n')
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        chunk = "\n".join(lines[max(0, i-2):min(len(lines), i+25)])
                        if "Log in" not in chunk and "Create new account" not in chunk:
                            # Linisin ang text gamit ang ating cleanup function
                            cleaned_chunk = clean_facebook_text(chunk)
                            if len(cleaned_chunk) > 30 and cleaned_chunk not in posts_found:
                                posts_found.append(cleaned_chunk)
                                if len(posts_found) >= 5: # Kunin muna ang pinakabagong 5 malinis na posts
                                    break
        except Exception as e:
            print(f"Scraper Error: {e}")
        
        browser.close()
        
        if posts_found:
            print(f"May nahanap na {len(posts_found)} malinis na advisories!")
            for post in posts_found:
                save_to_supabase(post)
        else:
            print("Walang nahanap na advisory.")

if __name__ == "__main__":
    scrape_facebook()
