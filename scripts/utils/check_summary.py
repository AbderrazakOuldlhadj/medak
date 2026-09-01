import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

csv_path = r"c:\Users\msipc\Desktop\products\parfums\shopify_perfumes_export.csv"

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    products = [r for r in reader if r['Title']]

print(f"Total Products loaded: {len(products)}")

best_seller_count = sum(1 for p in products if 'الأكثر طلبا - Best Seller' in p['Tags'])
european_count = sum(1 for p in products if 'العطور الأوروبية' in p['Tags'])
both_count = sum(1 for p in products if 'الأكثر طلبا - Best Seller' in p['Tags'] and 'العطور الأوروبية' in p['Tags'])

print(f"Products tagged 'الأكثر طلبا - Best Seller': {best_seller_count}")
print(f"Products tagged 'العطور الأوروبية': {european_count}")
print(f"Products in both: {both_count}")

# Check price ranges
prices = [float(p['Variant Price']) for p in products if p['Variant Price']]
print(f"Price range: {min(prices):.2f} DZD - {max(prices):.2f} DZD")

# Check compare at price count
has_compare = sum(1 for p in products if p['Variant Compare At Price'])
print(f"Products with Compare At Price: {has_compare}")

# Print 10 sample products
print("\n--- SAMPLE PRODUCTS ---")
for i, p in enumerate(products[:10], 1):
    print(f"{i:2d}. [{p['Tags']}] {p['Title']} -> Price: {p['Variant Price']} DZD (Compare: {p['Variant Compare At Price'] or 'None'}) | Handle: {p['Handle']}")

