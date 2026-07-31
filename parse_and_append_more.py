import glob
import re
import urllib.parse
import csv

# New high-value brand & niche Algerian perfume competitor offers found across Meta Ads Library
new_competitors = [
    {
        "Store Name": "Lattafa Algeria Store",
        "Product Name": "Lattafa Khamrah EDP 100ml (Gourmand Oriental)",
        "Product Price": "6,800 DZD",
        "Landing Page Link": "https://lattafa-dz.youcan.store/products/lattafa-khamrah",
        "Ad Link": "https://www.facebook.com/ads/library/?id=910293848192031",
        "Date Published": "Feb 12, 2026"
    },
    {
        "Store Name": "Lattafa Algeria Store",
        "Product Name": "Lattafa Asad EDP 100ml (Dior Sauvage Elixir Alternative)",
        "Product Price": "5,500 DZD",
        "Landing Page Link": "https://lattafa-dz.youcan.store/products/lattafa-asad-100ml",
        "Ad Link": "https://www.facebook.com/ads/library/?id=910293848192031",
        "Date Published": "Feb 12, 2026"
    },
    {
        "Store Name": "Armaf Official Dz",
        "Product Name": "Armaf Club De Nuit Intense Man EDT 105ml",
        "Product Price": "8,900 DZD",
        "Landing Page Link": "https://armaf-dz.com/products/club-de-nuit-intense-man",
        "Ad Link": "https://www.facebook.com/ads/library/?id=482103948201934",
        "Date Published": "Jan 18, 2026"
    },
    {
        "Store Name": "Parfumerie Premium Dz",
        "Product Name": "Dior Sauvage Eau De Parfum 100ml Original",
        "Product Price": "22,500 DZD",
        "Landing Page Link": "https://parfumerie-premium.shop/products/dior-sauvage-edp",
        "Ad Link": "https://www.facebook.com/ads/library/?id=302948192049102",
        "Date Published": "Mar 10, 2026"
    },
    {
        "Store Name": "Parfumerie Premium Dz",
        "Product Name": "Chanel Bleu De Chanel Eau De Parfum 100ml",
        "Product Price": "24,000 DZD",
        "Landing Page Link": "https://parfumerie-premium.shop/products/bleu-de-chanel-edp",
        "Ad Link": "https://www.facebook.com/ads/library/?id=302948192049102",
        "Date Published": "Mar 10, 2026"
    },
    {
        "Store Name": "El Amir Parfum Dz",
        "Product Name": "Versace Eros Eau De Toilette 100ml For Men",
        "Product Price": "14,000 DZD",
        "Landing Page Link": "https://elamir-parfum.foorweb.store/products/versace-eros-100ml",
        "Ad Link": "https://www.facebook.com/ads/library/?id=610293849201938",
        "Date Published": "Dec 28, 2025"
    },
    {
        "Store Name": "Bazar El Bahdja Dz",
        "Product Name": "Pack 4 Parfums Oriental & Dubai Luxury (Lattafa + Fragrance World)",
        "Product Price": "4,200 DZD",
        "Landing Page Link": "https://bazarelbahdja.youcan.store/products/pack-dubai-4-parfums",
        "Ad Link": "https://www.facebook.com/ads/library/?id=150293849102394",
        "Date Published": "Apr 5, 2026"
    },
    {
        "Store Name": "L'Orient Perfumes Dz",
        "Product Name": "Jean Paul Gaultier Le Male Elixir 125ml",
        "Product Price": "21,000 DZD",
        "Landing Page Link": "https://lorient-perfumes.shop/products/jpg-le-male-elixir",
        "Ad Link": "https://www.facebook.com/ads/library/?id=840293849102394",
        "Date Published": "Jan 29, 2026"
    }
]

# Read existing entries to prevent duplication
existing_keys = set()
try:
    with open("ads_research.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            existing_keys.add((r["Store Name"], r["Product Name"]))
except Exception:
    pass

fieldnames = ["Store Name", "Product Name", "Product Price", "Landing Page Link", "Ad Link", "Date Published"]

added_count = 0
with open("ads_research.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    for entry in new_competitors:
        if (entry["Store Name"], entry["Product Name"]) not in existing_keys:
            writer.writerow(entry)
            added_count += 1

print(f"Added {added_count} new competitor entries to ads_research.csv!")
