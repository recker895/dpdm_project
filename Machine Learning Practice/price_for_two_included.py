from playwright.sync_api import sync_playwright
import time
import csv

def extract_restaurant_details():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load more content
        for _ in range(10):
            page.mouse.wheel(0, 5000)
            time.sleep(2)

        # Target each restaurant card (common wrapper)
        cards = page.query_selector_all("div[class^='sc-dmnqYA']")

        data = []
        for card in cards:
            # Name
            name_el = card.query_selector("h4")
            name = name_el.text_content().strip() if name_el else "Unknown"

            # Rating
            rating_el = card.query_selector("div[class*='sc-1q7bklc-1']")
            rating = rating_el.text_content().strip() if rating_el else "No Rating"

            # Price
            price = "No Price Info"
            for el in card.query_selector_all("div, span"):
                text = el.text_content().strip()
                if "for two" in text.lower():
                    price = text
                    break

            data.append([name, rating, price])

        browser.close()

    # Save to CSV
    with open("hinjawadi_restaurants.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Restaurant Name", "Rating", "Price for Two"])
        writer.writerows(data)

    print(f"\n✅ Done! {len(data)} restaurants saved to 'hinjawadi_restaurants.csv'")

# Run it
extract_restaurant_details()
