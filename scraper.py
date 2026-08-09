import os
import json
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = "https://hook.eu1.make.com/ys71tgwopbgnfogxguktq3cuiftud9l9"
# Ginawang mobile version para tugma sa cookies na kinuha mo
FB_PAGE_URL = "https://m.facebook.com/share/1EjbKqSETH/"
COOKIES_JSON = os.environ.get("FB_COOKIES", "[]")

def scrape_facebook():
    post_text = "Walang nakitang post."
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Naglagay tayo ng mobile user-agent para maging tugma sa mobile cookies
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        
        try:
            cookies = json.loads(COOKIES_JSON)
            if cookies:
                context.add_cookies(cookies)
        except Exception as e:
            print(f"Error loading cookies: {e}")
            
        page = context.new_page()
        try:
            page.goto(FB_PAGE_URL, timeout=60000)
            page.wait_for_timeout(6000)
            post_text = page.inner_text("body")[:1500]
        except Exception as e:
            post_text = f"Error: {str(e)}"
        
        browser.close()
        
        payload = {
            "substation": post_text,
            "date": "2026-08-10",
            "postime": "Live Update"
        }
        
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Sent status: {response.status_code}")

if __name__ == "__main__":
    scrape_facebook()
