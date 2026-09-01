import sys
import os
import json
import base64
import urllib.parse
import re
import urllib.request
import concurrent.futures
import csv
import time

sys.stdout.reconfigure(encoding='utf-8')

# 1. Read base content
content_path = r"C:\Users\msipc\.gemini\antigravity-ide\brain\58560254-acba-49bf-8e1f-2bbf9072ba56\.system_generated\steps\5\content.md"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'decodeURIComponent\(atob\(["\']([A-Za-z0-9+/=]+)["\']\)\)', text)
decoded_bytes = base64.b64decode(matches[0])
decoded_str = urllib.parse.unquote(decoded_bytes.decode('utf-8', errors='ignore'))
data = json.loads(decoded_str)

collections = data.get('collections', [])
target_cols = {
    'Best-Seller': 'الأكثر طلبا - Best Seller',
    'parfum-european': 'العطور الأوروبية'
}

products_by_id = {}
for col in collections:
    col_slug = col.get('slug')
    if col_slug in target_cols:
        col_name = target_cols[col_slug]
        for item in col.get('items', []):
            p_id = item.get('id')
            if p_id not in products_by_id:
                products_by_id[p_id] = {
                    'item_summary': item,
                    'collections': [col_name]
                }
            else:
                if col_name not in products_by_id[p_id]['collections']:
                    products_by_id[p_id]['collections'].append(col_name)

print(f"Total unique target products: {len(products_by_id)}")

def fetch_product_details(p_id, p_info):
    slug = p_info['item_summary'].get('slug')
    url = f"https://perfumecorner.myecomstore.net/products/{slug}"
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    
    result = {
        'id': p_id,
        'slug': slug,
        'url': url,
        'collections': p_info['collections'],
        'summary': p_info['item_summary'],
        'product_details': None,
        'success': False
    }
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8')
            p_matches = re.findall(r'decodeURIComponent\(atob\(["\']([A-Za-z0-9+/=]+)["\']\)\)', html)
            if p_matches:
                decoded_b = base64.b64decode(p_matches[0])
                decoded_s = urllib.parse.unquote(decoded_b.decode('utf-8', errors='ignore'))
                prod_data = json.loads(decoded_s)
                product = prod_data.get('product')
                if product:
                    result['product_details'] = product
                    result['success'] = True
                    return result
        except Exception as e:
            time.sleep(1)
            
    return result

print("Fetching product details...")
scraped_data = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_product_details, p_id, p_info): p_id for p_id, p_info in products_by_id.items()}
    for future in concurrent.futures.as_completed(futures):
        res = future.result()
        scraped_data.append(res)

print(f"Scraped {len(scraped_data)} products successfully.")

# Read exact headers from template
template_path = r"c:\Users\msipc\Desktop\products\parfums\products_export_1 (1).csv"
with open(template_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)

def slugify(text):
    # normalize handle
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def format_price(val):
    if val is None or val == '' or val == 0:
        return ""
    try:
        return f"{float(val):.2f}"
    except:
        return str(val)

output_rows = []

