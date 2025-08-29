import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError, Error

OUTPUT_FILE = "products.json"

USERNAME = "sharanyamavinaguni@gmail.com"
PASSWORD = "AG2QBIJt"
LOGIN_URL = "https://hiring.idenhq.com/"

# -------- SCRAPER FUNCTION --------
# -------- SCRAPER FUNCTION --------
async def scrape_products(page, seen_products, products, autosave_interval=20):
    product_cards = await page.query_selector_all(
        "div.rounded-lg.border.bg-card.text-card-foreground.shadow-sm.animate-fade-in"
    )
    new_count = 0

    for card in product_cards:
        try:
            product = {}

            # Product Name
            name_el = await card.query_selector("h3.font-semibold.tracking-tight.text-lg")
            product["name"] = (await name_el.inner_text()).strip() if name_el else ""

            # Category
            category_el = await card.query_selector(
                "div.inline-flex.items-center.rounded-full.border"
            )
            product["category"] = (await category_el.inner_text()).strip() if category_el else ""

            # Attributes
            product["attributes"] = {}
            pairs = await card.query_selector_all("dl > div")
            for pair in pairs:
                dt = await pair.query_selector("dt")
                dd = await pair.query_selector("dd")
                if dt and dd:
                    key = (await dt.inner_text()).strip(": ").strip()
                    val = (await dd.inner_text()).strip()
                    product["attributes"][key] = val

            # Deduplication
            key = f"{product['name']}|{product['category']}"
            if key not in seen_products and product["name"]:
                seen_products.add(key)
                products.append(product)
                new_count += 1

                # 🔄 Autosave every N products
                if len(products) % autosave_interval == 0:
                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                        json.dump(products, f, indent=2, ensure_ascii=False)
                    print(f"💾 Autosaved progress: {len(products)} products")

        except Exception as e:
            print(f"⚠️ Error scraping product card: {e}")
            continue

    return new_count



# -------- SAFE CLICK HELPER --------
async def safe_click(page, selector, label, timeout=15000):
    print(f"🔎 Waiting for {label}...")
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
async def run():
    products, seen_products = [], set()
    context = None
    page = None

    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir="./user_data",
                headless=False
            )
            page = await context.new_page()
            await page.goto(LOGIN_URL)

            # --- LOGIN ---
            if await page.query_selector("input#email"):
                print("⚠️ Logging in...")
                await page.fill("input#email", USERNAME)
                await page.fill("input#password", PASSWORD)
                await page.click("button:has-text('Sign in')")
                await page.wait_for_load_state("networkidle", timeout=60000)
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

                # Save incrementally
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)

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
                    next_btn = await page.query_selector("button:has-text('Next')")
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
        print(f"💾 Progress saved: {len(products)} products in {OUTPUT_FILE}")

        # Close browser if still open
        if context:
            try:
                await context.close()
            except Exception:
                pass
        print("👋 Exiting scraper.")


# -------- ENTRY POINT --------
if __name__ == "__main__":
    asyncio.run(run())
