import cloudscraper
from bs4 import BeautifulSoup

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def scrape_website():
    # Ang cloudscraper ang bahala sa pag-solve ng Cloudflare challenge
    scraper = cloudscraper.create_scraper(delay=10) 
    
    try:
        print(f"Kinukuha ang data mula sa {TARGET_URL} gamit ang cloudscraper...")
        response = scraper.get(TARGET_URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n')
            
            print("--- NAKUHA ANG CONTENT ---")
            # I-print ang unang 1000 characters para makita natin kung gumana
            print(text[:1000])
            print("--- END OF CONTENT ---")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_website()
