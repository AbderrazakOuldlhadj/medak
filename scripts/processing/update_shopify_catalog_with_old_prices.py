import os
import sys
import json
import csv
import re

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TARGET_JSON = os.path.join(ROOT_DIR, 'data', 'interim', 'target_perfumes_from_sheet.json')
IMG_BASE_DIR = os.path.join(ROOT_DIR, 'assets', 'product_images')
OUTPUT_CSV = os.path.join(ROOT_DIR, 'data', 'processed', 'shopify_catalog_with_suggested_prices.csv')
ABDERK3_CSV = os.path.join(ROOT_DIR, 'data', 'interim', 'abderk3_sheet.csv')

HEADERS = [
    'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
    'Option1 Name', 'Option1 Value', 'Option1 Linked To', 'Option2 Name', 'Option2 Value', 'Option2 Linked To',
    'Option3 Name', 'Option3 Value', 'Option3 Linked To', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
    'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price',
    'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Unit Price Total Measure',
    'Unit Price Total Measure Unit', 'Unit Price Base Measure', 'Unit Price Base Measure Unit', 'Variant Barcode',
    'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description',
    'Flavor (product.metafields.shopify.flavor)', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code',
    'Cost per item', 'Status'
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

def main():
    # Load prices from abderk3_sheet.csv
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

    # Map alias
    if 'LACOSTE L.12.12 NOIR EDT 100ML' in sheet_prices:
        sheet_prices['LACOSTE L.12.12 NOIR 100ML'] = sheet_prices['LACOSTE L.12.12 NOIR EDT 100ML']

    with open(TARGET_JSON, 'r', encoding='utf-8') as f:
        perfumes = json.load(f)

    output_rows = []
    products_count = 0

    for item in perfumes:
        full_name = item['full_name'].strip()
        brand = item.get('brand', '').strip()
        
        price_info = sheet_prices.get(full_name, {})
        gros = price_info.get('gros', parse_price(item.get('gros_price', '')))
        max_p = price_info.get('max', 0)
        
        # Calculate Suggested Selling Price and Old Price (Variant Compare At Price)
        if max_p > 0:
            if max_p > (gros + 3500):
                sug_raw = max_p - 1000
            else:
                sug_raw = max_p - 600 if max_p > gros + 600 else max_p - 100
            
            # Psychological rounding
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

        folder_name = clean_folder_name(full_name)
        folder_path = os.path.join(IMG_BASE_DIR, folder_name)
        
        if os.path.exists(folder_path):
            all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))]
            sorted_files = sort_images(all_files) if all_files else []
        else:
            sorted_files = []

        handle = slugify(full_name) or f'perfume-{products_count+1}'
        title = full_name
        description = f'<p>{title}</p>'
        vendor = brand or 'Parfums DZ'
        product_category = 'Health & Beauty > Personal Care > Cosmetics > Perfumes & Fragrances'
        product_type = 'Perfume'
        tags = f'Parfum DZ, {vendor}'
        published = 'true'
        
        img_paths = [f'assets/product_images/{folder_name}/{img_file}' for img_file in sorted_files]
        first_img = img_paths[0] if img_paths else ''
        
        main_row = {
            'Handle': handle,
            'Title': title,
            'Body (HTML)': description,
            'Vendor': vendor,
            'Product Category': product_category,
            'Type': product_type,
            'Tags': tags,
            'Published': published,
            'Option1 Name': 'Title',
            'Option1 Value': 'Default Title',
            'Option1 Linked To': '',
            'Option2 Name': '',
            'Option2 Value': '',
            'Option2 Linked To': '',
            'Option3 Name': '',
            'Option3 Value': '',
            'Option3 Linked To': '',
            'Variant SKU': '',
            'Variant Grams': '0.0',
            'Variant Inventory Tracker': 'shopify',
            'Variant Inventory Qty': '100',
            'Variant Inventory Policy': 'deny',
            'Variant Fulfillment Service': 'manual',
            'Variant Price': price_str,
            'Variant Compare At Price': compare_at_str,
            'Variant Requires Shipping': 'true',
            'Variant Taxable': 'false',
            'Unit Price Total Measure': '',
            'Unit Price Total Measure Unit': '',
            'Unit Price Base Measure': '',
            'Unit Price Base Measure Unit': '',
            'Variant Barcode': '',
            'Image Src': first_img,
            'Image Position': '1' if first_img else '',
            'Image Alt Text': title if first_img else '',
            'Gift Card': 'false',
            'SEO Title': title,
            'SEO Description': title,
            'Flavor (product.metafields.shopify.flavor)': '',
            'Variant Image': first_img,
            'Variant Weight Unit': 'kg',
            'Variant Tax Code': '',
            'Cost per item': cost_per_item,
            'Status': 'active'
        }
        output_rows.append(main_row)
        
        for img_idx, img_src in enumerate(img_paths[1:], start=2):
            img_row = {h: '' for h in HEADERS}
            img_row['Handle'] = handle
            img_row['Image Src'] = img_src
            img_row['Image Position'] = str(img_idx)
            img_row['Image Alt Text'] = title
            output_rows.append(img_row)
            
        products_count += 1

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in output_rows:
            writer.writerow(r)

    print(f'Done! Successfully generated {products_count} unique products ({len(output_rows)} total rows with images) to {OUTPUT_CSV}')

if __name__ == '__main__':
    main()
