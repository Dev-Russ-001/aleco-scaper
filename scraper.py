import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SUPABASE_URL = "https://gnagimmnoutjjaifdgvq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImduYWdpbW1ub3V0amphaWZkZ3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYyNTg2MzcsImV4cCI6MjEwMTgzNDYzN30.y4nlEnr9-ZRUkKn7CgQ8d6am7viNYkLB3RdELwqyXjs"

TG_BOT_TOKEN = "8922919303:AAENx7PehTDQOoYIb2kya7L1laXDcgQtiUE"
TG_CHAT_ID = "@AlbayPowerUpdates"

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def send_telegram_alert(advisory_text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    current_time_str = datetime.now().strftime('%B %d, %Y %I:%M %p')
    message = f"""⚡ALBAY POWER ADVISORY⚡
May bago pong update sa ating mga area:

📝 Detalye:
{advisory_text}

🕒 Oras ng Post: {current_time_str}

Para sa iba pang updates, bisitahin ang aming website: {TARGET_URL}"""

    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message
    }
    try:
        res = requests.post(url, json=payload)
        print(f"Telegram status: {res.status_code}")
    except Exception as e:
        print(f"Error sa Telegram: {e}")

def clean_text(raw_text):
    lines = raw_text.split('\n')
    cleaned_lines = []
    
    # Mga salitang dapat balewalain dahil menu items lang ito at hindi totoong advisory
    menu_blockers = [
        'ERC NOTICE AND ORDER', 'CAREER OPPORTUNITIES', 'EVENTS HIGHLIGHTS', 
        'EVENT ACTIVITY ANNOUNCEMENT', 'FEATURED EVENTS', 'PHOTO GALLERY',
        'Home', 'About Us', 'MGA ADVISORY'
    ]
    
    capturing = False
    for line in lines:
        line_str = line.strip()
        
        # Hanapin kung saan magsisimula ang totoong advisory content
        if any(keyword in line_str.upper() for keyword in ['POWER ADVISORY', 'MAINTENANCE ADVISORY', 'SUBSTATION AFFECTED']):
            capturing = True
            
        if capturing:
            # Kung menu item ang sumunod, tigilan na ang pagkuha
            if any(blocker in line_str.upper() for blocker in menu_blockers) and len(cleaned_lines) > 3:
                break
            if line_str and line_str != '.' and not line_str.isdigit():
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

def scrape_website():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"Kinukuha ang data mula sa {TARGET_URL}...")
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Error: HTTP status code {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator='\n')
        
        cleaned_chunk = clean_text(page_text)
        
        if len(cleaned_chunk) > 30:
            print("May nahanap na malinis na advisory sa website!")
            print(cleaned_chunk)
            save_to_supabase(cleaned_chunk)
            send_telegram_alert(cleaned_chunk)
        else:
            print("Walang nahanap na sapat na detalye ng advisory.")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_website()
