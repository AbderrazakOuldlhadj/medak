import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

test_items = [
    "DIOR SAUVAGE EDT 100ML",
    "AZZARO THE MOST WANTED EDP 100ML",
    "GUERLAIN L'HOMME IDEAL INTENSE EDP 100ML",
    "HERMES H24 EDT 100ML",
    "YVES SAINT LAURENT Y EDT 100ML"
]

with sync_playwright() as p:
    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_new_page_test")
    context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )

    for item in test_items:
        print(f"\nProcessing: '{item}'", flush=True)
        page = context.new_page()

        parts = item.split()
        brand = parts[0]
        name_clean = ' '.join([p for p in parts[1:] if p.upper() not in ['EDP', 'EDT', 'PARFUM', '100ML', '125ML', '200ML', '150ML', '75ML', '80ML', '90ML', '100', 'ML']])
        query_str = f"{brand} {name_clean}".strip()
        search_url = f"https://www.sephora.fr/recherche?q={query_str.replace(' ', '+')}"

        print(f"  Navigating: {search_url}", flush=True)
        page.goto(search_url, wait_until="domcontentloaded", timeout=25000)

        # Remove privacy overlay
        try:
            page.evaluate("""() => {
                ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
                    const el = document.querySelector(id);
                    if (el) el.remove();
                });
            }""")
        except Exception:
            pass

        try:
            page.wait_for_selector("a[href*='/p/']", timeout=10000)
            link = page.locator("a[href*='/p/']").first
            link.click(force=True)
            time.sleep(4)
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
        except Exception as e:
            print(f"  [Error clicking link]: {e}", flush=True)

        imgs = page.eval_on_selector_all(
            "img, source",
            """elements => {
                const set = new Set();
                elements.forEach(e => {
                    const s = e.src || e.getAttribute('data-src') || '';
                    if (s) set.add(s);
                    const srcset = e.srcset || e.getAttribute('data-srcset') || '';
                    if (srcset) {
                        srcset.split(',').forEach(item => {
                            const u = item.trim().split(' ')[0];
                            if (u) set.add(u);
                        });
                    }
                });
                return Array.from(set);
            }"""
        )

        valid = [u for u in imgs if 'media.sephora.eu' in u and any(k in u for k in ['media_principal', 'media_', 'published', 'PIM'])]
        print(f"  ✓ Extracted {len(valid)} Sephora product images.", flush=True)
        page.close()

    context.close()
