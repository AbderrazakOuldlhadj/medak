import os
import sys
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from PIL import Image

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

ASSETS_DIR = r'c:\Users\msipc\Desktop\products\parfums\assets\product_images'

# Ignore common stop words for token matching
STOP_WORDS = {'de', 'la', 'le', 'les', 'for', 'men', 'homme', 'parfum', 'eau', 'edt', 'edp', 'edc', '100ml', '125ml', '150ml', '200ml', '80ml', '90ml', '75ml', '50ml', 'ml'}

def get_missing_folders():
    missing = []
    if not os.path.exists(ASSETS_DIR):
        return []
    for d in sorted(os.listdir(ASSETS_DIR)):
        dp = os.path.join(ASSETS_DIR, d)
        if os.path.isdir(dp):
            files = [f for f in os.listdir(dp) if os.path.isfile(os.path.join(dp, f))]
            if 'bottle.webp' not in files:
                missing.append(d)
    return missing

def get_key_variant_tokens(folder_name):
    tokens = [w.lower() for w in re.findall(r'\w+', folder_name)]
    key_tokens = [t for t in tokens if t not in STOP_WORDS]
    return set(key_tokens)

def search_odorem_dz(perfume_folder_name, session):
    key_tokens = get_key_variant_tokens(perfume_folder_name)
    if not key_tokens:
        return None

    # Formulate search queries
    query_str = " ".join(key_tokens)
    search_url = f"https://odorem-dz.com/?s={urllib.parse.quote(query_str)}&post_type=product"
    print(f"Searching odorem-dz.com for key terms: '{query_str}'...")

    try:
        res = session.get(search_url, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        candidates = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/produit/' in href:
                full_href = urllib.parse.urljoin('https://odorem-dz.com', href).split('#')[0]
                title = a.text.strip()
                if full_href not in [c[0] for c in candidates]:
                    candidates.append((full_href, title))

        best_url = None
        best_score = 0

        for cand_url, cand_title in candidates:
            slug = urllib.parse.urlparse(cand_url).path.strip('/').split('/')[-1].replace('-', ' ')
            cand_tokens = set(w.lower() for w in re.findall(r'\w+', slug + " " + cand_title))
            
            # Key variant tokens MUST be a subset of candidate tokens (or at least 80% match)
            matched_keys = key_tokens.intersection(cand_tokens)
            score = len(matched_keys)

            # Strict check: key distinctive words (like 'kouros', 'scandale', 'sauvage', 'paradigme', 'explorer') MUST match
            distinctive_word = [k for k in key_tokens if k not in ['dior', 'yves', 'saint', 'laurent', 'guerlain', 'hugo', 'boss', 'armani', 'gaultier', 'chanel', 'prada']][:1]
            if distinctive_word and distinctive_word[0] not in cand_tokens:
                continue

            if score > best_score and score >= len(key_tokens) * 0.6:
                best_score = score
                best_url = cand_url

        return best_url
    except Exception as e:
        print(f"  Search error: {e}")
        return None

def process_product_page(product_url, target_dir, session):
    print(f"  Fetching product page: {product_url}")
    try:
        res = session.get(product_url, timeout=15)
        if res.status_code != 200:
            return 0
        soup = BeautifulSoup(res.text, 'html.parser')
        
        urls = []
        og = soup.find('meta', property='og:image')
        if og and og.get('content'):
            urls.append(og['content'])
            
        gallery = soup.find_all(class_=re.compile(r'woocommerce-product-gallery|product-gallery|gallery', re.I))
        for g in gallery:
            for a in g.find_all('a', href=True):
                if any(ext in a['href'].lower() for ext in ['.jpg', '.png', '.webp']):
                    urls.append(a['href'])
            for img in g.find_all('img'):
                val = img.get('data-large_image') or img.get('src') or img.get('data-src')
                if val and any(ext in val.lower() for ext in ['.jpg', '.png', '.webp']):
                    urls.append(val)
                    
        base_map = {}
        for u in urls:
            if u.startswith('data:'): continue
            full_u = urllib.parse.urljoin('https://odorem-dz.com', u)
            clean_u = re.sub(r'-\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', full_u)
            base_map[clean_u] = clean_u
            
        unique_urls = list(base_map.values())
        print(f"  Found {len(unique_urls)} unique gallery image URLs.")
        
        saved = 0
        for idx, u in enumerate(unique_urls, 1):
            try:
                r = session.get(u, timeout=12)
                if r.status_code == 200 and len(r.content) > 5000:
                    ext = 'png' if u.endswith('.png') else 'jpg'
                    raw_name = f'raw_{idx}.{ext}'
                    raw_path = os.path.join(target_dir, raw_name)
                    with open(raw_path, 'wb') as f:
                        f.write(r.content)
                    
                    img = Image.open(raw_path)
                    webp_name = 'bottle.webp' if idx == 1 else f'image_{idx}.webp'
                    webp_path = os.path.join(target_dir, webp_name)
                    
                    success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                    if success:
                        print(f"    [✓ Saved] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(r.content)//1024} KB)")
                        saved += 1
            except Exception as e:
                print(f"    Error saving image {u}: {e}")
                
        return saved
    except Exception as e:
        print(f"  Product page error: {e}")
        return 0

def run_batch():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    })
    
    # First wipe folders that received incorrect fallback matches
    incorrect_folders = [
        'YVES SAINT LAURENT KOUROS EDT 100ML',
        'YVES SAINT LAURENT LA NUIT DE L\'HOMME EDT 100ML',
        'YVES SAINT LAURENT Y EDT 100ML',
        'JEAN PAUL GAULTIER SCANDALE PARFUM 150ML'
    ]
    for inf in incorrect_folders:
        dp = os.path.join(ASSETS_DIR, inf)
        if os.path.exists(dp):
            for f in os.listdir(dp):
                try: os.remove(os.path.join(dp, f))
                except Exception: pass

    missing = get_missing_folders()
    print(f"Starting refined batch search & download for {len(missing)} missing perfumes...")
    
    results = {'processed': [], 'skipped': []}
    
    for idx, folder_name in enumerate(missing, 1):
        print(f"\n==================================================")
        print(f"[{idx}/{len(missing)}] Processing: {folder_name}")
        print(f"==================================================")
        
        target_dir = os.path.join(ASSETS_DIR, folder_name)
        product_url = search_odorem_dz(folder_name, session)
        
        if product_url:
            print(f"  ✓ Matched Product URL: {product_url}")
            saved_count = process_product_page(product_url, target_dir, session)
            if saved_count > 0:
                results['processed'].append((folder_name, product_url, saved_count))
            else:
                print(f"  ✗ Failed to download images from page.")
                results['skipped'].append((folder_name, "Failed image download"))
        else:
            print(f"  ✗ Not found on odorem-dz.com. Passing to next perfume...")
            results['skipped'].append((folder_name, "Not found on odorem-dz.com"))
            
    print("\n\n==================================================")
    print("REFINED BATCH PROCESSING COMPLETE")
    print("==================================================")
    print(f"Successfully Processed: {len(results['processed'])}")
    print(f"Skipped / Not Found: {len(results['skipped'])}")
    
    if results['processed']:
        print("\n--- POPULATED PERFUMES ---")
        for p, u, cnt in results['processed']:
            print(f"✓ {p} -> {u} ({cnt} images)")
            
    if results['skipped']:
        print("\n--- SKIPPED PERFUMES ---")
        for p, reason in results['skipped']:
            print(f"✗ {p} -> {reason}")

if __name__ == '__main__':
    run_batch()
