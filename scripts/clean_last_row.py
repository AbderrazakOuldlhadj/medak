import csv

csv_path = "ads_research.csv"

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        r["Store Name"] = r["Store Name"].replace('""', '"').strip('"')
        r["Product Name"] = r["Product Name"].replace('""', '"').strip('"')
        if r["Ad Link"] == "https://www.facebook.com/ads/library/?id=1857703455595685":
            r["Store Name"] = 'Pafen DZ "Parfum Original"'
            r["Product Name"] = "Emmanuelle Jane Luxury Collection"
            r["Product Price"] = "41,000 DZD"
        rows.append(r)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print("Cleaned last row formatting.")
