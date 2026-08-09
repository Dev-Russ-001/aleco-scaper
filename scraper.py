import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = "https://hook.eu1.make.com/ys71tgwopbgnfogxguktq3cuiftud9l9"
FB_PAGE_URL = "https://m.facebook.com/share/1EjbKqSETH/"

def scrape_facebook():
    post_text = "Walang nakitang post."
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(FB_PAGE_URL, timeout=60000)
            page.wait_for_timeout(5000)
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
