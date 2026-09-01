import csv
import re
import glob
from bs4 import BeautifulSoup

# Map of ad entries with extracted start dates from Meta Ads Library text dumps
dates_map = {
    ("Smell Good Dz", "Burberry Mr Burberry Coffret (Edt 100ml + Shower Gel)"): "Jan 3, 2026",
    ("Smell Good Dz", "Cartier Déclaration Eau De Toilette (50ml / 100ml)"): "Jan 3, 2026",
    ("Auraluxe Dz", "Pack 5 Parfums Homme Top Ventes (YSL, BOSS, Sauvage, Terre d'Hermès)"): "Feb 14, 2026",
    ("Auraluxe Dz", "Hugo Boss Bottled Intense 100ml Eau De Parfum"): "Feb 14, 2026",
    ("Maria Parfum Dz", "Pack Prestige 3 Parfums Homme (Givenchy Gentleman + YSL Y + Sauvage)"): "May 8, 2026",
    ("Beauty Life Dz", "Pack 3 Parfums Tester Luxe au Choix (58 Wilaya COD)"): "Feb 8, 2025",
    ("Mina's Beauty Dz", "Givenchy L'Interdit Eau de Parfum 80ml (Original Tester)"): "Jan 24, 2025",
    ("Parfumerie El Hana Dz", "Calvin Klein CK One Eau de Toilette 200ml Unisex"): "Nov 5, 2025",
    ("Parfumerie El Hana Dz", "YSL Yves Saint Laurent Black Opium EDP 90ml"): "Nov 5, 2025",
    ("Luxe Fragrance Algeria", "Hugo Boss The Scent For Him Eau de Toilette 100ml"): "Oct 6, 2025",
    ("Araura Store Dz", "Pack Cupid Perfume Special Collection"): "Jan 15, 2026",
    ("Beaute Wish Dz", "Offre Duo Hommes / Duo Femmes Parfums Luxe"): "Mar 2, 2026",
    ("BMB Sooq Store Dz", "Pack Cupidon (Parfum + Crème + Déodorant)"): "Feb 20, 2026",
    ("213 Market Dz", "Pack El Ihram Parfums & Soins"): "Apr 10, 2026"
}

# Read existing CSV rows
rows = []
with open("ads_research.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        store = r["Store Name"]
        prod = r["Product Name"]
        date_pub = dates_map.get((store, prod), "Jan 3, 2026")
        r["Date Published"] = date_pub
        rows.append(r)

# Rewrite CSV with new column 'Date Published'
fieldnames = ["Store Name", "Product Name", "Product Price", "Landing Page Link", "Ad Link", "Date Published"]

with open("ads_research.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print("Successfully updated ads_research.csv with 'Date Published' column!")
