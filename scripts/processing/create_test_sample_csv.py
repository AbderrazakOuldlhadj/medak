import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

input_csv_path = r"c:\Users\msipc\Desktop\products\parfums\shopify_perfumes_export.csv"
output_csv_path = r"c:\Users\msipc\Desktop\products\parfums\shopify_perfumes_sample_10.csv"

with open(input_csv_path, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    all_rows = list(reader)

# Find first 10 unique product handles
first_10_handles = []
for r in all_rows:
    handle = r.get('Handle')
    if handle and handle not in first_10_handles:
        first_10_handles.append(handle)
        if len(first_10_handles) == 10:
            break

# Collect all rows belonging to these 10 handles
sample_rows = [r for r in all_rows if r.get('Handle') in first_10_handles]

with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for r in sample_rows:
        writer.writerow(r)

print(f"Created sample CSV: {output_csv_path}")
print(f"Total Unique Products: {len(first_10_handles)}")
print(f"Total Rows (with image positions): {len(sample_rows)}")

print("\n--- The 10 Products Included ---")
count = 0
for r in sample_rows:
    if r.get('Title'):
        count += 1
        print(f"{count:2d}. {r.get('Title')} | Price: {r.get('Variant Price')} DZD (Compare: {r.get('Variant Compare At Price') or 'None'}) | Handle: {r.get('Handle')}")

