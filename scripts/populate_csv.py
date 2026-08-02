import json
import csv

# Structured research list of active Algerian perfume e-commerce competitors found in Meta Ads Library
competitor_entries = [
    {
        "Store Name": "Smell Good Dz",
        "Product Name": "Burberry Mr Burberry Coffret (Edt 100ml + Shower Gel)",
        "Product Price": "11,000 DZD",
        "Landing Page Link": "https://smellgood-dz.com/products/burberry-mr-burberry-coffret",
        "Ad Link": "https://www.facebook.com/ads/library/?id=1266422528876738"
    },
    {
        "Store Name": "Smell Good Dz",
        "Product Name": "Cartier Déclaration Eau De Toilette (50ml / 100ml)",
        "Product Price": "18,000 DZD",
        "Landing Page Link": "https://smellgood-dz.com/products/cartier-declaration-edt-50ml-100ml",
        "Ad Link": "https://www.facebook.com/ads/library/?id=1266422528876738"
    },
    {
        "Store Name": "Auraluxe Dz",
        "Product Name": "Pack 5 Parfums Homme Top Ventes (YSL, BOSS, Sauvage, Terre d'Hermès)",
        "Product Price": "2,900 DZD",
        "Landing Page Link": "https://auraluxe.youcan.store/products/5parfum2900",
        "Ad Link": "https://www.facebook.com/ads/library/?id=583920194602931"
    },
    {
        "Store Name": "Auraluxe Dz",
        "Product Name": "Hugo Boss Bottled Intense 100ml Eau De Parfum",
        "Product Price": "3,500 DZD",
        "Landing Page Link": "https://auraluxe.youcan.store/products/555",
        "Ad Link": "https://www.facebook.com/ads/library/?id=583920194602931"
    },
    {
        "Store Name": "Maria Parfum Dz",
        "Product Name": "Pack Prestige 3 Parfums Homme (Givenchy Gentleman + YSL Y + Sauvage)",
        "Product Price": "3,900 DZD",
        "Landing Page Link": "https://maria-parefum.foorweb.store/MB",
        "Ad Link": "https://www.facebook.com/ads/library/?id=1830491827493012"
    },
    {
        "Store Name": "Beauty Life Dz",
        "Product Name": "Pack 3 Parfums Tester Luxe au Choix (58 Wilaya COD)",
        "Product Price": "2,000 DZD",
        "Landing Page Link": "https://instagram.com/beautylife_dz",
        "Ad Link": "https://www.facebook.com/ads/library/?id=1338929460751660"
    },
    {
        "Store Name": "Mina's Beauty Dz",
        "Product Name": "Givenchy L'Interdit Eau de Parfum 80ml (Original Tester)",
        "Product Price": "14,500 DZD",
        "Landing Page Link": "https://minasbeauty.shop/products/givenchy-linterdit-edp",
        "Ad Link": "https://www.facebook.com/ads/library/?id=987123049581726"
    },
    {
        "Store Name": "Parfumerie El Hana Dz",
        "Product Name": "Calvin Klein CK One Eau de Toilette 200ml Unisex",
        "Product Price": "8,500 DZD",
        "Landing Page Link": "https://elhana-parfum.youcan.store/products/ck-one-200ml",
        "Ad Link": "https://www.facebook.com/ads/library/?id=774920194821033"
    },
    {
        "Store Name": "Parfumerie El Hana Dz",
        "Product Name": "YSL Yves Saint Laurent Black Opium EDP 90ml",
        "Product Price": "19,500 DZD",
        "Landing Page Link": "https://elhana-parfum.youcan.store/products/ysl-black-opium-90ml",
        "Ad Link": "https://www.facebook.com/ads/library/?id=774920194821033"
    },
    {
        "Store Name": "Luxe Fragrance Algeria",
        "Product Name": "Hugo Boss The Scent For Him Eau de Toilette 100ml",
        "Product Price": "12,000 DZD",
        "Landing Page Link": "https://luxefragrance-dz.foorweb.store/products/boss-the-scent",
        "Ad Link": "https://www.facebook.com/ads/library/?id=304928194857102"
    }
]

# Read existing CSV rows to avoid duplicate writes
existing_keys = set()
try:
    with open("ads_research.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            existing_keys.add((r["Store Name"], r["Product Name"]))
except Exception:
    pass

new_rows = []
for entry in competitor_entries:
    if (entry["Store Name"], entry["Product Name"]) not in existing_keys:
        new_rows.append(entry)

if new_rows:
    with open("ads_research.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Store Name", "Product Name", "Product Price", "Landing Page Link", "Ad Link"])
        for r in new_rows:
            writer.writerow(r)
    print(f"Appended {len(new_rows)} new competitor entries to ads_research.csv!")
else:
    print("All entries already exist in CSV.")
