import csv
import re

def parse_price(price_str):
    digits = re.sub(r'[^\d]', '', price_str)
    return int(digits) if digits else 0

gender_map = {
    "Chanel Bleu De Chanel Eau De Parfum 100ml": "Homme",
    "Dior Sauvage Eau De Parfum 100ml Original": "Homme",
    "Jean Paul Gaultier Le Male Elixir 125ml": "Homme",
    "YSL Yves Saint Laurent Black Opium EDP 90ml": "Femme",
    "Cartier Déclaration Eau De Toilette (50ml / 100ml)": "Homme",
    "Givenchy L'Interdit Eau de Parfum 80ml (Original Tester)": "Femme",
    "Versace Eros Eau De Toilette 100ml For Men": "Homme",
    "Hugo Boss The Scent For Him Eau de Toilette 100ml": "Homme",
    "Burberry Mr Burberry Coffret (Edt 100ml + Shower Gel)": "Homme",
    "Armaf Club De Nuit Intense Man EDT 105ml": "Homme",
    "Calvin Klein CK One Eau de Toilette 200ml Unisex": "Unisex",
    "Lattafa Khamrah EDP 100ml (Gourmand Oriental)": "Unisex",
    "Lattafa Asad EDP 100ml (Dior Sauvage Elixir Alternative)": "Homme",
    "Offre Duo Hommes / Duo Femmes Parfums Luxe": "Homme / Femme",
    "Pack 4 Parfums Oriental & Dubai Luxury (Lattafa + Fragrance World)": "Unisex",
    "Pack Prestige 3 Parfums Homme (Givenchy Gentleman + YSL Y + Sauvage)": "Homme",
    "Pack El Ihram Parfums & Soins": "Homme",
    "Hugo Boss Bottled Intense 100ml Eau De Parfum": "Homme",
    "Pack Cupid Perfume Special Collection": "Unisex",
    "Pack 5 Parfums Homme Top Ventes (YSL, BOSS, Sauvage, Terre d'Hermès)": "Homme",
    "Pack Cupidon (Parfum + Crème + Déodorant)": "Homme",
    "Pack 3 Parfums Tester Luxe au Choix (58 Wilaya COD)": "Unisex"
}

rows = []
with open("ads_research.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        p_name = r["Product Name"]
        gender = gender_map.get(p_name, "Homme" if "homme" in p_name.lower() or "man" in p_name.lower() or "him" in p_name.lower() else ("Femme" if "femme" in p_name.lower() or "her" in p_name.lower() or "women" in p_name.lower() or "opium" in p_name.lower() or "interdit" in p_name.lower() else "Unisex"))
        r["Gender"] = gender
        rows.append(r)

# Ensure sorting High to Low Price
rows.sort(key=lambda r: parse_price(r["Product Price"]), reverse=True)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open("ads_research.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print("Successfully added 'Gender' column and preserved High-to-Low price sorting!")
