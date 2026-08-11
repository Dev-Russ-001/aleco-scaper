import cloudscraper
from bs4 import BeautifulSoup

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def scrape_aleco():
    scraper = cloudscraper.create_scraper(delay=10)
    
    try:
        print(f"Kinukuha ang data mula sa {TARGET_URL}...")
        response = scraper.get(TARGET_URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("\n--- MGA NAKATAGONG IFRAME SA WEBSITE ---")
            found_iframe = False
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                print(f"Iframe link: {src}")
                if 'facebook.com' in src:
                    print(f"-> Nahanap ang Facebook Plugin URL: {src}")
                    found_iframe = True
            
            if not found_iframe:
                print("Walang direktang Facebook iframe, maaaring kinakarga ito gamit ang JavaScript.")
                
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_aleco()
