import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError, Error
import os
from dotenv import load_dotenv
OUTPUT_FILE = "products.json"

load_dotenv()  # Load environment variables from .env
USERNAME = os.getenv("SCRAPER_USERNAME")
PASSWORD = os.getenv("SCRAPER_PASSWORD")
LOGIN_URL = "https://hiring.idenhq.com/"


# -------- SCRAPER FUNCTION --------
FAILED_FILE = "failed_products.json"


async def scrape_products(page, seen_products, products,autosave_interval=20):
    """
    Scrapes product data from the provided page, extracting details from product cards and updating the products list while tracking seen products to avoid duplicates.

    Autosaves progress after a specified interval and logs failed extractions for further review.

    Args:
        page: The Playwright page object to scrape.
        seen_products (set): Set to track products already processed.
        products (list): List to store successfully scraped product data.
        autosave_interval (int, optional): Number of new products to process before autosaving. Defaults to 20.

    Returns:
        int: The number of new products successfully scraped and added.
    """


    product_cards = await page.query_selector_all(
        "div.rounded-lg.border.bg-card.text-card-foreground.shadow-sm.animate-fade-in"
    )
    new_count = 0
    failed_products = []  # 📝 store failed ones here

    for card in product_cards:
        try:
            product = {}

            # Product Name
            name_el = await card.query_selector("h3.font-semibold.tracking-tight.text-lg")
            product["name"] = (await name_el.inner_text()).strip() if name_el else ""
            if not product["name"]:
                # 🚨 No name = skip, but log
                failed_products.append({"reason": "Missing name", "html": await card.inner_html()})
                continue  

            # Category
            category_el = await card.query_selector(
                "div.inline-flex.items-center.rounded-full.border"
            )
            product["category"] = (await category_el.inner_text()).strip() if category_el else ""

            # Attributes
            attributes = {}
            pairs = await card.query_selector_all("dl > div")
            for pair in pairs:
                dt = await pair.query_selector("dt")
                dd = await pair.query_selector("dd")
                if dt and dd:
                    key = (await dt.inner_text()).strip(": ").strip()
                    val = (await dd.inner_text()).strip()
                    attributes[key] = val

            product["attributes"] = attributes

            # ✅ Only append if complete
            key = f"{product['name']}|{product['category']}"
            if key not in seen_products:
                seen_products.add(key)
                products.append(product)
                new_count += 1

                # 🔄 Autosave every N products
                if len(products) % autosave_interval == 0:
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(products, f, indent=2, ensure_ascii=False)
                    print(f"💾 Autosaved progress: {len(products)} products")

        except Exception as e:
            # ⛔ If scraping failed mid-way
            failed_products.append({
                "reason": str(e),
                "html": await card.inner_html()
            })
            print(f"⚠️ Error scraping product card: {e}")
            continue

    # 📝 Save failed products separately
    if failed_products:
        try:
            with open(FAILED_FILE, "a", encoding="utf-8") as f:
                json.dump(failed_products, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"🚨 Logged {len(failed_products)} failed products into {FAILED_FILE}")
        except Exception as e:
            print(f"⚠️ Failed to save failed products: {e}")

    return new_count



# -------- SAFE CLICK HELPER --------
async def safe_click(page, selector, label, timeout=15000):
    """
    Safely clicks an element identified by a selector, with waiting, scrolling, and retry logic.

    Args:
        page: The Playwright page object.
        selector (str): CSS selector for the target element.
        label (str): Readable label for logging purposes.
        timeout (int, optional): Maximum wait time in milliseconds. Defaults to 15000.

    Raises:
        TimeoutError: If the element is not found within the timeout period.
    """

    try:
        btn = await page.wait_for_selector(selector, timeout=timeout, state="visible")
        await btn.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        await btn.click(force=True)
        print(f"✅ Clicked {label}")
        await page.wait_for_timeout(2000)
    except TimeoutError:
        print(f"❌ Timeout: {label} not found!")
        raise



# -------- MAIN RUN FUNCTION --------

SESSION_FILE = "session.json"
async def run():
    """
    Automates the login, navigation, and product scraping process from an inventory web page using Playwright.

    Manages persistent login sessions, navigates through paginated product listings, scrapes product data while preventing duplicates, handles lazy-loaded content, and saves both successful and failed scrape results to disk. Provides progress logging and a summary report upon completion or interruption.
    """
    
    products, seen_products = [], set()
    failed_products = []   # ⬅️ Track failed ones
    context = None
    page = None

    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir="./user_data",
                headless=False            )
            
            page = await context.new_page()
            
            await page.goto(LOGIN_URL)
            

            # --- LOGIN ---
            if await page.query_selector("input#email"):
                print("⚠️ Logging in...")
                await page.fill("input#email", USERNAME)
                await page.fill("input#password", PASSWORD)
                await page.click("button:has-text('Sign in')")
                await page.wait_for_load_state("networkidle", timeout=6000000)
                print("✅ Login successful!")
            else:
                print("✅ Already logged in.")

            # --- NAVIGATION ---
            print("➡️ Navigating to products...")
            await safe_click(page, "button:has-text('Start Journey')", "Start Journey")
            await safe_click(page, "button:has-text('Continue Search')", "Continue Search")
            await safe_click(page, "button:has-text('Inventory Section')", "Inventory Section")

            print("📊 Product table visible, scraping...")

            # --- SCRAPE PRODUCTS ---
            has_next = True
            while has_next:
                before = len(products)

                # Scrape visible products
                await scrape_products(page, seen_products, products)

                # Scroll to bottom for lazy-load
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)

                # Scrape again after scroll
                await scrape_products(page, seen_products, products)

                # Save incrementally again
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)

                # Check if new products appeared
                if len(products) == before:
                    # Try next page
                    next_btn = await page.query_selector("button:has-text('Next')") or \
                               await page.query_selector("button[aria-label='Next']")

                    if next_btn and await next_btn.is_enabled():
                        print("➡️ Moving to next page...")
                        await next_btn.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)
                    else:
                        has_next = False

            print(f"✅ Scraped {len(products)} products.")

    except Error:
        print("⚠️ Browser was closed manually. Stopping gracefully...")

    finally:
        # Always save whatever was scraped
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

        # ✅ Save failed products (if any)
        if failed_products:
            with open("failed_products.json", "w", encoding="utf-8") as f:
                json.dump(failed_products, f, indent=2, ensure_ascii=False)

        # 📊 Final Summary Report
        print("\n📌 SCRAPING SUMMARY")
        print(f"   ✅ Success: {len(products)} products")
        print(f"   ❌ Failed : {len(failed_products)} products")
        print(f"   💾 Saved  : {OUTPUT_FILE}")
        if failed_products:
            print(f"   ⚠️ Check failed_products.json for details")

        # Close browser if still open
        if context:
            try:
                await context.close()
            except Exception:
                pass
        print("👋 Exiting scraper.")

# -------- ENTRY POINT --------
if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n🛑 Scraper interrupted by user. Progress saved, exiting gracefully...")

