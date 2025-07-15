from playwright.sync_api import sync_playwright
import time
import csv

def extract_restaurant_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set True if you want headless
        page = browser.new_page()
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load more restaurants
        print("🔄 Scrolling to load restaurants...")
        for _ in range(12):
            page.mouse.wheel(0, 5000)
            time.sleep(2)

        print("✅ Scrolling done.\nExtracting restaurant data...")

        # Collect all cards with h4 (restaurant name)
        cards = page.locator("h4").all()

        data = []
        for card in cards:
            try:
                name = card.inner_text().strip()

                # Look upward to parent to get whole card
                parent = card.locator("xpath=ancestor::a[1]")

                # Rating (look inside parent for .sc-1q7bklc-1.* pattern)
                rating = "No Rating"
                rating_span = parent.locator("css=div[class*='sc-1q7bklc-1']").first
                if rating_span:
                    try:
                        rating = rating_span.inner_text().strip()
                    except:
                        pass

                # Price (search any child span/div for "for two")
                price = "No Price Info"
                all_text_elements = parent.locator("css=div, span").all()
                for el in all_text_elements:
                    text = el.inner_text().strip()
                    if "for two" in text.lower():
                        price = text
                        break

                print(f"🍽️ {name} | ⭐ {rating} | 💰 {price}")
                data.append([name, rating, price])
            except Exception as e:
                print(f"⚠️ Error parsing a card: {e}")

        browser.close()

    # Save to CSV
    with open("hinjawadi_restaurants.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Restaurant Name", "Rating", "Price for Two"])
        writer.writerows(data)

    print(f"\n✅ Done! {len(data)} restaurants saved to 'hinjawadi_restaurants.csv'")

# Run it
extract_restaurant_details()
