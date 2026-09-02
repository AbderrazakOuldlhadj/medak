import os
import sys
import re
import io
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
}

def sanitize_folder_name(name):
    # Remove unwanted trailing site titles or separators
    name = re.sub(r'\s*-\s*odorem\s*dz.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\|\s*.*$', '', name)
    # Remove illegal filename chars
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    return clean

def find_existing_matching_folder(product_name):
    """
    Check if a matching folder (case-insensitive or partial token match) already exists in assets/product_images.
    """
    base_dir = os.path.join(ROOT_DIR, "assets", "product_images")
    if not os.path.exists(base_dir):
        return None
    
    target_tokens = set(re.findall(r'\w+', product_name.lower()))
    target_tokens.discard('dz')
    target_tokens.discard('odorem')
    target_tokens.discard('pafen')
    target_tokens.discard('smellgood')
    
    best_match = None
    best_score = 0.0
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            folder_tokens = set(re.findall(r'\w+', folder.lower()))
            if not folder_tokens:
                continue
            
            # Direct exact string match ignoring non-alphanumeric
            clean_target = re.sub(r'[^a-zA-Z0-9]', '', product_name).lower()
            clean_folder = re.sub(r'[^a-zA-Z0-9]', '', folder).lower()
            if clean_target == clean_folder:
                return folder
                
            intersection = target_tokens.intersection(folder_tokens)
            if intersection:
                score = len(intersection) / max(len(target_tokens), len(folder_tokens))
                # If all target tokens (e.g. antonio, banderas, blue, seduction, 200ml) are present in folder tokens
                if target_tokens.issubset(folder_tokens) or score > best_score:
                    if score >= 0.6 or target_tokens.issubset(folder_tokens):
                        best_score = score
                        best_match = folder
                        
    return best_match if best_score >= 0.5 else None

def extract_product_title(soup, url):
    # 1. H1 tag (standard product title)
    h1 = soup.find('h1')
    if h1 and h1.text.strip():
        return h1.text.strip()
    
    # 2. Meta og:title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        return og_title['content'].strip()
    
    # 3. Title tag
    title_tag = soup.find('title')
    if title_tag and title_tag.text.strip():
        return title_tag.text.strip()
    
    # Fallback to URL path slug
    slug = urllib.parse.urlparse(url).path.strip('/').split('/')[-1]
    return slug.replace('-', ' ').title()

def extract_image_urls(soup, html_text, base_url):
    urls = []
    
    # WooCommerce full size images from gallery links/attributes
    gallery_items = soup.find_all(class_=re.compile(r'woocommerce-product-gallery|gallery|product-image|slider', re.I))
    for item in gallery_items:
        for a in item.find_all('a', href=True):
            href = a['href']
            if re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', href, re.I):
                urls.append(href)
        for img in item.find_all('img'):
            for attr in ['data-large_image', 'data-src', 'data-full-src', 'data-lazy-src', 'src']:
                val = img.get(attr)
                if val and re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', val, re.I):
                    urls.append(val)
                    
    # Search for all wp-content/uploads image URLs in raw HTML
    raw_matches = re.findall(r'(https?://[^\s"\'<>]+\/wp-content\/uploads\/[^\s"\'<>]+?\.(?:jpg|jpeg|png|webp))', html_text, re.I)
    for rm in raw_matches:
        urls.append(rm)

    # og:image
    og_img = soup.find('meta', property='og:image')
    if og_img and og_img.get('content'):
        urls.append(og_img['content'])

    # Clean and filter image URLs
    cleaned = []
    seen = set()
    
    for u in urls:
        full_u = urllib.parse.urljoin(base_url, u)
        
        # Remove WooCommerce thumbnail sizing like -600x600, -300x300, -150x150, -100x100 if full size exists
        # E.g. 1000306917-600x600.jpg -> 1000306917.jpg or 1000306917-scaled.jpg
        base_orig = re.sub(r'-\d+x\d+(\.(?:jpg|jpeg|png|webp))', r'\1', full_u, flags=re.I)
        scaled_orig = re.sub(r'-\d+x\d+(\.(?:jpg|jpeg|png|webp))', r'-scaled\1', full_u, flags=re.I)

        for candidate in [base_orig, scaled_orig, full_u]:
            c_lower = candidate.lower()
            if any(x in c_lower for x in ['logo', 'icon', 'favicon', 'chaty', 'photoroom', 'payment', 'banner', 'avatar', '3.png']):
                continue
            if candidate not in seen:
                seen.add(candidate)
                cleaned.append(candidate)

    return cleaned

def download_images(url, custom_folder_name=None):
    print(f"Fetching product page: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    res.raise_for_status()
    html_text = res.text
    soup = BeautifulSoup(html_text, 'html.parser')
    
    raw_title = extract_product_title(soup, url)
    sanitized_title = sanitize_folder_name(raw_title)
    
    # Check if a matching folder exists in assets/product_images
    existing_folder = find_existing_matching_folder(sanitized_title)
    
    if custom_folder_name:
        folder_name = custom_folder_name
    elif existing_folder:
        folder_name = existing_folder
    else:
        folder_name = sanitized_title.upper()
        
    perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)
    os.makedirs(perfume_dir, exist_ok=True)
    
    print(f"Product Title Identified: '{raw_title}'")
    print(f"Target Directory: assets/product_images/{folder_name}/")
    
    image_urls = extract_image_urls(soup, html_text, url)
    print(f"Found {len(image_urls)} candidate image URLs.")
    
    downloaded_files = []
    
    idx = 1
    for img_url in image_urls:
        try:
            r = requests.get(img_url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and len(r.content) > 5000:
                img_io = io.BytesIO(r.content)
                img = Image.open(img_io)
                
                if img.width < 200 or img.height < 200:
                    continue

                ext = img.format.lower() if img.format else 'jpg'
                if ext == 'jpeg': ext = 'jpg'
                
                # Save raw high-res image
                raw_filename = f"raw_{idx}.{ext}" if len(image_urls) > 1 else f"original.{ext}"
                raw_path = os.path.join(perfume_dir, raw_filename)
                
                with open(raw_path, 'wb') as f:
                    f.write(r.content)
                
                print(f"  [✓ Downloaded] {raw_filename} ({img.width}x{img.height}px, {len(r.content)//1024} KB)")
                downloaded_files.append(raw_path)
                
                # Also generate clean square WebP asset with rembg AI
                webp_name = "bottle.webp" if idx == 1 else f"image_{idx}.webp"
                webp_path = os.path.join(perfume_dir, webp_name)
                formatted_success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                if formatted_success:
                    print(f"  [✓ Processed] Saved square WebP asset: {webp_name}")
                
                idx += 1
        except Exception as e:
            print(f"  [✗ Failed URL] {img_url}: {e}")

    print(f"\nSuccessfully downloaded and processed {len(downloaded_files)} images into:")
    print(os.path.abspath(perfume_dir))
    return perfume_dir, downloaded_files

if __name__ == '__main__':
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://odorem-dz.com/produit/antonio-banderas-blue-seduction-200ml/"
    download_images(target_url)
