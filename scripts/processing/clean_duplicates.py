import csv

csv_path = "ads_research.csv"

rows = []
seen = set()

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        # Clean quotes
        r["Store Name"] = r["Store Name"].replace('""', '"').strip('"')
        r["Product Name"] = r["Product Name"].replace('""', '"').strip('"')
        
        # Deduplicate by Ad Link or Landing Page
        key = (r["Ad Link"], r["Product Name"])
        if key not in seen:
            seen.add(key)
            rows.append(r)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Cleaned duplicates! {len(rows)} unique rows remaining.")
