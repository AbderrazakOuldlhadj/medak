import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

def download_sephora_via_page_goto():
    perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", "AZZARO WANTED BY NIGHT EDP 100ML")
    os.makedirs(perfume_dir, exist_ok=True)

    user_data_dir = os.path.join(ROOT_DIR, "data", "interim", "sephora_browser_profile")

    candidates = [
        "https://media.sephora.eu/media/p/P3351012/media_principal/AZZARO_3351012_WANTEDBYNIGHT_EDP_100ML_PACK_03351012_1000x1000.jpg",
        "https://media.sephora.eu/media/p/P3351012/media_1/AZZARO_3351012_WANTEDBYNIGHT_EDP_100ML_03351012_1000x1000.jpg",
        "https://media.sephora.eu/media/p/P3351012/media_2/AZZARO_3351012_WANTEDBYNIGHT_EDP_100ML_03351012_1000x1000.jpg",
        "https://www.sephora.fr/dw/image/v2/BCVW_PRD/on/demandware.static/-/Sites-masterCatalog_Sephora/default/dw10f0f5b9/P3351012_media_principal.jpg?sw=1000&sh=1000&sm=fit",
    ]

    saved_files = []
    idx = 1

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            locale='fr-FR',
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.new_page()

        for u in candidates:
            print(f"Navigating to CDN image: {u}")
            try:
                res = page.goto(u, wait_until='domcontentloaded', timeout=15000)
                if res and res.status == 200:
                    img_bytes = res.body()
                    if len(img_bytes) > 5000:
                        raw_name = f"raw_{idx}.jpg"
                        raw_path = os.path.join(perfume_dir, raw_name)
                        with open(raw_path, 'wb') as f:
                            f.write(img_bytes)

                        img = Image.open(raw_path)
                        webp_name = "bottle.webp" if idx == 1 else f"image_{idx}.webp"
                        webp_path = os.path.join(perfume_dir, webp_name)

                        success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                        if success:
                            print(f"  [✓ Authentic Sephora Image {idx}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(img_bytes)//1024} KB)")
                            saved_files.append(webp_path)
                            idx += 1
                else:
                    print(f"  Status code: {res.status if res else 'None'}")
            except Exception as e:
                print(f"  [Error]: {e}")

        context.close()

    print(f"\nTotal authentic Sephora images saved: {len(saved_files)}")

if __name__ == '__main__':
    download_sephora_via_page_goto()
