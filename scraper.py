import os
import re
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = "https://hook.eu1.make.com/ys71tgwopbgnfogxguktq3cuiftud9l9"
FB_PAGE_URL = "https://www.facebook.com/share/1EjbKqSETH/"

def scrape_facebook():
    post_text = "Walang nakitang post."
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Nagpanggap tayo bilang Googlebot para lusutan ang login wall ng public page
        context = browser.new_context(
            user_agent="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        try:
            page.goto(FB_PAGE_URL, timeout=60000)
            page.wait_for_timeout(6000)
            
            # 1. Kunin ang mga post gamit ang article/post containers ng Facebook
            articles = page.locator('article, [role="article"], div.story_body_container').all_inner_texts()
            
            # RegEx para salain kung alin ang naglalaman ng dalawang klase ng advisory
            pattern = re.compile(r'POWER ADVISORY|NGCP SCHEDULED POWER INTERRUPTION', re.IGNORECASE)
            
            for text in articles:
                if pattern.search(text):
                    post_text = text.strip()
                    break
            
            # 2. Fallback sakaling hindi makuha ng article selector
            if post_text == "Walang nakitang post.":
                body_text = page.inner_text("body")
                lines = body_text.split('\n')
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        # Kunin ang linya pati na rin ang kasunod nitong mga detalye ng advisory
                        chunk = "\n".join(lines[max(0, i-2):min(len(lines), i+15)])
                        post_text = chunk.strip()
                        break
                        
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
