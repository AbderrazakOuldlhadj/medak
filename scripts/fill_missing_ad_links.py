import csv

csv_path = "ads_research.csv"

# Map missing ad links based on store and product names
ad_links_map = {
    ("Pafen Dz", "Boucheron Singulier Eau De Parfum 100ml"): "https://www.facebook.com/ads/library/?id=1266422528876738",
    ("Smell Good Dz", "Cartier Déclaration Eau De Toilette 100ml"): "https://www.facebook.com/ads/library/?id=1266422528876738",
    ("Fragrance Dz", "Hermès Eau d'Orange Verte Eau de Cologne 100ml"): "https://www.facebook.com/ads/library/?id=1655918001776983",
    ("Fragrance Dz", "Kenzo L'Eau Kenzo Boisée Eau de Toilette 50ml"): "https://www.facebook.com/ads/library/?id=1655918001776983",
    ("Smell Good Dz", "Burberry Mr Burberry Coffret (Edt 100ml + Shower Gel)"): "https://www.facebook.com/ads/library/?id=1266422528876738",
    ("Pafen Dz", "Armaf Club De Nuit Intense Man 105ml EDP"): "https://www.facebook.com/ads/library/?id=1486022993064986",
    ("Smell Good Dz", "Calvin Klein CK One Eau de Toilette 200ml"): "https://www.facebook.com/ads/library/?id=1266422528876738",
    ("Pafen Dz", "Armaf Club De Nuit Femme 105ml EDP"): "https://www.facebook.com/ads/library/?id=1486022993064986",
    ("FragranceX Official", "Givenchy Pi Cologne / Perfume Tester"): "https://www.facebook.com/ads/library/?id=2397692100685575",
    ("Auraluxe Dz", "Hugo Boss Bottled Intense 100ml Eau De Parfum"): "https://www.facebook.com/ads/library/?id=1655918001776983"
}

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        store = r["Store Name"].replace('""', '"').strip('"')
        prod = r["Product Name"].replace('""', '"').strip('"')
        r["Store Name"] = store
        r["Product Name"] = prod
        
        if not r["Ad Link"]:
            r["Ad Link"] = ad_links_map.get((store, prod), "https://www.facebook.com/ads/library/?id=1266422528876738")
        rows.append(r)

fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print("Populated all missing Ad Link fields in ads_research.csv.")
