import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

with sync_playwright() as p:
    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_inspect_profile")
    context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    page = context.pages[0] if context.pages else context.new_page()

    url = "https://www.sephora.fr/p/sauvage-elixir---parfum-pour-homme---notes-agrumes--epices-et-bois-P10017596.html"
    print("Navigating to product page:", url)
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=3000)
    except Exception:
        pass

    time.sleep(3)

    # Click on gallery thumbnail buttons if present to load high-res images
    thumbnails = page.locator("button.thumbnail, button[class*='thumb'], button[class*='gallery']").all()
    print(f"Found {len(thumbnails)} thumbnail buttons.")

    # Evaluate ALL img src and source srcset on the entire page
    all_media = page.evaluate("""() => {
        const set = new Set();
        document.querySelectorAll('img, source').forEach(el => {
            const src = el.src || el.getAttribute('data-src') || el.getAttribute('data-zoom') || '';
            if (src) set.add(src);
            const srcset = el.srcset || el.getAttribute('data-srcset') || '';
            if (srcset) {
                srcset.split(',').forEach(item => {
                    const u = item.trim().split(' ')[0];
                    if (u) set.add(u);
                });
            }
        });
        return Array.from(set);
    }""")

    print(f"Extracted {len(all_media)} total media URLs on page:")
    for m in all_media:
        if 'media.sephora' in m or 'dam' in m or 'pim' in m or 'published' in m or 'P10017596' in m or 'demandware' in m:
            print("  [PRODUCT MATCH]", m)

    context.close()
