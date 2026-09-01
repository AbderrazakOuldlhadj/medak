import os
import sys
import re
import requests
import urllib.parse
from PIL import Image
import io

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def search_bing_images(query, max_results=10):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
        if not matches:
            matches = re.findall(r'"murl":"(http[^"]+)"', res.text)
        
        # Filter out obvious non-image or invalid URLs
        valid_urls = []
        for m in matches:
            m_clean = urllib.parse.unquote(m)
            if any(ext in m_clean.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif']):
                valid_urls.append(m_clean)
        return valid_urls[:max_results]
    except Exception as e:
        print(f"Error searching Bing for '{query}': {e}")
        return []

def download_and_process(urls, output_path):
    for u in urls:
        try:
            resp = requests.get(u, headers=HEADERS, timeout=8, stream=True)
            if resp.status_code == 200:
                content = resp.content
                if len(content) < 5000:  # Skip tiny icon files
                    continue
                # Try opening image
                img_io = io.BytesIO(content)
                img = Image.open(img_io)
                # Format to 1000x1000 square webp
                success = format_image_to_square_webp(img, output_path)
                if success:
                    print(f"  Saved: {output_path} (Source: {u[:60]}...)")
                    return True
        except Exception as e:
            continue
    return False

if __name__ == '__main__':
    perfume = "AZZARO THE MOST WANTED EDP 100ML"
    queries = {
        'bottle': f"{perfume} bottle white background",
        'package': f"{perfume} box packaging white background",
        'both': f"{perfume} bottle with box packaging white background"
    }

    test_dir = os.path.join(ROOT_DIR, "assets", "product_images", perfume)
    for image_type, q in queries.items():
        out_file = os.path.join(test_dir, f"{image_type}.webp")
        print(f"\nSearching for '{image_type}': query='{q}'")
        urls = search_bing_images(q, max_results=8)
        print(f"Found {len(urls)} image URLs.")
        ok = download_and_process(urls, out_file)
        if not ok:
            print(f"Failed to fetch valid image for {image_type}")
