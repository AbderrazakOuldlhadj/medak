import os
import sys
import re
import io
import json
import time
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

def normalize_perfume_tokens(text):
    # Convert text to lowercase token set with expanded abbreviations
    text_lower = text.lower()
    text_lower = re.sub(r'\beau\s*de\s*parfum\b', ' edp ', text_lower)
    text_lower = re.sub(r'\beau\s*de\s*toilette\b', ' edt ', text_lower)
    text_lower = re.sub(r'\beau\s*de\s*cologne\b', ' edc ', text_lower)
    text_lower = re.sub(r'\bintense\b', ' ', text_lower)  # Often synonymous with EDP/Parfum versions
    
    tokens = set(re.findall(r'\w+', text_lower))
    for drop in ['dz', 'odorem', 'pafen', 'smellgood', 'fragrance', 'produit', 'product', 'parfums', 'com', 'store', 'shop']:
        tokens.discard(drop)
    return tokens

def find_existing_matching_folder(product_name, url=""):
    """
    Check if a matching folder (case-insensitive or partial token match) already exists in assets/product_images.
    """
    base_dir = os.path.join(ROOT_DIR, "assets", "product_images")
    if not os.path.exists(base_dir):
        return None
    
    # Extract domain brand name if available (e.g. azzaro.com -> azzaro)
    domain = urllib.parse.urlparse(url).netloc
    domain_brand = domain.replace('www.', '').split('.')[0]
    if domain_brand and len(domain_brand) > 3 and domain_brand.lower() not in product_name.lower():
        product_name = f"{domain_brand} {product_name}"

    target_tokens = normalize_perfume_tokens(product_name)
    
    best_match = None
    best_score = 0.0
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            folder_tokens = normalize_perfume_tokens(folder)
            if not folder_tokens:
                continue
            
            clean_target = re.sub(r'[^a-zA-Z0-9]', '', product_name).lower()
            clean_folder = re.sub(r'[^a-zA-Z0-9]', '', folder).lower()
            if clean_target == clean_folder:
                return folder
                
            intersection = target_tokens.intersection(folder_tokens)
            if intersection:
                score = len(intersection) / max(len(target_tokens), len(folder_tokens))
                # High overlap or target tokens subset of existing folder
                if target_tokens.issubset(folder_tokens) or score > best_score:
                    if score >= 0.5 or target_tokens.issubset(folder_tokens):
                        best_score = score
                        best_match = folder
                        
    return best_match if best_score >= 0.45 else None

def extract_product_title(soup, url):
    # If title tag is generic (e.g., 'Parfum Azzaro...'), fallback to page headings or URL path
    h1 = soup.find('h1')
    h1_text = h1.text.strip() if h1 else ""
    
    # Check if H1 is meaningful
    if h1_text and len(h1_text) > 3 and not re.search(r'parfum|boutique|accueil|home', h1_text, re.I):
        # Check if URL has additional path info (e.g. eau-de-parfum-intense)
        path_parts = [p for p in urllib.parse.urlparse(url).path.strip('/').split('/') if p]
        if path_parts:
            last_slug = path_parts[-1].replace('-', ' ').title()
            if last_slug.lower() not in h1_text.lower():
                return f"{h1_text} {last_slug}"
        return h1_text
    
    # 2. Meta og:title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content') and 'parfum' not in og_title['content'].lower()[:15]:
        return og_title['content'].strip()
    
    # 3. URL path slug composition
    path_parts = [p for p in urllib.parse.urlparse(url).path.strip('/').split('/') if p and p not in ['fr', 'en', 'ar', 'produit', 'product', 'parfums', 'parfum', 'products']]
    if path_parts:
        clean_slugs = [p.replace('-', ' ').title() for p in path_parts]
        return " ".join(clean_slugs)

    # Fallback to title tag
    title_tag = soup.find('title')
    if title_tag and title_tag.text.strip():
        return title_tag.text.strip()

    return "Perfume Product"

