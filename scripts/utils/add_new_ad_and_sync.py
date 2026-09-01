import csv
import subprocess

new_entry = {
    "Store Name": 'Pafen DZ "Parfum Original"',
    "Product Name": "Pack Armaf Club de Nuit Intense Man (Parfum + Déodorant DEO)",
    "Product Price": "8,900 DZD",
    "Gender": "Homme",
    "Landing Page Link": "https://pafen-dz.com/order/4223-pack-promo-club-de-nuit",
    "Ad Link": "https://www.facebook.com/ads/library/?id=1701177097798374",
    "Date Published": "May 22, 2026"
}

csv_path = "ads_research.csv"

# Read existing rows
rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# Check duplicate
existing_links = {r["Ad Link"] for r in rows}
rows.append(new_entry)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Appended new ad link entry to {csv_path}!")
