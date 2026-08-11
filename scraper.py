def scrape_rss():
    print("Binabasa at ino-order ang RSS feed...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Walang nahanap na entries sa RSS feed o mali ang link.")
        return

    # I-sort ang entries mula pinakabago hanggang pinakaluma
    # Gagamitin ang published_parsed date
    sorted_entries = sorted(
        feed.entries, 
        key=lambda x: x.get('published_parsed', (0,0,0,0,0,0)), 
        reverse=True
    )

    print(f"May nakitang {len(sorted_entries)} na post sa RSS feed (sorted).")
    
    # I-process ang sorted entries
    for entry in sorted_entries[:3]:
        raw_content = entry.get('description', '') or entry.get('summary', '')
        
        # Kunin ang petsa para sa formatting
        published_parsed = entry.get('published_parsed')
        if published_parsed:
            dt = datetime(*published_parsed[:6])
            post_date_str = dt.strftime('%B %d, %Y at %I:%M %p')
        else:
            post_date_str = datetime.now().strftime('%B %d, %Y')

        # Linisin ang HTML
        soup_html = BeautifulSoup(raw_content, 'html.parser')
        content = soup_html.get_text(separator='\n')
        
        normalized_content = unicodedata.normalize('NFKD', content).upper()
        
        # Suriin kung Power Advisory
        if "ADVISORY" in normalized_content or "SUBSTATION" in normalized_content:
            formatted, ctrl_no = format_advisory(content, post_date_str)
            
            if not check_if_exists(ctrl_no):
                print(f"\n[BAGONG ADVISORY NAKITA]: {ctrl_no}")
                save_to_supabase(formatted)
                send_telegram_alert(formatted)
            else:
                print(f"Naka-save na sa database ang post na may Control No: {ctrl_no}")
        else:
            print("May post sa feed pero hindi ito Power Advisory.")