for item in scraped_data:
    p_id = item['id']
    slug = item['slug']
    collections_list = item['collections']
    summary = item['summary']
    details = item.get('product_details') or {}
    
    title = (details.get('title') or summary.get('title') or '').strip()
    # clean extra whitespace inside title
    title = re.sub(r'\s+', ' ', title)
    
    # Handle / Slug
    handle = slugify(title)
    if not handle or len(handle) < 3:
        handle = slugify(slug) or f"product-{p_id}"
        
    description = details.get('description', '') or ''
    # If description is empty, fallback to clean paragraph with title
    if not description.strip():
        description = f"<p>{title}</p>"
        
    vendor = "perfume.corner"
    product_category = "Health & Beauty > Personal Care > Cosmetics > Perfumes & Fragrances"
    product_type = "Perfume"
    tags = ", ".join(collections_list)
    published = "true"
    
    # Prices
    price_val = details.get('price') if details.get('price') is not None else summary.get('price', 0)
    compare_at_val = details.get('compare_at_price') if details.get('compare_at_price') is not None else summary.get('compare_at_price', 0)
    
    variant_price = format_price(price_val)
    variant_compare_at = format_price(compare_at_val) if compare_at_val and float(compare_at_val) > float(price_val or 0) else ""
    
    # Images
    images = details.get('images') or []
    if not images and details.get('thumbnail'):
        images = [details.get('thumbnail')]
    if not images and summary.get('thumbnail'):
        images = [summary.get('thumbnail')]
        
    # Ensure no duplicates in images while preserving order
    unique_images = []
    for img in images:
        if img and img not in unique_images:
            unique_images.append(img)
            
    variants = details.get('variants') or []
    options = details.get('options') or []
    
    # If there are actual multiple variants
    if len(variants) > 1:
        # Determine option names
        opt1_name = options[0].get('name', 'Option 1') if len(options) > 0 else 'Title'
        opt2_name = options[1].get('name', '') if len(options) > 1 else ''
        opt3_name = options[2].get('name', '') if len(options) > 2 else ''
        
        for v_idx, var in enumerate(variants):
            var_title = (var.get('title') or f"Variant {v_idx+1}").strip()
            var_options = var.get('options') or []
            
            v_opt1_val = var_options[0] if len(var_options) > 0 else var_title
            v_opt2_val = var_options[1] if len(var_options) > 1 else ""
            v_opt3_val = var_options[2] if len(var_options) > 2 else ""
            
            v_price = format_price(var.get('price', price_val))
            v_compare_at = format_price(var.get('compare_at_price', compare_at_val)) if var.get('compare_at_price') and float(var.get('compare_at_price')) > float(var.get('price', price_val)) else ""
            v_image = var.get('image', '')
            v_sku = var.get('sku', '')
            
            # If first variant of product
            if v_idx == 0:
                first_img = unique_images[0] if len(unique_images) > 0 else ""
                row = {
                    "Handle": handle,
                    "Title": title,
                    "Body (HTML)": description,
                    "Vendor": vendor,
                    "Product Category": product_category,
                    "Type": product_type,
                    "Tags": tags,
                    "Published": published,
                    "Option1 Name": opt1_name,
                    "Option1 Value": v_opt1_val,
                    "Option1 Linked To": "",
                    "Option2 Name": opt2_name,
                    "Option2 Value": v_opt2_val,
                    "Option2 Linked To": "",
                    "Option3 Name": opt3_name,
                    "Option3 Value": v_opt3_val,
                    "Option3 Linked To": "",
                    "Variant SKU": v_sku,
                    "Variant Grams": "0.0",
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": "100",
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": v_price,
                    "Variant Compare At Price": v_compare_at,
                    "Variant Requires Shipping": "true",
                    "Variant Taxable": "false",
                    "Unit Price Total Measure": "",
                    "Unit Price Total Measure Unit": "",
                    "Unit Price Base Measure": "",
                    "Unit Price Base Measure Unit": "",
                    "Variant Barcode": "",
                    "Image Src": first_img,
                    "Image Position": "1" if first_img else "",
                    "Image Alt Text": title if first_img else "",
                    "Gift Card": "false",
                    "SEO Title": title,
                    "SEO Description": title,
                    "Flavor (product.metafields.shopify.flavor)": "",
                    "Variant Image": v_image or first_img,
                    "Variant Weight Unit": "kg",
                    "Variant Tax Code": "",
                    "Cost per item": "",
                    "Status": "active"
                }
                output_rows.append(row)
            else:
                row = {
                    "Handle": handle,
                    "Title": "",
                    "Body (HTML)": "",
                    "Vendor": "",
                    "Product Category": "",
                    "Type": "",
                    "Tags": "",
                    "Published": "",
                    "Option1 Name": "",
                    "Option1 Value": v_opt1_val,
                    "Option1 Linked To": "",
                    "Option2 Name": "",
                    "Option2 Value": v_opt2_val,
                    "Option2 Linked To": "",
                    "Option3 Name": "",
                    "Option3 Value": v_opt3_val,
                    "Option3 Linked To": "",
                    "Variant SKU": v_sku,
                    "Variant Grams": "0.0",
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": "100",
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Price": v_price,
                    "Variant Compare At Price": v_compare_at,
                    "Variant Requires Shipping": "true",
                    "Variant Taxable": "false",
                    "Unit Price Total Measure": "",
                    "Unit Price Total Measure Unit": "",
                    "Unit Price Base Measure": "",
                    "Unit Price Base Measure Unit": "",
                    "Variant Barcode": "",
                    "Image Src": "",
                    "Image Position": "",
                    "Image Alt Text": "",
                    "Gift Card": "",
                    "SEO Title": "",
                    "SEO Description": "",
                    "Flavor (product.metafields.shopify.flavor)": "",
                    "Variant Image": v_image,
                    "Variant Weight Unit": "kg",
                    "Variant Tax Code": "",
                    "Cost per item": "",
                    "Status": ""
                }
                output_rows.append(row)
                
        # Now add additional images (position 2+)
        for img_idx, img_url in enumerate(unique_images[1:], start=2):
            row = {h: "" for h in headers}
            row["Handle"] = handle
            row["Image Src"] = img_url
            row["Image Position"] = str(img_idx)
            row["Image Alt Text"] = title
            output_rows.append(row)
            
    else:
        # Single variant (Default Title)
        first_img = unique_images[0] if len(unique_images) > 0 else ""
        sku = variants[0].get('sku', '') if variants else ""
        
        row = {
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
            "Variant SKU": sku,
            "Variant Grams": "0.0",
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": "100",
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": variant_price,
            "Variant Compare At Price": variant_compare_at,
            "Variant Requires Shipping": "true",
            "Variant Taxable": "false",
            "Unit Price Total Measure": "",
            "Unit Price Total Measure Unit": "",
            "Unit Price Base Measure": "",
            "Unit Price Base Measure Unit": "",
            "Variant Barcode": "",
            "Image Src": first_img,
            "Image Position": "1" if first_img else "",
            "Image Alt Text": title if first_img else "",
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
        output_rows.append(row)
        
        # Additional images
        for img_idx, img_url in enumerate(unique_images[1:], start=2):
            img_row = {h: "" for h in headers}
            img_row["Handle"] = handle
            img_row["Image Src"] = img_url
            img_row["Image Position"] = str(img_idx)
            img_row["Image Alt Text"] = title
            output_rows.append(img_row)

# Save to CSV
output_csv_path = r"c:\Users\msipc\Desktop\products\parfums\shopify_perfumes_export.csv"
with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for r in output_rows:
        writer.writerow(r)

print(f"\nSuccessfully created Shopify import CSV: {output_csv_path}")
print(f"Total CSV Rows: {len(output_rows)}")
print(f"Total Unique Products: {len(scraped_data)}")

