from playwright.sync_api import sync_playwright
import json

def scrape_reviews_correctly():
    all_data = []
    restaurant_limit = 250

    # Step 1: Get restaurant names and URLs
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll more to load enough restaurants (increase scrolls)
        for _ in range(40):  # scroll more for 250 restaurants
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1200)

        restaurants = []
        seen = set()
        cards = page.locator("h4").all()

        for card in cards:
            try:
                name = card.inner_text().strip()
                if name in seen or not name:
                    continue
                anchor = card.locator("xpath=ancestor::a[1]")
                href = anchor.get_attribute("href")
                if href:
                    full_url = href if href.startswith("http") else "https://www.zomato.com" + href
                    restaurants.append((name, full_url))
                    seen.add(name)
                if len(restaurants) >= restaurant_limit:
                    break
            except:
                continue
        browser.close()

    # Step 2: Visit each restaurant, get reviews
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for i, (name, base_url) in enumerate(restaurants, start=1):
            print(f"\n🔍 [{i}/{restaurant_limit}] Visiting: {name}")
            page = browser.new_page()
            try:
                page.goto(base_url, timeout=60000)
                page.wait_for_timeout(5000)

                # Find review tab
                review_tab = page.query_selector("a:has-text('Reviews')")
                if not review_tab:
                    print(f"❌ No review tab found for {name}")
                    page.close()
                    continue

                review_href = review_tab.get_attribute("href")
                review_url = review_href if review_href.startswith("http") else "https://www.zomato.com" + review_href

                # Open review tab
                page.goto(review_url, timeout=60000)
                page.wait_for_timeout(4000)

                # Scroll to load reviews
                for _ in range(3):
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

                print(f"✅ Done with {name} ({i}/{restaurant_limit})")

            except Exception as e:
                print(f"⚠️ Error for {name}: {str(e)}")

            page.close()

        browser.close()

    # Save to JSON
    with open("zomato_reviews_250.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("\n🎉 All done! Saved to 'zomato_reviews_250.json'")

# Run the function
scrape_reviews_correctly()
