import json
import logging
from playwright.sync_api import sync_playwright

# ✅ Setup logging
logging.basicConfig(
    filename="zomato_scraper.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s — %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def scrape_reviews_correctly():
    all_data = []
    restaurant_limit = 2  # ✅ Try with 2 restaurants

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        logging.info("Opening Zomato Hinjawadi restaurants page...")
        page.goto("https://www.zomato.com/pune/hinjawadi-restaurants", timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load restaurants
        for _ in range(40):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1200)

        try:
            page.wait_for_selector("h4", timeout=10000)
        except:
            logging.error("❌ Restaurant cards did not load.")
            browser.close()
            return

        restaurants = []
        seen = set()
        cards = page.locator("h4").all()
        logging.info(f"Found {len(cards)} restaurant title cards")

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
            except Exception as e:
                logging.warning(f"⚠️ Error parsing restaurant card: {e}")
                continue
        browser.close()
        logging.info(f"✅ Collected {len(restaurants)} restaurant URLs.")

    # Step 2: Visit each restaurant and collect reviews + stars
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for i, (name, base_url) in enumerate(restaurants, 1):
            logging.info(f"\n🔍 [{i}/{restaurant_limit}] Visiting: {name}")
            page = browser.new_page()
            try:
                page.goto(base_url, timeout=60000)
                page.wait_for_timeout(5000)

                review_tab = page.query_selector("a:has-text('Reviews')")
                if not review_tab:
                    logging.warning(f"❌ No Reviews tab for {name}")
                    page.close()
                    continue

                review_href = review_tab.get_attribute("href")
                review_url = review_href if review_href.startswith("http") else "https://www.zomato.com" + review_href
                page.goto(review_url, timeout=60000)
                page.wait_for_timeout(4000)

                # Scroll to load reviews
                for _ in range(5):
                    page.mouse.wheel(0, 2500)
                    page.wait_for_timeout(1200)

                # Review text
                p_tags = page.query_selector_all("p.sc-1hez2tp-0")
                # Star rating
                rating_tags = page.query_selector_all("div.sc-1q7bklc-1")

                logging.info(f"Found {len(p_tags)} reviews and {len(rating_tags)} ratings")

                reviews = []

                for idx, tag in enumerate(p_tags):
                    try:
                        text = tag.inner_text().strip()
                        if len(text) >= 80 and any(w in text.lower() for w in ["food", "ambience", "service", "staff", "taste"]):
                            rating = "N/A"
                            if idx < len(rating_tags):
                                rating = rating_tags[idx].inner_text().strip()
                            reviews.append({
                                "review": text,
                                "rating": rating
                            })
                        if len(reviews) >= 5:
                            break
                    except Exception as e:
                        logging.warning(f"⚠️ Error reading review #{idx}: {e}")
                        continue

                all_data.append({
                    "restaurant": name,
                    "url": review_url,
                    "reviews": reviews
                })

                logging.info(f"✅ Collected {len(reviews)} reviews for {name}")

            except Exception as e:
                logging.error(f"❌ Error with {name}: {e}")
            finally:
                page.close()

        browser.close()

    # Save to JSON
    output_file = "zomato_reviews_with_stars.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    logging.info(f"\n🎉 Done! Data saved to '{output_file}'")

# Run
scrape_reviews_correctly()
