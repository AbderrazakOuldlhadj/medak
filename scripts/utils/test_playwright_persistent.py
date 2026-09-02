import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    # Use Chromium non-headless or persistent context
    userDataDir = "./data/interim/playwright_user_data"
    context = p.chromium.launch_persistent_context(
        userDataDir,
        headless=False,  # Launch visible window to bypass Akamai bot detection
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.sephora.fr/p/sauvage---eau-de-toilette-P2266017.html", wait_until="domcontentloaded", timeout=30000)
    print("Page Title:", page.title())

    # Accept cookie banner if present
    try:
        page.locator("#onetrust-accept-btn-handler").click(timeout=4000)
        print("Accepted cookies.")
    except Exception:
        pass

    time.sleep(3)

    img_data = page.eval_on_selector_all(
        "img",
        """elements => elements.map(e => ({
            src: e.src,
            data_src: e.getAttribute('data-src') || e.getAttribute('data-zoom-image') || '',
            srcset: e.srcset,
            alt: e.alt,
            class: e.className
        })).filter(o => o.src || o.data_src || o.srcset)"""
    )
    print(f"Total img elements found: {len(img_data)}")
    for d in img_data:
        if any(kw in str(d).lower() for kw in ['sauvage', '2266017', 'mastercatalog', 'hi-res', 'product', 'media']):
            print("  [MATCH]", d)

    context.close()
