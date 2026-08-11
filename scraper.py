from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
import requests
import time

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Ito ang magic: ginagawa nating "tao" ang browser
        stealth_sync(page)
        
        print("Naglo-load ng page gamit ang Stealth Browser...")
        page.goto(TARGET_URL, wait_until="networkidle")
        
        # Hintayin ng konti para ma-solve ang challenge
        time.sleep(10) 
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator='\n')
        
        # Debug: I-print ang text para makita natin kung nakalusot na
        print("--- CONTENT START ---")
        print(text[:1000]) 
        print("--- CONTENT END ---")
        
        # Dito mo ilalagay ang logic mo para sa Telegram/Supabase pag nakalusot na
        browser.close()

if __name__ == "__main__":
    scrape()
