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

def sanitize_folder_name(name):
    # Remove invalid Windows filename characters
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    return clean

def search_bing_images(query, max_results=12):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
        if not matches:
            matches = re.findall(r'"murl":"(http[^"]+)"', res.text)
        
        valid_urls = []
        for m in matches:
            m_clean = urllib.parse.unquote(m)
            # Skip invalid or tracking URLs
            if any(ext in m_clean.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif']):
                valid_urls.append(m_clean)
        return valid_urls[:max_results]
    except Exception as e:
        print(f"  [Search Error] Bing query '{query}': {e}")
        return []

def download_and_save(urls, output_path):
    for u in urls:
        try:
            resp = requests.get(u, headers=HEADERS, timeout=8, stream=True)
            if resp.status_code == 200:
                content = resp.content
                if len(content) < 4000:  # Skip icons/small assets
                    continue
                img_io = io.BytesIO(content)
                img = Image.open(img_io)
                
                # Check minimum resolution
                if img.width < 150 or img.height < 150:
                    continue

                success = format_image_to_square_webp(img, output_path)
                if success:
                    return True
        except Exception:
            continue
    return False

def process_perfume(item, index, total):
    full_name = item['full_name']
    brand = item['brand']
    name = item['name']

    folder_name = sanitize_folder_name(full_name)
    perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)
    os.makedirs(perfume_dir, exist_ok=True)

    print(f"\n[{index}/{total}] Processing: {full_name}")

    # 3 required image types
    image_specs = {
        'bottle': [
            f"{full_name} bottle product white background",
            f"{brand} {name} bottle white background",
            f"{full_name} bottle isolated white background"
        ],
        'package': [
            f"{full_name} box packaging white background",
            f"{brand} {name} box boxset white background",
            f"{full_name} packaging product white background"
        ],
        'both': [
            f"{full_name} bottle with box packaging white background",
            f"{brand} {name} bottle and box white background",
            f"{full_name} set bottle box white background"
        ]
    }

    results_summary = {}

    for img_type, search_queries in image_specs.items():
        output_file = os.path.join(perfume_dir, f"{img_type}.webp")

        if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
            print(f"  ✓ {img_type}.webp already exists.")
            results_summary[img_type] = True
            continue

        success = False
        for q in search_queries:
            urls = search_bing_images(q, max_results=10)
            if urls:
                if download_and_save(urls, output_file):
                    print(f"  ✓ {img_type}.webp generated successfully.")
                    success = True
                    break

        # Fallback if specific box or both queries returned nothing: use any primary query
        if not success:
            fallback_query = f"{full_name} white background product"
            urls = search_bing_images(fallback_query, max_results=12)
            if urls and download_and_save(urls, output_file):
                print(f"  ✓ {img_type}.webp generated via fallback query.")
                success = True

        if not success:
            print(f"  ✗ Could not fetch image for {img_type}.webp")
        
        results_summary[img_type] = success

    return results_summary

def main():
    target_json = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return

    with open(target_json, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    total = len(perfumes)
    print(f"Starting image fetch pipeline for {total} perfumes...")

    completed = 0
    for i, item in enumerate(perfumes, start=1):
        res = process_perfume(item, i, total)
        if all(res.values()):
            completed += 1
        time.sleep(0.5)  # Slight delay to avoid search throttling

    print("\n" + "="*70)
    print(f"Pipeline Complete! Fully processed {completed}/{total} perfumes.")
    print("All image assets stored in ./assets/product_images/")
    print("="*70)

if __name__ == '__main__':
    main()
