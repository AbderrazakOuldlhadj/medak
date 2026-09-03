import os
import sys
import csv
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r'c:\Users\msipc\Desktop\products\parfums'
DATA_DIR = os.path.join(ROOT_DIR, 'data')
INTERIM_DIR = os.path.join(DATA_DIR, 'interim')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets', 'product_images')

STORES = [
    'Shoppili Dz',
    'Smell Good Dz',
    'Briki Parfums',
    'Pafen Dz',
    'Gallery Parfums Dz',
    'Odorem Dz'
]

def format_price_dzd(amount):
    """Format numeric amount into 'XX,XXX DZD' format."""
    if not amount or amount <= 0:
        return "N/A"
    return f"{amount:,} DZD"

def get_project_perfumes():
    """Extract full list of project perfumes."""
    perfumes = set()
    csv_path = os.path.join(PROCESSED_DIR, 'shopify_perfumes_export.csv')
    if os.path.exists(csv_path):
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

def build_csvs():
    interim_json = os.path.join(INTERIM_DIR, 'scraped_store_prices.json')
    if not os.path.exists(interim_json):
        print(f"Interim JSON file not found: {interim_json}")
        return

    with open(interim_json, 'r', encoding='utf-8') as f:
        matches = json.load(f)

    perfumes = get_project_perfumes()
    print(f"Loaded {len(matches)} scraped price matches for {len(perfumes)} catalog perfumes.")

    # 1. Build Detailed Relational CSV: perfume_store_prices.csv
    detailed_csv_path = os.path.join(PROCESSED_DIR, 'perfume_store_prices.csv')
    detailed_rows = []

    for m in matches:
        price_num = m.get('price_num', 0)
        formatted_price = format_price_dzd(price_num)
        detailed_rows.append({
            'Project Perfume Name': m.get('project_perfume', ''),
            'Store Name': m.get('store', ''),
            'Store Product Title': m.get('store_product_title', ''),
            'Price (DZD)': formatted_price,
            'Raw Price': price_num,
            'Availability': m.get('availability', 'In Stock'),
            'Store Product Link': m.get('url', '')
        })

    with open(detailed_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'Project Perfume Name',
            'Store Name',
            'Store Product Title',
            'Price (DZD)',
            'Raw Price',
            'Availability',
            'Store Product Link'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_rows)

    print(f"Successfully generated detailed price list CSV: {detailed_csv_path} ({len(detailed_rows)} rows)")

    # 2. Build Pivot Matrix CSV: perfume_price_comparison_matrix.csv
    matrix_csv_path = os.path.join(PROCESSED_DIR, 'perfume_price_comparison_matrix.csv')
    
    # Group matches by perfume name and store
    perfume_store_map = {p: {store: [] for store in STORES} for p in perfumes}
    
    for m in matches:
        p_name = m.get('project_perfume')
        store = m.get('store')
        price_num = m.get('price_num', 0)
        if p_name in perfume_store_map and store in STORES and price_num > 0:
            perfume_store_map[p_name][store].append(price_num)

    matrix_rows = []
    for p_name in perfumes:
        row = {'Perfume Name': p_name}
        all_prices = []
        stores_count = 0

        for store in STORES:
            prices = perfume_store_map[p_name][store]
            if prices:
                stores_count += 1
                all_prices.extend(prices)
                # Format single or multiple prices
                unique_prices = sorted(list(set(prices)))
                formatted = " | ".join([format_price_dzd(p) for p in unique_prices])
                row[store] = formatted
            else:
                row[store] = "N/A"

        if all_prices:
            row['Min Price (DZD)'] = format_price_dzd(min(all_prices))
            row['Max Price (DZD)'] = format_price_dzd(max(all_prices))
        else:
            row['Min Price (DZD)'] = "N/A"
            row['Max Price (DZD)'] = "N/A"

        row['Stores Count'] = stores_count
        matrix_rows.append(row)

    with open(matrix_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['Perfume Name'] + STORES + ['Min Price (DZD)', 'Max Price (DZD)', 'Stores Count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matrix_rows)

    print(f"Successfully generated price matrix CSV: {matrix_csv_path} ({len(matrix_rows)} rows)")

if __name__ == '__main__':
    build_csvs()
