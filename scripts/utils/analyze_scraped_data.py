import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\msipc\.gemini\antigravity-ide\brain\58560254-acba-49bf-8e1f-2bbf9072ba56\scratch\scraped_products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"Loaded {len(products)} products.")

# Inspect product details
has_multiple_variants = []
has_multiple_images = []
has_description = []

for p in products:
    details = p.get('product_details', {})
    variants = details.get('variants', [])
    images = details.get('images', [])
    desc = details.get('description', '')
    
    if len(variants) > 1:
        has_multiple_variants.append(p)
    if len(images) > 1:
        has_multiple_images.append(p)
    if desc and desc.strip():
        has_description.append(p)

print(f"Products with >1 variants: {len(has_multiple_variants)}")
print(f"Products with >1 images: {len(has_multiple_images)}")
print(f"Products with description: {len(has_description)}")

if has_multiple_variants:
    print("\n--- Example of product with multiple variants ---")
    p = has_multiple_variants[0]
    print("Title:", p['product_details'].get('title'))
    print("Options:", p['product_details'].get('options'))
    print("Variants:", json.dumps(p['product_details'].get('variants'), indent=2, ensure_ascii=False))

print("\n--- Example of standard product ---")
p = products[0]
print("Title:", p['product_details'].get('title'))
print("Price:", p['product_details'].get('price'))
print("Compare at price:", p['product_details'].get('compare_at_price'))
print("Images count:", len(p['product_details'].get('images', [])))
print("Images:", p['product_details'].get('images', []))
print("Description:", p['product_details'].get('description'))
print("Collections:", p['collections'])

