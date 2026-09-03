import os
import sys
import re
import json
import time
import urllib.parse
import concurrent.futures
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r'c:\Users\msipc\Desktop\products\parfums'
DATA_DIR = os.path.join(ROOT_DIR, 'data')
INTERIM_DIR = os.path.join(DATA_DIR, 'interim')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets', 'product_images')

os.makedirs(INTERIM_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
}

STOP_WORDS = {
    'de', 'la', 'le', 'les', 'for', 'men', 'homme', 'femme', 'parfum', 'eau', 
    'edt', 'edp', 'edc', '100ml', '125ml', '150ml', '200ml', '80ml', '90ml', '75ml', '50ml', 'ml', 'pack', 'coffret', 'dzd', 'da', 'بديل'
}

def get_project_perfumes():
    perfumes = set()
    csv_path = os.path.join(PROCESSED_DIR, 'shopify_perfumes_export.csv')
    if os.path.exists(csv_path):
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Title', '').strip()
                if title:
                    perfumes.add(title)
                    
    if os.path.exists(ASSETS_DIR):
        for d in os.listdir(ASSETS_DIR):
            dp = os.path.join(ASSETS_DIR, d)
            if os.path.isdir(dp):
                perfumes.add(d)
                
    return sorted(list(perfumes))

def extract_key_tokens(name):
    tokens = [w.lower() for w in re.findall(r'\w+', name)]
    return [t for t in tokens if t not in STOP_WORDS and not t.isdigit() and len(t) > 1]

def parse_price_number(price_str):
    if isinstance(price_str, (int, float)):
        val = int(price_str)
        return val if val < 300000 else val // 100
    if not price_str:
        return 0
    s = str(price_str).strip()
    s = re.sub(r'(?i)\b(da|dzd|dz)\b', '', s).strip()
    s = re.sub(r'[,.]00$', '', s)
    s = re.sub(r',\d{1,2}$', '', s)
    
    numbers = re.findall(r'\b\d{4,6}\b', s.replace('.', '').replace(',', '').replace(' ', ''))
    if numbers:
        valid_nums = [int(n) for n in numbers if 1000 <= int(n) <= 300000]
        if valid_nums:
            return valid_nums[0]
    
    cleaned = re.sub(r'[^\d]', '', s)
    if cleaned:
        try:
            val = int(cleaned)
            if val > 300000:
                val = val // 100
            return val
        except ValueError:
            return 0
    return 0

def scrape_smellgood_dz(session):
    print("\n--- Scraping Smell Good Dz (Shopify) ---")
    products = []
    page = 1
    while True:
        url = f"https://smellgood-dz.com/products.json?limit=250&page={page}"
        try:
            res = session.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                break
            data = res.json()
            prods = data.get('products', [])
            if not prods:
                break
            for p in prods:
                title = p.get('title', '')
                handle = p.get('handle', '')
                prod_url = f"https://smellgood-dz.com/products/{handle}"
                variants = p.get('variants', [])
                for v in variants:
                    v_title = v.get('title', '')
                    price = v.get('price', '')
                    available = v.get('available', True)
                    full_title = f"{title} ({v_title})" if v_title and v_title.lower() != 'default title' else title
                    price_num = parse_price_number(price)
                    products.append({
                        'store': 'Smell Good Dz',
                        'product_title': full_title,
                        'raw_title': title,
                        'variant_title': v_title,
                        'price_num': price_num,
                        'url': prod_url,
                        'available': available
                    })
            print(f"Smell Good Dz Page {page}: fetched {len(prods)} products (Total variants: {len(products)})")
            page += 1
            if len(prods) < 250:
                break
        except Exception as e:
            print(f"Error scraping Smell Good Dz page {page}: {e}")
            break
    return products

def safe_get(session, url, retries=2, timeout=8):
    for attempt in range(retries):
        try:
            res = session.get(url, headers=HEADERS, timeout=timeout)
            if res.status_code == 200:
                return res
        except Exception:
            time.sleep(0.3)
    return None

def search_odorem_dz(query, session):
    url = f"https://odorem-dz.com/?s={urllib.parse.quote(query)}&post_type=product"
    results = []
    res = safe_get(session, url)
    if not res:
        return results
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.product, article.post, div.product-small, li.product')
        for item in items:
            a_tag = item.select_one('a.woocommerce-LoopProduct-link, h2 a, h3 a, a.product-title')
            if not a_tag:
                a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            title = a_tag.text.strip()
            href = a_tag['href']
            price_tag = item.select_one('.price, .woocommerce-Price-amount')
            price_str = price_tag.text.strip() if price_tag else ''
            results.append({
                'store': 'Odorem Dz',
                'product_title': title,
                'url': href,
                'price_raw': price_str
            })
    except Exception:
        pass
    return results

def search_galleryparfums_dz(query, session):
    url = f"https://galleryparfums-dz.com/?s={urllib.parse.quote(query)}&post_type=product"
    results = []
    res = safe_get(session, url)
    if not res:
        return results
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.product, article, div.product-grid-item, li.product')
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            href = a_tag['href']
            title = item.select_one('h2, h3, .product-title, .entry-title')
            title_str = title.text.strip() if title else a_tag.text.strip()
            price_tag = item.select_one('.price, .amount')
            price_str = price_tag.text.strip() if price_tag else ''
            if title_str and len(title_str) > 3:
                results.append({
                    'store': 'Gallery Parfums Dz',
                    'product_title': title_str,
                    'url': href,
                    'price_raw': price_str
                })
    except Exception:
        pass
    return results

