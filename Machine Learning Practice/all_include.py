from playwright.sync_api import sync_playwright
import json
import time

def extract_reviews_for_two_restaurants():
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Open Zomato Hinjawadi listing
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load restaurants
        for _ in range(5):
            page.mouse.wheel(0, 5000)
            time.sleep(1.5)

        # Extract 2 restaurant links
        links = []
        seen = set()
        cards = page.locator("h4").all()

        for card in cards:
            try:
                name = card.inner_text().strip()
                parent = card.locator("xpath=ancestor::a[1]")
                href = parent.get_attribute("href")
                if name and href and name not in seen:
                    full_url = href if href.startswith("http") else "https://www.zomato.com" + href
                    links.append((name, full_url))
                    seen.add(name)
                if len(links) >= 2:
                    break
            except:
                continue

        # Step 2: Visit each restaurant's /reviews page
        for name, main_url in links:
            print(f"\n📘 Scraping: {name}")
            reviews_url = main_url.rstrip("/") + "/reviews"
            rpage = context.new_page()

            try:
                rpage.goto(reviews_url, timeout=60000)
                rpage.wait_for_timeout(5000)

                # Scroll the page to load more reviews
                for _ in range(5):
                    rpage.mouse.wheel(0, 3000)
                    time.sleep(2)

                # Take screenshot for visual confirmation
                try:
                    safe_name = name.replace(" ", "_").replace("&", "and")
                    rpage.screenshot(path=f"screenshot_DEBUG_{safe_name}.png", full_page=True, timeout=10000)
                    print(f"📸 Screenshot saved: screenshot_DEBUG_{safe_name}.png")
                except Exception as e:
                    print(f"⚠️ Screenshot failed for {name}: {e}")

                # Extract review <p> tags (broad filter)
                p_tags = rpage.query_selector_all("p")
                print(f"🔎 Found {len(p_tags)} <p> tags")

                filtered_reviews = []
                for tag in p_tags:
                    try:
                        text = tag.inner_text().strip()
                        if len(text) >= 80 and any(word in text.lower() for word in ["food", "ambience", "service", "place", ".", ",", "!"]):
                            filtered_reviews.append(text)
                        if len(filtered_reviews) >= 5:
                            break
                    except:
                        continue

                all_data.append({
                    "restaurant": name,
                    "reviews": filtered_reviews
                })

            except Exception as e:
                print(f"⚠️ Failed to scrape reviews for {name}: {e}")
                all_data.append({
                    "restaurant": name,
                    "reviews": []
                })

            rpage.close()

        browser.close()

    # Save to JSON
    with open("hinjawadi_reviews_debug.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("\n✅ Finished! Reviews saved to 'hinjawadi_reviews_debug.json'")

# Run the function
extract_reviews_for_two_restaurants()
