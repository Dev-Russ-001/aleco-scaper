l
def scrape_aleco():
    # Gamitin ang cloudscraper para ligtas sa Cloudflare block
    scraper = cloudscraper.create_scraper(delay=10)
    
    try:
        print(f"Kinukuha ang data mula sa {TARGET_URL} gamit ang cloudscraper...")
        response = scraper.get(TARGET_URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hanapin ang lahat ng text o elements na naglalaman ng advisory keywords
            full_text = soup.get_text(separator='\n')
            
            if "POWER ADVISORY" in full_text:
                print("May nahanap na Power Advisory sa pahina!")
                chunks = full_text.split("POWER ADVISORY")
                if len(chunks) > 1:
                    latest_post = "POWER ADVISORY " + chunks[1][:400]
                    formatted = format_advisory(latest_post)
                    print("\n--- FORMATTED ADVISORY ---")
                    print(formatted)
            else:
                print("Walang nakitang POWER ADVISORY sa kasalukuyang HTML response.")
                # I-print ang ilang bahagi ng text para makita natin kung ano ang nasalo
                print(full_text[:500])
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Scraper Error: {e}")

if __name__ == "__main__":
    scrape_aleco()
