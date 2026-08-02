import csv

csv_path = "ads_research.csv"

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        # Clean quotes in store names
        r["Store Name"] = r["Store Name"].replace('""', '"').strip('"')
        r["Product Name"] = r["Product Name"].replace('""', '"').strip('"')
        rows.append(r)

# Deduplicate
unique_rows = []
seen = set()
for r in rows:
    key = (r["Store Name"], r["Product Name"], r["Ad Link"])
    if key not in seen:
        seen.add(key)
        unique_rows.append(r)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in unique_rows:
        writer.writerow(r)

print("Cleaned ads_research.csv successfully!")
