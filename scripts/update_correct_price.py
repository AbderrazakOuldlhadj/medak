import csv

csv_path = "ads_research.csv"

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r["Ad Link"] == "https://www.facebook.com/ads/library/?id=1701177097798374":
            r["Product Price"] = "12,500 DZD"
        rows.append(r)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print("Updated ads_research.csv with exact verified price: 12,500 DZD")
