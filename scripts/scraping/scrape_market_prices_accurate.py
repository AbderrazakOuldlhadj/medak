import os
import sys
import re
import json
import time
import urllib.parse
import concurrent.futures
import requests

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
INTERIM_DIR = os.path.join(DATA_DIR, 'interim')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
TARGET_JSON = os.path.join(INTERIM_DIR, 'target_perfumes_from_sheet.json')
OUTPUT_CSV = os.path.join(PROCESSED_DIR, 'perfume_market_prices_min_max.csv')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6',
}

BRAND_MAP = {
    'ABSOLUS ALLEGORIA': ['GUERLAIN', 'ABSOLUS ALLEGORIA', 'ALLEGORIA'],
    'ANTONIO BANDERAS': ['ANTONIO BANDERAS', 'BANDERAS'],
    'AZZARO': ['AZZARO'],
    'BOUCHERON': ['BOUCHERON'],
    'CAROLINA HERRERA': ['CAROLINA HERRERA', 'CH', 'HERRERA'],
    'CHOPARD': ['CHOPARD'],
    'CK': ['CALVIN KLEIN', 'CK'],
    'CLINIQUE HAPPY': ['CLINIQUE'],
    'DIOR': ['DIOR', 'CHRISTIAN DIOR'],
    'DOLCE GABBANA': ['DOLCE', 'GABBANA', 'DOLCE & GABBANA', 'D&G'],
    'EMPORIO ARMANI': ['ARMANI', 'EMPORIO ARMANI', 'GIORGIO ARMANI'],
    'ENCENS': ['GUERLAIN'],
    'GIVENCHY': ['GIVENCHY'],
    'GUERLAIN': ['GUERLAIN'],
    'HABIT': ['GUERLAIN', 'HABIT ROUGE'],
    'HERMES': ['HERMES', 'HERMÈS'],
    'HUGO BOSS': ['HUGO BOSS', 'HUGO', 'BOSS'],
    'JEAN PAUL GAULTIER': ['JEAN PAUL GAULTIER', 'GAULTIER', 'JPG'],
    'JOOP': ['JOOP'],
    'KENZO': ['KENZO'],
    'L\'INSTANT': ['GUERLAIN', 'L\'INSTANT', 'INSTANT'],
    'LACOSTE': ['LACOSTE'],
    'LAURA BIAGIOTTI': ['LAURA BIAGIOTTI', 'BIAGIOTTI'],
    'MONT BLANC': ['MONT BLANC', 'MONTBLANC'],
    'PRADA': ['PRADA'],
    'SPICE BOMP': ['VIKTOR', 'ROLF', 'VIKTOR&ROLF', 'VIKTOR & ROLF', 'SPICEBOMB', 'SPICE BOMB'],
    'YVES SAINT LAURENT': ['YVES SAINT LAURENT', 'YSL', 'SAINT LAURENT']
}

