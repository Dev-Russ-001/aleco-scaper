import cloudscraper
from bs4 import BeautifulSoup
import re
from datetime import datetime

TARGET_URL = "https://web.alecoinc.com.ph/index.php"

def format_advisory(raw_text):
    substation = "Albay Area Feeder"
    reason = "Maintenance/Repair Work"
    date_val = datetime.now().strftime('%B %d, %Y')
    control_no = f"UIAUG{datetime.now().strftime('%Y')}-001"

    sub_match = re.search(r'SUBSTATION\s*AFFECTED\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if sub_match:
        substation = sub_match.group(1).strip()

    reas_match = re.search(r'REASON\s*[:|-]\s*(.*)', raw_text, re.IGNORECASE)
    if reas_match:
        reason = reas_match.group(1).strip()

    date_match = re.search(r'DATE\s*[:|-]\s*(.*)', raw_text, raw_text)
    if date_match:
        date_val = date_match.group(1).strip()

    formatted_message = f"""‼𝙋𝙊𝙒𝙀𝙍 𝘼𝘿𝙑𝙄𝑺𝙊𝙍𝙔
𝑺𝑼𝑩𝑺𝑻𝑨𝑻𝑰𝑶𝑵 𝑨𝑭𝑭𝑬𝑪𝑻𝑬𝑫: {substation}
𝑹𝑬𝑨𝑺𝑶𝑵: {reason}
𝑫𝑨𝑻𝑬: {date_val}
𝘾𝙤𝙣𝙩𝙧𝙤𝙡 𝙉𝙪𝙢𝙗𝙚𝙧: {control_no}

𝐑𝐄𝐌𝐈𝐍𝐃𝐄𝐑: All works may be finished ahead of schedule and power may be restored earlier than planned and/or announced. 
For safety purposes, please ALWAYS CONSIDER our lines as ENERGIZED.
𝙉𝙤𝙩𝙚: An unscheduled service disruption is in effect, necessary to facilitate the coop’s ongoing technical work. We are sorry for any inconvenience caused"""

    return formatted_message

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
