import csv
import re

def parse_price(price_str):
    # Extract digits from price string e.g. "24,000 DZD" -> 24000
    digits = re.sub(r'[^\d]', '', price_str)
    return int(digits) if digits else 0

def sort_and_save_csv(input_file="ads_research.csv"):
    rows = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    # Sort rows by numeric price High to Low (descending)
    rows.sort(key=lambda r: parse_price(r["Product Price"]), reverse=True)

    fieldnames = ["Store Name", "Product Name", "Product Price", "Landing Page Link", "Ad Link", "Date Published"]

    with open(input_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Successfully sorted {len(rows)} entries in {input_file} from highest to lowest price!")
    return rows

if __name__ == "__main__":
    sort_and_save_csv()