def search_briki_parfums(query, session):
    url = f"https://briki-parfums.com/?s={urllib.parse.quote(query)}&post_type=product"
    results = []
    res = safe_get(session, url)
    if not res:
        return results
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.product, article, div.product-type-simple, li.product')
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            href = a_tag['href']
            title = item.select_one('h2, h3, .product-title, .entry-title')
            title_str = title.text.strip() if title else a_tag.text.strip()
            price_tag = item.select_one('.price, .amount')
            price_str = price_tag.text.strip() if price_tag else ''
            if title_str and len(title_str) > 3:
                results.append({
                    'store': 'Briki Parfums',
                    'product_title': title_str,
                    'url': href,
                    'price_raw': price_str
                })
    except Exception:
        pass
    return results

def search_shoppili_dz(query, session):
    url = f"https://shoppili-dz.youcan.store/products?q={urllib.parse.quote(query)}"
    results = []
    res = safe_get(session, url)
    if not res:
        return results
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.product-card, .product-item, div[class*="product"]')
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            href = urllib.parse.urljoin('https://shoppili-dz.youcan.store', a_tag['href'])
            title = item.select_one('.product-name, .product-title, h3, h2')
            title_str = title.text.strip() if title else a_tag.text.strip()
            price_tag = item.select_one('.price, .product-price')
            price_str = price_tag.text.strip() if price_tag else ''
            if title_str and len(title_str) > 3:
                results.append({
                    'store': 'Shoppili Dz',
                    'product_title': title_str,
                    'url': href,
                    'price_raw': price_str
                })
    except Exception:
        pass
    return results

def search_pafen_dz(query, session):
    url = f"https://pafen-dz.com/search?q={urllib.parse.quote(query)}"
    results = []
    res = safe_get(session, url)
    if not res:
        return results
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select('.product-card, .product, article')
        for item in items:
            a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            href = urllib.parse.urljoin('https://pafen-dz.com', a_tag['href'])
            title = item.select_one('.product-title, h3, h2')
            title_str = title.text.strip() if title else a_tag.text.strip()
            price_tag = item.select_one('.price, .product-price')
            price_str = price_tag.text.strip() if price_tag else ''
            if title_str and len(title_str) > 3:
                results.append({
                    'store': 'Pafen Dz',
                    'product_title': title_str,
                    'url': href,
                    'price_raw': price_str
                })
    except Exception:
        pass
    return results

def process_single_perfume(perfume, smellgood_products):
    session = requests.Session()
    key_tokens = extract_key_tokens(perfume)
    query = " ".join(key_tokens[:3]) if key_tokens else perfume
    matches = []

    # 1. Smell Good Dz
    for p in smellgood_products:
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and set(key_tokens).issubset(p_tokens):
            matches.append({
                'project_perfume': perfume,
                'store': 'Smell Good Dz',
                'store_product_title': p['product_title'],
                'price_num': p['price_num'],
                'availability': 'In Stock' if p['available'] else 'Out of Stock',
                'url': p['url']
            })

    # 2. Odorem Dz
    for p in search_odorem_dz(query, session):
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and (set(key_tokens[:2]).issubset(p_tokens) or set(key_tokens).issubset(p_tokens)):
            p_num = parse_price_number(p['price_raw'])
            matches.append({
                'project_perfume': perfume,
                'store': 'Odorem Dz',
                'store_product_title': p['product_title'],
                'price_num': p_num,
                'availability': 'In Stock',
                'url': p['url']
            })

    # 3. Gallery Parfums Dz
    for p in search_galleryparfums_dz(query, session):
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and set(key_tokens[:2]).issubset(p_tokens):
            p_num = parse_price_number(p['price_raw'])
            matches.append({
                'project_perfume': perfume,
                'store': 'Gallery Parfums Dz',
                'store_product_title': p['product_title'],
                'price_num': p_num,
                'availability': 'In Stock',
                'url': p['url']
            })

    # 4. Briki Parfums
    for p in search_briki_parfums(query, session):
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and set(key_tokens[:2]).issubset(p_tokens):
            p_num = parse_price_number(p['price_raw'])
            matches.append({
                'project_perfume': perfume,
                'store': 'Briki Parfums',
                'store_product_title': p['product_title'],
                'price_num': p_num,
                'availability': 'In Stock',
                'url': p['url']
            })

    # 5. Shoppili Dz
    for p in search_shoppili_dz(query, session):
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and set(key_tokens[:2]).issubset(p_tokens):
            p_num = parse_price_number(p['price_raw'])
            matches.append({
                'project_perfume': perfume,
                'store': 'Shoppili Dz',
                'store_product_title': p['product_title'],
                'price_num': p_num,
                'availability': 'In Stock',
                'url': p['url']
            })

    # 6. Pafen Dz
    for p in search_pafen_dz(query, session):
        p_tokens = set(extract_key_tokens(p['product_title']))
        if key_tokens and set(key_tokens[:2]).issubset(p_tokens):
            p_num = parse_price_number(p['price_raw'])
            matches.append({
                'project_perfume': perfume,
                'store': 'Pafen Dz',
                'store_product_title': p['product_title'],
                'price_num': p_num,
                'availability': 'In Stock',
                'url': p['url']
            })

    return matches

def main():
    session = requests.Session()
    perfumes = get_project_perfumes()
    print(f"Loaded {len(perfumes)} perfumes from project catalog.")

    smellgood_products = scrape_smellgood_dz(session)

    print(f"\nStarting parallel store search across {len(perfumes)} perfumes...")
    all_matches = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(process_single_perfume, p, smellgood_products): p for p in perfumes}
        for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            all_matches.extend(res)
            print(f"[{idx}/{len(perfumes)}] Completed perfume search ({len(res)} store matches)")

    out_file = os.path.join(INTERIM_DIR, 'scraped_store_prices.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

    print(f"\nCompleted! Total store-perfume price matches found: {len(all_matches)}")
    print(f"Saved interim results to: {out_file}")

if __name__ == '__main__':
    main()
