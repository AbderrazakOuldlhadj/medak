import csv
import subprocess

def add_and_sync_record(new_record, csv_path="ads_research.csv"):
    rows = []
    # Read existing rows
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception:
        pass

    # Avoid duplicate exact product + store
    existing_keys = {(r["Store Name"], r["Product Name"]) for r in rows}
    if (new_record["Store Name"], new_record["Product Name"]) not in existing_keys:
        rows.append(new_record)

    fieldnames = ["Store Name", "Product Name", "Product Price", "Gender", "Landing Page Link", "Ad Link", "Date Published"]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Updated {csv_path} with {len(rows)} records (unsorted).")

    # Sync / Git commit
    try:
        subprocess.run(["git", "add", csv_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Sync ad record: {new_record['Store Name']} - {new_record['Product Name']}"], check=True)
        print("Git sync complete!")
    except Exception as e:
        print("Git sync note:", e)

    return rows