def extract_volume(text):
    if not text:
        return None
    match = re.search(r'\b(\d{2,3})\s*ML\b', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match_loose = re.search(r'\b(\d{2,3})\s*ml\b', text, re.IGNORECASE)
    return int(match_loose.group(1)) if match_loose else None

def extract_concentration(text):
    if not text:
        return None
    upper = text.upper()
    if 'ELIXIR' in upper or 'ELEXIR' in upper:
        return 'ELIXIR'
    if 'PARFUM' in upper and 'EAU DE PARFUM' not in upper and 'EDP' not in upper and 'EDT' not in upper:
        return 'PARFUM'
    if 'EDP' in upper or 'EAU DE PARFUM' in upper:
        return 'EDP'
    if 'EDT' in upper or 'EAU DE TOILETTE' in upper:
        return 'EDT'
    if 'EDC' in upper or 'COLOGNE' in upper:
        return 'EDC'
    return None

def parse_price_number(price_str):
    if isinstance(price_str, (int, float)):
        val = int(price_str)
        return val if val < 400000 else val // 100
    if not price_str:
        return 0
    s = str(price_str).strip()
    s = re.sub(r'(?i)\b(da|dzd|dz)\b', '', s).strip()
    s = re.sub(r'[,.]00$', '', s)
    s = re.sub(r',\d{1,2}$', '', s)
    
    numbers = re.findall(r'\b\d{4,6}\b', s.replace('.', '').replace(',', '').replace(' ', ''))
    if numbers:
        valid_nums = [int(n) for n in numbers if 3000 <= int(n) <= 300000]
        if valid_nums:
            return valid_nums[0]
    
    cleaned = re.sub(r'[^\d]', '', s)
    if cleaned:
        try:
            val = int(cleaned)
            if val > 300000:
                val = val // 100
            return val if val >= 3000 else 0
        except ValueError:
            return 0
    return 0

def safe_get(session, url, retries=2, timeout=8):
    for attempt in range(retries):
        try:
            res = session.get(url, headers=HEADERS, timeout=timeout)
            if res.status_code == 200:
                return res
        except Exception:
            time.sleep(0.3)
    return None

def scrape_smellgood_dz(session):
    print("--- Scraping Smell Good Dz (Shopify Catalog) ---")
    products = []
    page = 1
    while True:
        url = f"https://smellgood-dz.com/products.json?limit=250&page={page}"
        try:
            res = session.get(url, headers=HEADERS, timeout=12)
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
                    full_title = f"{title} {v_title}" if v_title and v_title.lower() != 'default title' else title
                    price_num = parse_price_number(price)
                    products.append({
                        'store': 'Smell Good DZ',
                        'product_title': full_title,
                        'raw_title': title,
                        'variant_title': v_title,
                        'price_num': price_num,
                        'url': prod_url,
                        'available': available
                    })
            print(f"  Page {page}: fetched {len(prods)} products (Total variants: {len(products)})")
            page += 1
            if len(prods) < 250:
                break
        except Exception as e:
            print(f"  Error scraping Smell Good Dz page {page}: {e}")
            break
    return products

def search_woocommerce_store(store_name, base_url, query, session):
    search_url = f"{base_url}/?s={urllib.parse.quote(query)}&post_type=product"
    results = []
    res = safe_get(session, search_url)
    if not res:
        return results
    try:
        html_content = res.text
        card_matches = re.findall(r'<li[^>]*class=["\'][^"\']*product[^"\']*["\'][^>]*>(.*?)</li>', html_content, re.IGNORECASE | re.DOTALL)
        if not card_matches:
            card_matches = re.findall(r'<div[^>]*class=["\'][^"\']*product[^"\']*["\'][^>]*>(.*?)</div>', html_content, re.IGNORECASE | re.DOTALL)
            
        for card in card_matches:
            title_match = re.search(r'<(?:h2|h3|span)[^>]*class=["\'][^"\']*(?:title|entry-title)[^"\']*["\'][^>]*>(.*?)</', card, re.IGNORECASE | re.DOTALL)
            if not title_match:
                title_match = re.search(r'<a[^>]+href=["\']([^"\']+)["\']\s*[^>]*>(.*?)</a>', card, re.IGNORECASE | re.DOTALL)
            if not title_match:
                continue
                
            href_match = re.search(r'href=["\']([^"\']+)["\']', card, re.IGNORECASE)
            url = href_match.group(1) if href_match else base_url
            
            raw_title = re.sub(r'<[^>]+>', ' ', title_match.group(0)).strip()
            
            # Prefer price inside ins or main price tag
            price_match = re.search(r'<ins[^>]*>(.*?)</ins>', card, re.IGNORECASE | re.DOTALL)
            if not price_match:
                price_match = re.search(r'<(?:span|bdi)[^>]*class=["\'][^"\']*(?:amount|price)[^"\']*["\'][^>]*>(.*?)</', card, re.IGNORECASE | re.DOTALL)
            price_str = re.sub(r'<[^>]+>', '', price_match.group(1)) if price_match else ''
            
            if not price_str:
                p_num_match = re.search(r'(\d{1,3}(?:[.,\s]\d{3})+|\d{4,5})\s*(?:DA|DZD)', card, re.IGNORECASE)
                if p_num_match:
                    price_str = p_num_match.group(0)
                    
            if raw_title and len(raw_title) > 3:
                price_num = parse_price_number(price_str)
                results.append({
                    'store': store_name,
                    'product_title': raw_title,
                    'url': url,
                    'price_num': price_num
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
        html_content = res.text
        cards = re.findall(r'<div[^>]*class=["\'][^"\']*product[^"\']*["\'][^>]*>(.*?)</div>', html_content, re.IGNORECASE | re.DOTALL)
        for card in cards:
            title_match = re.search(r'<a[^>]+href=["\']([^"\']+)["\']\s*[^>]*>(.*?)</a>', card, re.IGNORECASE | re.DOTALL)
            if not title_match:
                continue
            href = urllib.parse.urljoin('https://shoppili-dz.youcan.store', title_match.group(1))
            title_str = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            
            price_match = re.search(r'(\d{1,3}(?:[.,\s]\d{3})+|\d{4,5})\s*(?:DA|DZD)', card, re.IGNORECASE)
            price_str = price_match.group(0) if price_match else ''
            
            if title_str and len(title_str) > 3:
                price_num = parse_price_number(price_str)
                results.append({
                    'store': 'Shoppili DZ',
                    'product_title': title_str,
                    'url': href,
                    'price_num': price_num
                })
    except Exception:
        pass
    return results

def get_required_keywords(target_name):
    u = target_name.upper()
    kw = set()
    
    if 'EPICES EXQUISES' in u: kw.update(['EPICES', 'EXQUISES'])
    elif 'OUD ESSENTIEL' in u: kw.update(['OUD', 'ESSENTIEL'])
    elif 'SANTAL ROYAL' in u: kw.update(['SANTAL', 'ROYAL'])
    elif 'BLUE SEDUCTION' in u: kw.update(['BLUE', 'SEDUCTION'])
    elif 'MOST WANTED' in u: kw.update(['MOST', 'WANTED'])
    elif 'WANTED BY NIGHT' in u: kw.update(['WANTED', 'NIGHT'])
    elif 'SINGULIER' in u: kw.add('SINGULIER')
    elif 'CHIC HOMME' in u or 'CHIC FOR MEN' in u: kw.add('CHIC')
    elif 'BLACK INCENCE' in u or 'BLACK INCENSE' in u: kw.update(['BLACK', 'INCENSE'])
    elif 'OUD MALAKI' in u: kw.update(['OUD', 'MALAKI'])
    elif 'CK IN2U' in u: kw.add('IN2U')
    elif 'CK ONE' in u: kw.update(['CK', 'ONE'])
    elif 'CLINIQUE HAPPY' in u: kw.add('HAPPY')
    elif 'SAUVAGE' in u: kw.add('SAUVAGE')
    elif 'DIOR HOMME SPORT' in u: kw.update(['HOMME', 'SPORT'])
    elif 'DIOR HOMME INTENSE' in u: kw.update(['HOMME', 'INTENSE'])
    elif 'DIOR HOMME PARFUM' in u: kw.update(['HOMME', 'PARFUM'])
    elif 'DIOR COLOGNE' in u: kw.update(['COLOGNE', 'HOMME'])
    elif 'STRONGER WITH YOU INTENSELY' in u: kw.update(['STRONGER', 'INTENSELY'])
    elif 'STRONGER WITH YOU POWERFULLY' in u: kw.update(['STRONGER', 'POWERFULLY'])
    elif 'STRONGER WITH YOU' in u: kw.update(['STRONGER', 'YOU'])
    elif 'ENCENS MYTHIQUE' in u: kw.update(['ENCENS', 'MYTHIQUE'])
    elif 'BLUE LABEL' in u: kw.update(['BLUE', 'LABEL'])
    elif 'IDEAL EXTREME' in u: kw.update(['IDEAL', 'EXTREME'])
    elif 'IDEAL INTENSE' in u: kw.update(['IDEAL', 'INTENSE'])
    elif 'PATCHOULI ARDEN' in u or 'PATCHOULI ARDENT' in u: kw.add('PATCHOULI')
    elif 'HABIT ROUGE' in u: kw.update(['HABIT', 'ROUGE'])
    elif 'H24' in u: kw.add('H24')
    elif 'BOTTLED NIGHT' in u: kw.update(['BOTTLED', 'NIGHT'])
    elif 'JUST DIFFRENT' in u or 'JUST DIFFERENT' in u: kw.add('DIFFERENT')
    elif 'SUPERMAN' in u: kw.add('SUPERMAN')
    elif 'XY' in u: kw.add('XY')
    elif 'LE MALE' in u: kw.add('MALE')
    elif 'SCANDALE' in u or 'SCANDAL' in u: kw.add('SCANDAL')
    elif 'JOOP HOMME' in u: kw.update(['JOOP'])
    elif 'KENZO INTENSE' in u: kw.update(['KENZO', 'INTENSE'])
    elif 'INSTANT HOMME' in u: kw.add('INSTANT')
    elif 'NOIR' in u: kw.add('NOIR')
    elif 'ROMA UOMO' in u: kw.update(['ROMA', 'UOMO'])
    elif 'EXPLORER' in u: kw.add('EXPLORER')
    elif 'PARADIGME' in u: kw.add('PARADIGME')
    elif 'PARADOXE' in u: kw.add('PARADOXE')
    elif 'SPICE BOMP' in u or 'SPICEBOMB' in u:
        kw.add('SPICEBOMB')
        if 'DARK LEATHER' in u: kw.update(['DARK', 'LEATHER'])
        elif 'INFRARED' in u: kw.add('INFRARED')
    elif 'KOUROS' in u: kw.add('KOUROS')
    elif 'LA NUIT DE L\'HOMME' in u: kw.update(['NUIT', 'HOMME'])
    elif 'L\'HOMME' in u: kw.add('HOMME')
    elif 'MY SLF' in u or 'MYSLF' in u: kw.add('MYSLF')
    elif 'Y INTENSE' in u: kw.update(['INTENSE'])
    elif 'Y EDT' in u or 'Y EDP' in u: kw.add('Y')

    return kw

def is_strict_match(target_name, target_brand, target_vol, target_conc, listing_title):
    t_title = target_name.upper()
    l_title = listing_title.upper()
    
    # 0. Brand Verification
    brand_keywords = BRAND_MAP.get(target_brand, [target_brand])
    if not any(b in l_title for b in brand_keywords):
        return False

    # 1. Reject Female / Women listings if target is Male/Homme
    if any(w in t_title for w in ['HOMME', 'MEN', 'MALE', 'UOMO', 'KING']):
        if any(re.search(rf'\b{w}\b', l_title) for w in ['FEMME', 'WOMEN', 'HER', 'GIRL', 'BELLE', 'LADY']):
            return False

    # 2. Strict Volume Check
    listing_vol = extract_volume(listing_title)
    if target_vol and listing_vol:
        if target_vol != listing_vol:
            return False
            
    # 3. Strict Concentration Check
    listing_conc = extract_concentration(listing_title)
    if target_conc and listing_conc:
        if target_conc != listing_conc:
            return False
            
    # 4. Required Line Keywords Check
    req_keywords = get_required_keywords(target_name)
    if req_keywords:
        for kw in req_keywords:
            if kw == 'Y':
                if not re.search(r'\bY\b', l_title):
                    return False
            elif kw not in l_title:
                return False
            
    return True

def process_single_perfume(target_item, smellgood_catalog):
    session = requests.Session()
    full_name = target_item['full_name']
    brand = target_item.get('brand', '')
    gros_price_str = target_item.get('gros_price', '')
    gros_num = parse_price_number(gros_price_str)
    
    target_vol = extract_volume(full_name)
    target_conc = extract_concentration(full_name)
    
    req_kw = list(get_required_keywords(full_name))
    search_query = f"{brand} {' '.join(req_kw[:2])}".strip() if req_kw else full_name
    
    matched_listings = []

    # 1. Smell Good DZ (Shopify Catalog)
    for p in smellgood_catalog:
        if is_strict_match(full_name, brand, target_vol, target_conc, p['product_title']):
            if p['price_num'] >= 3000:
                matched_listings.append(p)

    # 2. Briki Parfums
    briki_res = search_woocommerce_store('Briki Parfums', 'https://briki-parfums.com', search_query, session)
    for p in briki_res:
        if is_strict_match(full_name, brand, target_vol, target_conc, p['product_title']):
            if p['price_num'] >= 3000:
                matched_listings.append(p)

    # 3. Odorem DZ
    odorem_res = search_woocommerce_store('Odorem DZ', 'https://odorem-dz.com', search_query, session)
    for p in odorem_res:
        if is_strict_match(full_name, brand, target_vol, target_conc, p['product_title']):
            if p['price_num'] >= 3000:
                matched_listings.append(p)

    # 4. Gallery Parfums
    gallery_res = search_woocommerce_store('Gallery Parfums DZ', 'https://galleryparfums-dz.com', search_query, session)
    for p in gallery_res:
        if is_strict_match(full_name, brand, target_vol, target_conc, p['product_title']):
            if p['price_num'] >= 3000:
                matched_listings.append(p)

    # 5. Shoppili DZ
    shoppili_res = search_shoppili_dz(search_query, session)
    for p in shoppili_res:
        if is_strict_match(full_name, brand, target_vol, target_conc, p['product_title']):
            if p['price_num'] >= 3000:
                matched_listings.append(p)

    # Deduplicate store prices
    store_prices = {}
    store_urls = {}
    
    for m in matched_listings:
        st = m['store']
        pr = m['price_num']
        ur = m['url']
        if st not in store_prices or pr < store_prices[st]:
            store_prices[st] = pr
            store_urls[st] = ur

    all_prices = list(store_prices.values())
    
    if all_prices:
        min_price = min(all_prices)
        max_price = max(all_prices)
        avg_price = round(sum(all_prices) / len(all_prices))
        min_store = [st for st, pr in store_prices.items() if pr == min_price][0]
        max_store = [st for st, pr in store_prices.items() if pr == max_price][0]
    else:
        min_price = ""
        min_store = ""
        max_price = ""
        max_store = ""
        avg_price = ""

    return {
        'Brand': brand,
        'Perfume Title': full_name,
        'Volume (ML)': f"{target_vol}ML" if target_vol else "",
        'Concentration': target_conc or "",
        'Prix Gros (DZD)': f"{gros_num:,} DZD" if gros_num else "",
        'Min Retail Price (DZD)': f"{min_price:,} DZD" if min_price else "N/A",
        'Min Price Store': min_store or "N/A",
        'Max Retail Price (DZD)': f"{max_price:,} DZD" if max_price else "N/A",
        'Max Price Store': max_store or "N/A",
        'Average Retail Price (DZD)': f"{avg_price:,} DZD" if avg_price else "N/A",
        'Stores Found Count': len(store_prices),
        'Briki Parfums Price': f"{store_prices.get('Briki Parfums'):,} DZD" if store_prices.get('Briki Parfums') else "",
        'Smell Good DZ Price': f"{store_prices.get('Smell Good DZ'):,} DZD" if store_prices.get('Smell Good DZ') else "",
        'Odorem DZ Price': f"{store_prices.get('Odorem DZ'):,} DZD" if store_prices.get('Odorem DZ') else "",
        'Gallery Parfums Price': f"{store_prices.get('Gallery Parfums DZ'):,} DZD" if store_prices.get('Gallery Parfums DZ') else "",
        'Shoppili DZ Price': f"{store_prices.get('Shoppili DZ'):,} DZD" if store_prices.get('Shoppili DZ') else "",
        'Matched URLs': " | ".join([f"{st}: {ur}" for st, ur in store_urls.items()])
    }

def main():
    if not os.path.exists(TARGET_JSON):
        print(f"Error: {TARGET_JSON} not found.")
        return

    with open(TARGET_JSON, 'r', encoding='utf-8') as f:
        target_perfumes = json.load(f)

    session = requests.Session()
    print(f"Loaded {len(target_perfumes)} target perfumes.")

    smellgood_catalog = scrape_smellgood_dz(session)

    print(f"\nSearching store market prices across {len(target_perfumes)} perfumes...")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_single_perfume, item, smellgood_catalog): item for item in target_perfumes}
        for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            results.append(res)
            print(f"[{idx}/{len(target_perfumes)}] Analyzed: {res['Perfume Title']} -> Min: {res['Min Retail Price (DZD)']}, Max: {res['Max Retail Price (DZD)']}")

    results = sorted(results, key=lambda x: (x['Brand'], x['Perfume Title']))

    headers = [
        'Brand', 'Perfume Title', 'Volume (ML)', 'Concentration', 'Prix Gros (DZD)',
        'Min Retail Price (DZD)', 'Min Price Store', 'Max Retail Price (DZD)', 'Max Price Store',
        'Average Retail Price (DZD)', 'Stores Found Count', 'Briki Parfums Price',
        'Smell Good DZ Price', 'Odorem DZ Price', 'Gallery Parfums Price', 'Shoppili DZ Price', 'Matched URLs'
    ]

    import csv
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"\nSUCCESS! Updated market research CSV file at:")
    print(f"-> {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
