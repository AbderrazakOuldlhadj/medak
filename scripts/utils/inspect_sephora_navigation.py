import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    # Launch Chromium with stealth flags to bypass headless detection
    browser = p.chromium.launch(
        channel="msedge",
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    )
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="fr-FR"
    )
    
    # Hide navigator.webdriver
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    page = context.new_page()

    page.goto("https://www.sephora.fr/", wait_until="domcontentloaded", timeout=40000)
    print("Page title:", page.title())

    # Check for cookie button
    try:
        cookie_btn = page.locator("#onetrust-accept-btn-handler")
        if cookie_btn.is_visible(timeout=5000):
            cookie_btn.click()
            print("Clicked cookie button.")
    except Exception as e:
        print("Cookie step note:", e)

    time.sleep(2)

    # Search query
    page.goto("https://www.sephora.fr/p/sauvage---eau-de-toilette-P2266017.html", wait_until="domcontentloaded", timeout=40000)
    print("Product Page title:", page.title())

    # Get image URLs
    imgs = page.eval_on_selector_all(
        "img[src*='demandware.static'], img[src*='products_all'], img[srcset*='demandware.static']",
        "elements => elements.map(e => e.src || e.srcset)"
    )
    print(f"Found {len(imgs)} Sephora image elements:")
    for im in imgs:
        print("  ", im)

    browser.close()
