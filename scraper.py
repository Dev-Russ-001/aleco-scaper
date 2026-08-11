import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

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
        
        # DEBUG: I-print ang kabuuang text para makita natin kung nasaan ang advisory
        full_text = soup.get_text(separator='\n')
        print("--- RAW TEXT START ---")
        print(full_text[:1000]) # Unang 1000 characters
        print("--- RAW TEXT END ---")
        
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_website()
