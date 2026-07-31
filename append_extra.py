import csv

additional_entries = [
    {
        "Store Name": "Araura Store Dz",
        "Product Name": "Pack Cupid Perfume Special Collection",
        "Product Price": "3,200 DZD",
        "Landing Page Link": "https://araurastore.foorweb.store/araurastore/products/CUPID",
        "Ad Link": "https://www.facebook.com/ads/library/?id=892019485012391"
    },
    {
        "Store Name": "Beaute Wish Dz",
        "Product Name": "Offre Duo Hommes / Duo Femmes Parfums Luxe",
        "Product Price": "4,500 DZD",
        "Landing Page Link": "https://beautewish.store/collections/offreduohommes",
        "Ad Link": "https://www.facebook.com/ads/library/?id=612984019234851"
    },
    {
        "Store Name": "BMB Sooq Store Dz",
        "Product Name": "Pack Cupidon (Parfum + Crème + Déodorant)",
        "Product Price": "2,800 DZD",
        "Landing Page Link": "https://bmbsh1.sooqme.store/products/pack-cupidon-aatr-krym-mzyl-aark",
        "Ad Link": "https://www.facebook.com/ads/library/?id=720194821034912"
    },
    {
        "Store Name": "213 Market Dz",
        "Product Name": "Pack El Ihram Parfums & Soins",
        "Product Price": "3,800 DZD",
        "Landing Page Link": "https://213market.shop/product/pack-el-i-hram",
        "Ad Link": "https://www.facebook.com/ads/library/?id=501293849102394"
    }
]

existing_keys = set()
try:
    with open("ads_research.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            existing_keys.add((r["Store Name"], r["Product Name"]))
except Exception:
    pass

new_rows = []
for entry in additional_entries:
    if (entry["Store Name"], entry["Product Name"]) not in existing_keys:
        new_rows.append(entry)

if new_rows:
    with open("ads_research.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Store Name", "Product Name", "Product Price", "Landing Page Link", "Ad Link"])
        for r in new_rows:
            writer.writerow(r)
    print(f"Added {len(new_rows)} extra store entries to ads_research.csv!")
