import os
import sys
import json
import csv
import re
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TARGET_JSON = os.path.join(ROOT_DIR, 'data', 'interim', 'target_perfumes_from_sheet.json')
IMG_BASE_DIR = os.path.join(ROOT_DIR, 'assets', 'product_images')
OUTPUT_CSV = os.path.join(ROOT_DIR, 'data', 'processed', 'shopify_catalog_with_suggested_prices.csv')
ABDERK3_CSV = os.path.join(ROOT_DIR, 'data', 'interim', 'abderk3_sheet.csv')

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/AbderrazakOuldlhadj/medak/main"

HEADERS = [
    'Title', 'URL handle', 'Description', 'Vendor', 'Product category', 'Type', 'Tags',
    'Published on online store', 'Status', 'SKU', 'Barcode',
    'Option1 name', 'Option1 value', 'Option1 Linked To',
    'Option2 name', 'Option2 value', 'Option2 Linked To',
    'Option3 name', 'Option3 value', 'Option3 Linked To',
    'Price', 'Compare-at price', 'Cost per item', 'Charge tax', 'Tax code',
    'Unit price total measure', 'Unit price total measure unit',
    'Unit price base measure', 'Unit price base measure unit',
    'Inventory tracker', 'Inventory quantity', 'Continue selling when out of stock',
    'Weight value (grams)', 'Weight unit for display', 'Requires shipping', 'Fulfillment service',
    'Product image URL', 'Image position', 'Image alt text', 'Variant image URL', 'Gift card',
    'SEO title', 'SEO description', 'Color (product.metafields.shopify.color-pattern)',
    'Google Shopping / Google product category', 'Google Shopping / Gender', 'Google Shopping / Age group',
    'Google Shopping / Manufacturer part number (MPN)', 'Google Shopping / Ad group name',
    'Google Shopping / Ads labels', 'Google Shopping / Condition', 'Google Shopping / Custom product',
    'Google Shopping / Custom label 0', 'Google Shopping / Custom label 1',
    'Google Shopping / Custom label 2', 'Google Shopping / Custom label 3', 'Google Shopping / Custom label 4'
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def clean_folder_name(full_name):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    res = full_name
    for c in invalid_chars:
        res = res.replace(c, '')
    return res.strip()

def sort_images(img_list):
    priority = {'bottle.webp': 1, 'both.webp': 2, 'package.webp': 3}
    def key_func(filename):
        f_lower = filename.lower()
        if f_lower in priority:
            return (0, priority[f_lower], f_lower)
        if f_lower.startswith('image_') and f_lower.endswith('.webp'):
            num_match = re.search(r'\d+', f_lower)
            idx = int(num_match.group()) if num_match else 99
            return (1, idx, f_lower)
        if f_lower.endswith('.webp'):
            return (2, 0, f_lower)
        if f_lower.startswith('raw_'):
            num_match = re.search(r'\d+', f_lower)
            idx = int(num_match.group()) if num_match else 99
            return (4, idx, f_lower)
        return (3, 0, f_lower)
    return sorted(img_list, key=key_func)

def parse_price(val):
    if not val or str(val).strip() == 'N/A':
        return 0
    clean = re.sub(r'[^\d]', '', str(val))
    return int(clean) if clean else 0

def build_catalog_with_github_urls():
    sheet_prices = {}
    with open(ABDERK3_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            title = r[1].strip()
            gros = parse_price(r[4])
            min_p = parse_price(r[5])
            max_p = parse_price(r[6])
            sheet_prices[title] = {'gros': gros, 'min': min_p, 'max': max_p}

    if 'LACOSTE L.12.12 NOIR EDT 100ML' in sheet_prices:
        sheet_prices['LACOSTE L.12.12 NOIR 100ML'] = sheet_prices['LACOSTE L.12.12 NOIR EDT 100ML']

    with open(TARGET_JSON, 'r', encoding='utf-8') as f:
        perfumes = json.load(f)

    output_rows = []
    products_count = 0

    for idx, item in enumerate(perfumes, start=1):
        full_name = item['full_name'].strip()
        brand = item.get('brand', '').strip() or 'Parfums DZ'
        
        price_info = sheet_prices.get(full_name, {})
        gros = price_info.get('gros', parse_price(item.get('gros_price', '')))
        max_p = price_info.get('max', 0)
        
        if max_p > 0:
            if max_p > (gros + 3500):
                sug_raw = max_p - 1000
            else:
                sug_raw = max_p - 600 if max_p > gros + 600 else max_p - 100
            
            base = round(sug_raw / 100) * 100
            rem = base % 1000
            if rem < 250:
                sug = (base // 1000) * 1000 - 100
            elif rem < 750:
                sug = (base // 1000) * 1000 + 500
            else:
                sug = (base // 1000) * 1000 + 900
                
            if sug >= max_p:
                sug = max_p - 500 if max_p % 1000 == 0 else max_p - (max_p % 1000) + 500
                if sug >= max_p:
                    sug = max_p - 100
                    
            price_str = f'{float(sug):.2f}'
            compare_at_str = f'{float(max_p):.2f}'
        else:
            sug = gros + 4500
            price_str = f'{float(sug):.2f}'
            compare_at_str = f'{float(sug + 1500):.2f}'
            
        cost_per_item = f'{float(gros):.2f}' if gros else ''

        handle = slugify(full_name) or f'perfume-{idx}'
        title = full_name
        description = f'<p>{title}</p>'
        vendor = brand
        product_category = 'Health & Beauty > Personal Care > Cosmetics > Perfumes & Fragrances'
        product_type = 'Perfume'
        tags = f'Parfum DZ, {vendor}'

        fn_upper = full_name.upper()
        if any(w in fn_upper for w in ['HOMME', 'MEN', 'MALE', 'UOMO', 'KING']):
            gender = 'Male'
        elif any(w in fn_upper for w in ['FEMME', 'WOMEN', 'HER', 'GIRL', 'BELLE']):
            gender = 'Female'
        else:
            gender = 'Unisex'

        folder_name = clean_folder_name(full_name)
        folder_path = os.path.join(IMG_BASE_DIR, folder_name)
        
        if os.path.exists(folder_path):
            all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))]
            sorted_files = sort_images(all_files) if all_files else []
        else:
            sorted_files = []

        # Construct public GitHub URLs
        # Note: urllib.parse.quote handles spaces and special characters
        encoded_folder = urllib.parse.quote(folder_name)
        img_urls = [f"{GITHUB_RAW_BASE}/assets/product_images/{encoded_folder}/{urllib.parse.quote(img_f)}" for img_f in sorted_files]
        first_img_url = img_urls[0] if img_urls else ''

        main_row = {
            'Title': title,
            'URL handle': handle,
            'Description': description,
            'Vendor': vendor,
            'Product category': product_category,
            'Type': product_type,
            'Tags': tags,
            'Published on online store': 'TRUE',
            'Status': 'Active',
            'SKU': f'PFDZ-{idx:03d}',
            'Barcode': '',
            'Option1 name': 'Title',
            'Option1 value': 'Default Title',
            'Option1 Linked To': '',
            'Option2 name': '',
            'Option2 value': '',
            'Option2 Linked To': '',
            'Option3 name': '',
            'Option3 value': '',
            'Option3 Linked To': '',
            'Price': price_str,
            'Compare-at price': compare_at_str,
            'Cost per item': cost_per_item,
            'Charge tax': 'FALSE',
            'Tax code': '',
            'Unit price total measure': '',
            'Unit price total measure unit': '',
            'Unit price base measure': '',
            'Unit price base measure unit': '',
            'Inventory tracker': 'shopify',
            'Inventory quantity': '100',
            'Continue selling when out of stock': 'DENY',
            'Weight value (grams)': '150',
            'Weight unit for display': 'g',
            'Requires shipping': 'TRUE',
            'Fulfillment service': 'manual',
            'Product image URL': first_img_url,
            'Image position': '1' if first_img_url else '',
            'Image alt text': title if first_img_url else '',
            'Variant image URL': first_img_url,
            'Gift card': 'FALSE',
            'SEO title': title,
            'SEO description': title,
            'Color (product.metafields.shopify.color-pattern)': '',
            'Google Shopping / Google product category': product_category,
            'Google Shopping / Gender': gender,
            'Google Shopping / Age group': 'Adult (13+ years old)',
            'Google Shopping / Manufacturer part number (MPN)': '',
            'Google Shopping / Ad group name': 'Perfumes DZ',
            'Google Shopping / Ads labels': 'Perfumes DZ',
            'Google Shopping / Condition': 'New',
            'Google Shopping / Custom product': 'FALSE',
            'Google Shopping / Custom label 0': 'Top Seller',
            'Google Shopping / Custom label 1': '',
            'Google Shopping / Custom label 2': '',
            'Google Shopping / Custom label 3': '',
            'Google Shopping / Custom label 4': ''
        }
        output_rows.append(main_row)

        # Additional image rows
        for img_idx, img_u in enumerate(img_urls[1:], start=2):
            img_row = {h: '' for h in HEADERS}
            img_row['URL handle'] = handle
            img_row['Product image URL'] = img_u
            img_row['Image position'] = str(img_idx)
            img_row['Image alt text'] = title
            output_rows.append(img_row)

        products_count += 1

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in output_rows:
            writer.writerow(r)

    print(f'Successfully generated CSV with GitHub image URLs: {OUTPUT_CSV}')
    print(f'Total products: {products_count} ({len(output_rows)} total rows including extra images)')

if __name__ == '__main__':
    build_catalog_with_github_urls()
