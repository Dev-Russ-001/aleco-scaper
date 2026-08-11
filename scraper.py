import cloudscraper
from bs4 import BeautifulSoup

PLUGIN_URL = "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Falbayelectric&tabs=timeline&width=340&height=500&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true"

def test_scraper():
    scraper = cloudscraper.create_scraper(delay=10)
    response = scraper.get(PLUGIN_URL)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text(separator='\n')
        
        print("--- LAHAT NG TEKSTO MULA SA FB PLUGIN ---")
        print(full_text[:1500]) # I-print ang unang 1500 characters
        print("--- WAKAS ---")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_scraper()
