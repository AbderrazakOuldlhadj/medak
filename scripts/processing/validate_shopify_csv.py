import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

csv_path = r"c:\Users\msipc\Desktop\products\parfums\shopify_perfumes_export.csv"
template_path = r"c:\Users\msipc\Desktop\products\parfums\products_export_1 (1).csv"

with open(template_path, "r", encoding="utf-8") as f:
    template_headers = next(csv.reader(f))

with open(csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    actual_headers = next(reader)
    rows = list(reader)

print(f"Header match: {template_headers == actual_headers}")
print(f"Header count: {len(actual_headers)}")
print(f"Total Rows in generated CSV: {len(rows)}")

# Check distinct handles
handles = set(r[0] for r in rows if r[0])
print(f"Total unique products (Handles): {len(handles)}")

# Inspect first 15 rows
print("\n--- SAMPLE ROWS (First 15) ---")
for i, r in enumerate(rows[:15]):
    handle = r[0]
    title = r[1]
    price = r[23]
    compare = r[24]
    tags = r[6]
    img = r[32]
    img_pos = r[33]
    print(f"Row {i+1:2d} | Handle: {handle[:30]:<30} | Pos: {img_pos:2s} | Price: {price:<8} | Title: {title[:35]:<35} | Tags: {tags}")

# Check image URLs count
img_count = sum(1 for r in rows if r[32])
print(f"\nTotal image references: {img_count}")

# Check any missing prices or images
missing_price = [r[0] for r in rows if r[1] and not r[23]]
missing_img = [r[0] for r in rows if r[1] and not r[32]]
print(f"Products with missing price: {len(missing_price)}")
print(f"Products with missing first image: {len(missing_img)}")

