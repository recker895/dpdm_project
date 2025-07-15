from playwright.sync_api import sync_playwright
import json

def extract_only_review_paragraphs():
    url = "https://www.zomato.com/pune/akasa-poolbar-kitchen-wakad/reviews"
    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)

        page.wait_for_timeout(5000)

        # Scroll to load more reviews
        for _ in range(5):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)

        print("🔍 Looking for <p> tags with class 'sc-1hez2tp-0'...")
        p_tags = page.query_selector_all("p.sc-1hez2tp-0")

        count = 0
        for tag in p_tags:
            try:
                text = tag.inner_text().strip()

                # Filter: must look like a real review
                if len(text) >= 80 and any(p in text for p in [".", ",", "!", "food", "ambience", "service", "place"]):
                    reviews.append({
                        "review_number": count + 1,
                        "text": text
                    })
                    print(f"{count+1}. {text}")
                    count += 1

            except:
                continue

        browser.close()

    # Save filtered reviews to JSON
    with open("zomato_reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Saved {count} filtered reviews to 'zomato_reviews.json'")

extract_only_review_paragraphs()
