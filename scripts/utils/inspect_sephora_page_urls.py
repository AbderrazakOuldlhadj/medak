import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

url = "https://www.sephora.fr/p/the-most-wanted-parfum---eau-de-parfum-P10024968.html"

with sync_playwright() as p:
    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_inspect_page")
    context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    page = context.pages[0] if context.pages else context.new_page()

    search_url = "https://www.sephora.fr/recherche?q=Azzaro+The+Most+Wanted"
    print("Navigating to search URL:", search_url)
    page.goto(search_url, wait_until="domcontentloaded", timeout=25000)

    # Remove privacy overlay banner that intercepts clicks
    page.evaluate("""() => {
        ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
            const el = document.querySelector(id);
            if (el) el.remove();
        });
    }""")
    time.sleep(1)

    product_link = page.locator("a[href*='/p/']").first
    if product_link.is_visible():
        print("Clicking product link with force=True...")
        product_link.click(force=True)
        time.sleep(5)
    page.evaluate("window.scrollTo(0, 400)")
    time.sleep(2)

    # Extract ALL image src, srcset, data-src from the entire page
    all_imgs = page.evaluate("""() => {
        const set = new Set();
        document.querySelectorAll('img, source').forEach(e => {
            if (e.src) set.add(e.src);
            const dataSrc = e.getAttribute('data-src') || e.getAttribute('data-zoom-image') || '';
            if (dataSrc) set.add(dataSrc);
            const srcset = e.srcset || e.getAttribute('data-srcset') || '';
            if (srcset) {
                srcset.split(',').forEach(item => {
                    const u = item.trim().split(' ')[0];
                    if (u) set.add(u);
                });
            }
        });
        return Array.from(set);
    }""")

    print(f"\nExtracted {len(all_imgs)} total image/source elements on page:")
    for u in all_imgs:
        print("  ", u)

    context.close()
