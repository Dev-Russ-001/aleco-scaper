# ... (same imports)
# ... (same credentials)

def scrape_facebook():
    posts_found = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # ... (rest of setup)
        
        page = context.new_page()
        page.goto(FB_PAGE_URL, timeout=60000)
        page.wait_for_timeout(8000)
        
        body_text = page.inner_text("body")
        
        # DEBUG: I-print natin ang unang 500 characters ng nakita niya para makita mo sa logs
        print(f"DEBUG: Nakuha ko ang text mula sa FB: {body_text[:500]}...") 
        
        pattern = re.compile(r'POWER ADVISORY|INTERRUPTION|MAINTENANCE|ADVISORY', re.IGNORECASE)
        
        if pattern.search(body_text):
            print("DEBUG: May nahanap na pattern!")
            lines = body_text.split('\n')
            # ... (rest of logic)
        else:
            print("DEBUG: WALA akong nahanap na pattern sa text!")

        # ...
