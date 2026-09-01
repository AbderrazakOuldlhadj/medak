import csv

with open(r"c:\Users\msipc\Desktop\products\parfums\products_export_1 (1).csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)
    print("Total columns:", len(headers))
    for i, h in enumerate(headers):
        print(f"{i}: {h}")
    
    print("\n--- Example Row 1 ---")
    row1 = next(reader)
    for h, v in zip(headers, row1):
        if v:
            print(f"  {h}: {v}")

    print("\n--- Example Row 2 (Image row for same product) ---")
    row2 = next(reader)
    for h, v in zip(headers, row2):
        if v:
            print(f"  {h}: {v}")

