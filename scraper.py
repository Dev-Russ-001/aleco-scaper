import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

FB_PAGE_URL = "https://m.facebook.com/albayelectric/posts/"

def scrape_facebook_http():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    cookies_dict = {}
    cookies_env = os.getenv("FB_COOKIES")
    if cookies_env:
        try:
            cookie_list = json.loads(cookies_env)
            for cookie in cookie_list:
                cookies_dict[cookie['name']] = cookie['value']
        except Exception as e:
            print(f"Error parsing cookies: {e}")

    try:
        print("Nagpapadala ng HTTP request sa Facebook...")
        response = requests.get(FB_PAGE_URL, headers=headers, cookies=cookies_dict, timeout=30)
        
        print(f"HTTP Status Code: {response.status_code}")
        
        # I-print ang unang 300 characters ng nakuha nating HTML para makita natin kung na-block o login wall
        print(f"RESPONSE PREVIEW:\n{response.text[:300]}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator='\n')
        
        pattern = re.compile(r'POWER ADVISORY|MAINTENANCE ADVISORY|INTERRUPTION', re.IGNORECASE)
        
        if pattern.search(page_text):
            print("May nahanap na advisory!")
        else:
            print("Walang nahanap na advisory pattern sa response text.")
            
    except Exception as e:
        print(f"HTTP Scraper Error: {e}")

if __name__ == "__main__":
    scrape_facebook_http()
