import os
import sys
import json
import csv
import re

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TARGET_JSON = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
IMG_BASE_DIR = os.path.join(ROOT_DIR, "assets", "product_images")
OUTPUT_CSV = os.path.join(ROOT_DIR, "data", "processed", "shopify_perfumes_with_images.csv")

HEADERS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option1 Linked To", "Option2 Name", "Option2 Value", "Option2 Linked To",
    "Option3 Name", "Option3 Value", "Option3 Linked To", "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
    "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable", "Unit Price Total Measure",
    "Unit Price Total Measure Unit", "Unit Price Base Measure", "Unit Price Base Measure Unit", "Variant Barcode",
    "Image Src", "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description",
    "Flavor (product.metafields.shopify.flavor)", "Variant Image", "Variant Weight Unit", "Variant Tax Code",
    "Cost per item", "Status"
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

def format_price(val_str):
    if not val_str:
        return ""
    clean = str(val_str).replace(',', '').replace('DZD', '').replace('DA', '').strip()
    try:
        val = float(clean)
        return f"{val:.2f}"
    except Exception:
        return clean

def sort_images(img_list):
    """
    Sort images logically:
    1. bottle.webp
    2. both.webp
    3. package.webp
    4. image_*.webp (sorted by index)
    5. other .webp
    6. raw_*.jpg/png / other files
    """
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

def build_shopify_export():
    if not os.path.exists(TARGET_JSON):
        print(f"Error: {TARGET_JSON} not found.")
        return

    with open(TARGET_JSON, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    output_rows = []
    processed_count = 0

    for item in perfumes:
        full_name = item['full_name']
        brand = item.get('brand', '').strip()
        gros_price = item.get('gros_price', '')
        
        folder_name = clean_folder_name(full_name)
        folder_path = os.path.join(IMG_BASE_DIR, folder_name)
        
        if not os.path.exists(folder_path):
            continue
            
        all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))]
        if not all_files:
            continue
            
        sorted_files = sort_images(all_files)
        
        handle = slugify(full_name)
        if not handle:
            handle = f"product-{item.get('row', '0')}"
            
        title = full_name
        description = f"<p>{title}</p>"
        vendor = brand or "Parfums DZ"
        product_category = "Health & Beauty > Personal Care > Cosmetics > Perfumes & Fragrances"
        product_type = "Perfume"
        tags = f"Parfum DZ, {vendor}"
        published = "true"
        formatted_price = format_price(gros_price)
        
        # Build relative paths for image references
        img_paths = [f"assets/product_images/{folder_name}/{img_file}" for img_file in sorted_files]
        first_img = img_paths[0]
        
        # Main Product Row (Row 1 for this product)
        main_row = {
            "Handle": handle,
            "Title": title,
            "Body (HTML)": description,
            "Vendor": vendor,
            "Product Category": product_category,
            "Type": product_type,
            "Tags": tags,
            "Published": published,
            "Option1 Name": "Title",
            "Option1 Value": "Default Title",
            "Option1 Linked To": "",
            "Option2 Name": "",
            "Option2 Value": "",
            "Option2 Linked To": "",
            "Option3 Name": "",
            "Option3 Value": "",
            "Option3 Linked To": "",
            "Variant SKU": "",
            "Variant Grams": "0.0",
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": "100",
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": formatted_price,
            "Variant Compare At Price": "",
            "Variant Requires Shipping": "true",
            "Variant Taxable": "false",
            "Unit Price Total Measure": "",
            "Unit Price Total Measure Unit": "",
            "Unit Price Base Measure": "",
            "Unit Price Base Measure Unit": "",
            "Variant Barcode": "",
            "Image Src": first_img,
            "Image Position": "1",
            "Image Alt Text": title,
            "Gift Card": "false",
            "SEO Title": title,
            "SEO Description": title,
            "Flavor (product.metafields.shopify.flavor)": "",
            "Variant Image": first_img,
            "Variant Weight Unit": "kg",
            "Variant Tax Code": "",
            "Cost per item": "",
            "Status": "active"
        }
        output_rows.append(main_row)
        
        # Additional Image Rows (Positions 2+)
        for img_idx, img_src in enumerate(img_paths[1:], start=2):
            img_row = {h: "" for h in HEADERS}
            img_row["Handle"] = handle
            img_row["Image Src"] = img_src
            img_row["Image Position"] = str(img_idx)
            img_row["Image Alt Text"] = title
            output_rows.append(img_row)
            
        processed_count += 1

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in output_rows:
            writer.writerow(r)

    print(f"Successfully generated Shopify CSV: {OUTPUT_CSV}")
    print(f"Total Unique Products Exported: {processed_count}")
    print(f"Total CSV Rows (Products + Images): {len(output_rows)}")

if __name__ == '__main__':
    build_shopify_export()
