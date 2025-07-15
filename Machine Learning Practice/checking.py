from playwright.sync_api import sync_playwright
import time
import csv

def extract_restaurants_with_ratings_to_csv():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_selector("h4")  # Wait for restaurant names

        # Scroll to load all content
        previous_height = 0
        while True:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == previous_height:
                break
            previous_height = current_height

        # Find all restaurant cards
        restaurant_names = page.query_selector_all("h4")
        ratings_raw = page.query_selector_all("div.sc-1q7bklc-1.cILgox")

        # Match names and ratings (assuming same order)
        data = []
        for i in range(len(restaurant_names)):
            name = restaurant_names[i].text_content().strip()
            rating = ratings_raw[i].text_content().strip() if i < len(ratings_raw) else "No Rating"
            data.append([name, rating])

        browser.close()

    # Save to CSV
    with open("hinjawadi_restaurants.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Restaurant Name", "Rating"])
        writer.writerows(data)

    print("\n✅ Data saved to 'hinjawadi_restaurants.csv'")

# Run the function
extract_restaurants_with_ratings_to_csv()