def extract_image_urls(soup, html_text, base_url):
    urls = []
    
    # 1. Target single product container first (WooCommerce / Shopify / e-commerce product gallery)
    product_container = soup.find(class_=re.compile(r'woocommerce-product-gallery|single-product|product-single|product-detail|product-gallery|product-media', re.I))
    
    target_scope = product_container if product_container else (soup.find('main') or soup)

    # Search img tags inside main product container
    for img in target_scope.find_all('img'):
        for attr in ['data-large_image', 'data-zoom-image', 'data-src', 'data-full-src', 'data-lazy-src', 'src']:
            val = img.get(attr)
            if val and re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', val, re.I):
                urls.append(val)
        srcset = img.get('srcset')
        if srcset:
            for p in srcset.split(','):
                p_url = p.strip().split(' ')[0]
                if re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', p_url, re.I):
                    urls.append(p_url)

    # Search anchor links inside main product container
    for a in target_scope.find_all('a', href=True):
        href = a['href']
        if re.search(r'\.(jpg|jpeg|png|webp)(\?.*)?$', href, re.I):
            urls.append(href)

    # Always include main product og:image
    og_img = soup.find('meta', property='og:image')
    if og_img and og_img.get('content'):
        urls.append(og_img['content'])

    # Special handling for Chopard product URLs (e.g. 95201-0442.html)
    if 'chopard.com' in base_url:
        code_match = re.search(r'(\d+-\d+)\.html', base_url)
        if code_match:
            code = code_match.group(1)
            for suffix in ['_01.png', '_02.png', '_03.png']:
                urls.append(f"https://objects-prod.cdn.chopard.com/e_trim/dpr_auto,w_1000,c_lpad,ar_1:1,g_center/f_auto,q_auto:best/ProductsAssets/Web/{code}{suffix}")

    # Clean, deduplicate, and keep high-res versions
    cleaned = []
    base_photo_map = {}
    
    for u in urls:
        if u.startswith('//'):
            full_u = 'https:' + u
        else:
            full_u = urllib.parse.urljoin(base_url, u)
            
        c_lower = full_u.lower()
        if any(x in c_lower for x in ['logo', 'icon', 'favicon', 'chaty', 'photoroom', 'payment', 'banner', 'avatar', '3.png', 'site.webmanifest', 'facebook', 'twitter', 'instagram', 'youtube', 'pin-icon']):
            continue
            
        if 'media.sephora.eu' in full_u or 'demandware.static' in full_u:
            if any(k in full_u for k in ['media_principal', 'media_', 'published', 'PIM', 'massivpimupload']):
                base_u = full_u.split('?')[0]
                high_res_sephora = f"{base_u}?scaleWidth=1000&scaleMode=fit"
                if high_res_sephora not in cleaned:
                    cleaned.append(high_res_sephora)
                continue

        # Group by base filename or path
        parsed_url = urllib.parse.urlparse(full_u)
        path = parsed_url.path
        
        # Remove query params or resize dimensions
        base_path = re.sub(r'(-\d+x\d+|-scaled)?(\.[a-zA-Z0-9]+)$', r'\2', path, flags=re.I)
        
        size_match = re.search(r'-(\d+)x(\d+)\.[a-zA-Z0-9]+$', path)
        w = int(size_match.group(1)) if size_match else 9999
        
        if base_path not in base_photo_map or w > base_photo_map[base_path][0]:
            best_url = urllib.parse.urlunparse(parsed_url._replace(path=base_path))
            base_photo_map[base_path] = (w, best_url)

    for base_path, (w, best_url) in base_photo_map.items():
        if best_url not in cleaned:
            cleaned.append(best_url)

    return cleaned

def fetch_html_with_playwright(url):
    print("  [Notice] Initial HTTP request protected (403/Cloudflare/Akamai). Launching Playwright browser...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,  # Headless false bypasses Akamai bot walls
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                locale='fr-FR'
            )
            page = context.new_page()
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(3)
            # Remove cookie overlays
            page.evaluate("""() => {
                ['#tc-privacy-wrapper', '#tc-privacy-overlay-banner', '#onetrust-consent-sdk'].forEach(id => {
                    const el = document.querySelector(id);
                    if (el) el.remove();
                });
            }""")
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"  [Playwright Error]: {e}")
        return None

def fetch_fallback_product_images(query, max_results=10):
    print(f"  [Fallback Search] Fetching product photos via search query: '{query}'...")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
        if not matches:
            matches = re.findall(r'"murl":"(http[^"]+)"', res.text)
        
        valid_urls = []
        excluded = ['wallpaper', 'desktop', 'backgrounds', 'fanpop', 'pinterest', 'facebook', 'instagram', 'tiktok', 'youtube', 'twitter']
        for m in matches:
            m_clean = urllib.parse.unquote(m)
            m_lower = m_clean.lower()
            if any(dom in m_lower for dom in excluded):
                continue
            if any(ext in m_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                valid_urls.append(m_clean)
        return valid_urls[:max_results]
    except Exception as e:
        print(f"  [Search Error]: {e}")
        return []

def download_images(url, custom_folder_name=None):
    print(f"Fetching product page: {url}")
    html_text = ""
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 403:
            html_text = fetch_html_with_playwright(url)
        else:
            res.raise_for_status()
            html_text = res.text
    except Exception as e:
        print(f"Standard requests failed ({e}). Trying Playwright...")
        html_text = fetch_html_with_playwright(url)

    if not html_text:
        print(f"Error: Could not retrieve HTML from {url}")
        return None, []

    soup = BeautifulSoup(html_text, 'html.parser')
    
    raw_title = extract_product_title(soup, url)
    sanitized_title = sanitize_folder_name(raw_title)
    
    # Check if a matching folder exists in assets/product_images
    existing_folder = find_existing_matching_folder(sanitized_title, url)
    
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
    
    if not image_urls or 'access denied' in raw_title.lower():
        clean_query = folder_name if folder_name else sanitized_title
        image_urls = fetch_fallback_product_images(f'"{clean_query}" bottle product photo white background')
        if not image_urls:
            image_urls = fetch_fallback_product_images(f'{clean_query} fragrance bottle')
        
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

                # Filter out banners / non-square aspect ratios
                aspect_ratio = img.width / float(img.height)
                if aspect_ratio > 2.0 or aspect_ratio < 0.45:
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
