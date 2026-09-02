import os
import sys
import re
import json
import time
import io
import urllib.parse
import requests
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Block non-product stock/wallpaper sites
EXCLUDED_DOMAINS = [
    'wallpaper', 'desktop', 'backgrounds', 'fanpop', 'pinterest', 'facebook',
    'instagram', 'tiktok', 'youtube', 'twitter', 'imdb', 'deviantart'
]

def sanitize_folder_name(name):
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    return clean

def search_product_images(query, max_results=15):
    encoded_query = urllib.parse.quote(query)
    # Target Google / Bing Image search for authentic product photos
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
        if not matches:
            matches = re.findall(r'"murl":"(http[^"]+)"', res.text)
        
        valid_urls = []
        for m in matches:
            m_clean = urllib.parse.unquote(m)
            m_lower = m_clean.lower()
            
            # Skip non-product domains
            if any(dom in m_lower for dom in EXCLUDED_DOMAINS):
                continue

            if any(ext in m_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                valid_urls.append(m_clean)
        return valid_urls[:max_results]
    except Exception as e:
        print(f"  [Search Error] query '{query}': {e}")
        return []

def download_and_save(urls, output_path, remove_bg=True):
    for u in urls:
        try:
            resp = requests.get(u, headers=HEADERS, timeout=10, stream=True)
            if resp.status_code == 200:
                content = resp.content
                if len(content) < 5000:  # Skip icons/small assets
                    continue
                img_io = io.BytesIO(content)
                img = Image.open(img_io)
                
                # Check minimum dimensions for high quality
                if img.width < 150 or img.height < 150:
                    continue

                success = format_image_to_square_webp(img, output_path, remove_bg=remove_bg)
                if success:
                    return True
        except Exception:
            continue
    return False

def process_perfume(item, index, total, force_overwrite=False):
    full_name = item['full_name']
    brand = item['brand']
    name = item['name']

    folder_name = sanitize_folder_name(full_name)
    perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)
    os.makedirs(perfume_dir, exist_ok=True)

    print(f"\n[{index}/{total}] Processing: {full_name}")

    # Specific queries for real product photos
    image_specs = {
        'bottle': [
            f'"{brand}" "{name}" bottle product photo white background',
            f'"{full_name}" bottle standalone perfume',
            f'{full_name} fragrance bottle'
        ],
        'package': [
            f'"{brand}" "{name}" box packaging product photo',
            f'"{full_name}" retail box packaging',
            f'{full_name} outer box packaging'
        ],
        'both': [
            f'"{brand}" "{name}" bottle and box packaging set',
            f'"{full_name}" bottle with box packaging',
            f'{full_name} bottle and box set'
        ]
    }

    results_summary = {}

    for img_type, search_queries in image_specs.items():
        output_file = os.path.join(perfume_dir, f"{img_type}.webp")

        if not force_overwrite and os.path.exists(output_file) and os.path.getsize(output_file) > 5000:
            print(f"  ✓ {img_type}.webp ready.")
            results_summary[img_type] = True
            continue

        success = False
        for q in search_queries:
            urls = search_product_images(q, max_results=12)
            if urls:
                if download_and_save(urls, output_file, remove_bg=True):
                    print(f"  ✓ {img_type}.webp generated (AI background removed).")
                    success = True
                    break

        # Fallback if box or both specific search yielded no download:
        if not success:
            fallback_query = f'{full_name} perfume product photo'
            urls = search_product_images(fallback_query, max_results=15)
            if urls and download_and_save(urls, output_file, remove_bg=True):
                print(f"  ✓ {img_type}.webp generated via product fallback.")
                success = True

        if not success:
            print(f"  ✗ Could not fetch valid product image for {img_type}.webp")
        
        results_summary[img_type] = success

    return results_summary

def main():
    force_overwrite = '--force' in sys.argv or '-f' in sys.argv
    target_json = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return

    with open(target_json, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    total = len(perfumes)
    print(f"Starting AI product image fetch & background-removal pipeline for {total} perfumes (Force Overwrite: {force_overwrite})...")

    completed = 0
    for i, item in enumerate(perfumes, start=1):
        res = process_perfume(item, i, total, force_overwrite=force_overwrite)
        if all(res.values()):
            completed += 1
        time.sleep(0.3)

    print("\n" + "="*70)
    print(f"Pipeline Complete! Fully processed {completed}/{total} perfumes.")
    print("All image assets stored in ./assets/product_images/")
    print("="*70)

if __name__ == '__main__':
    main()
