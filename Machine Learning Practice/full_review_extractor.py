from playwright.sync_api import sync_playwright
import json
import time

def scrape_reviews_correctly():
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Step 1: Visit Hinjawadi restaurant listing page
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load more
        for _ in range(3):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(1.5)

        # Step 2: Extract first 2 restaurant names and base links
        restaurants = []
        seen = set()
        cards = page.locator("h4").all()

        for card in cards:
            name = card.inner_text().strip()
            if name in seen:
                continue
            anchor = card.locator("xpath=ancestor::a[1]")
            href = anchor.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else "https://www.zomato.com" + href
                restaurants.append((name, full_url))
                seen.add(name)
            if len(restaurants) >= 2:
                break

        browser.close()

    # Step 3: Visit each restaurant page, get actual Reviews tab URL and scrape
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        for name, base_url in restaurants:
            print(f"\n🔍 Visiting: {name}")
            page = browser.new_page()
            page.goto(base_url, timeout=60000)
            page.wait_for_timeout(5000)

            # Step 3a: Extract the actual review tab URL
            try:
                review_tab = page.query_selector("a:has-text('Reviews')")
                review_href = review_tab.get_attribute("href")
                if review_href:
                    review_url = review_href if review_href.startswith("http") else "https://www.zomato.com" + review_href
                else:
                    print(f"❌ Couldn't find review tab for {name}")
                    continue
            except:
                print(f"❌ No review tab found for {name}")
                continue

            # Step 4: Open review page and extract 5 reviews
            page.goto(review_url, timeout=60000)
            page.wait_for_timeout(4000)

            for _ in range(4):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1000)

            # Extract reviews
            reviews = []
            p_tags = page.query_selector_all("p.sc-1hez2tp-0")
            for tag in p_tags:
                try:
                    text = tag.inner_text().strip()
                    if len(text) >= 80 and any(w in text.lower() for w in ["food", "ambience", "service", ".", "staff"]):
                        reviews.append(text)
                    if len(reviews) >= 5:
                        break
                except:
                    continue

            all_data.append({
                "restaurant": name,
                "url": review_url,
                "reviews": reviews
            })

            page.close()
        browser.close()

    # Step 5: Save to JSON
    with open("zomato_reviews_fixed.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("\n✅ Done! Saved to 'zomato_reviews_fixed.json'")

# Run it
scrape_reviews_correctly()
