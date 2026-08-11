import os
import re
import json
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

FB_PAGE_URL = "https://m.facebook.com/albayelectric/posts/"

def scrape_facebook():
    with sync_playwright() as p:
        # Pinalakas natin ang browser configuration para magmukhang tao
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        
        # DEBUG: Print natin ang title ng page para malaman kung login page ba ito
        try:
            page.goto(FB_PAGE_URL, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(10000)
            
            print(f"DEBUG: Page Title: {page.title()}")
            
            # Kumuha ng screenshot para makita natin sa Actions Artifacts kung ano ang hitsura ng page
            page.screenshot(path="debug.png")
            print("DEBUG: Screenshot saved as debug.png")
            
            body_text = page.inner_text("body")
            
            # Check kung may "Log in" sa text
            if "Log in" in body_text or "Log In" in body_text:
                print("ERROR: Naka-redirect sa LOGIN PAGE. Hindi makapasok ang scraper.")
            
            pattern = re.compile(r'POWER ADVISORY|MAINTENANCE ADVISORY|INTERRUPTION', re.IGNORECASE)
            
            if pattern.search(body_text):
                print("SUCCESS: May nahanap na advisory sa text!")
                # ... (dito mo ilagay yung logic mo para sa save_to_supabase)
            else:
                print("FAILED: Walang nahanap na 'POWER ADVISORY' sa page.")
                
        except Exception as e:
            print(f"Scraper Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    scrape_facebook()
