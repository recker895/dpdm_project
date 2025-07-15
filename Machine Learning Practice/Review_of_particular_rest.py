from playwright.sync_api import sync_playwright
import json
import time

def extract_reviews_multiple_restaurants():
    all_reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Step 1: Go to Hinjawadi restaurant listing
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(4000)

        # Scroll to load more
        for _ in range(4):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)

        # Step 2: Collect restaurant names and base URLs
        seen = set()
        restaurants = []
        cards = page.locator("h4").all()
        for card in cards:
            name = card.inner_text().strip()
            if name in seen:
                continue
            anchor = card.locator("xpath=ancestor::a[1]")
            href = anchor.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else "https://www.zomato.com" + href
                restaurants.append((name, full_url + "/reviews"))  # ✅ Force review URL
                seen.add(name)
            if len(restaurants) >= 2:  # only first 2 restaurants
                break

        browser.close()  # done with list page

    # Step 3: Now visit each /reviews page using your working logic
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for name, review_url in restaurants:
            print(f"\n🔍 Scraping: {name} | {review_url}")
            reviews = []

            context = browser.new_context()
            page = context.new_page()
            page.goto(review_url, timeout=60000)
            page.wait_for_timeout(5000)

            # Scroll to load reviews
            for _ in range(5):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)

            # Extract review <p> tags
            p_tags = page.query_selector_all("p.sc-1hez2tp-0")
            count = 0
            for tag in p_tags:
                try:
                    text = tag.inner_text().strip()
                    if len(text) >= 80 and any(x in text for x in [".", "!", "food", "ambience", "service", "place"]):
                        reviews.append(text)
                        print(f"  {count+1}. {text[:100]}...")
                        count += 1
                except:
                    continue

            all_reviews.append({
                "restaurant": name,
                "reviews": reviews[:5]
            })

            page.close()

        browser.close()

    # Step 4: Save all to JSON
    with open("hinjawadi_reviews_multiple.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)

    print("\n✅ Done! Data saved to 'hinjawadi_reviews_multiple.json'")

extract_reviews_multiple_restaurants()
