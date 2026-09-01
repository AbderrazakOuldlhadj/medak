import os
import shutil
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Directories to create
DIRS_TO_CREATE = [
    os.path.join(ROOT_DIR, "data", "processed"),
    os.path.join(ROOT_DIR, "data", "samples"),
    os.path.join(ROOT_DIR, "data", "raw_dumps", "html"),
    os.path.join(ROOT_DIR, "data", "raw_dumps", "text"),
    os.path.join(ROOT_DIR, "data", "interim"),
    os.path.join(ROOT_DIR, "assets", "product_images"),
    os.path.join(ROOT_DIR, "scripts", "scraping"),
    os.path.join(ROOT_DIR, "scripts", "processing"),
    os.path.join(ROOT_DIR, "scripts", "google_sheets"),
    os.path.join(ROOT_DIR, "scripts", "utils"),
]

for d in DIRS_TO_CREATE:
    os.makedirs(d, exist_ok=True)

# Explicit mappings for root / products files
ROOT_MOVES = {
    "ads_research.csv": os.path.join(ROOT_DIR, "data", "processed", "ads_research.csv"),
    "shopify_perfumes_export.csv": os.path.join(ROOT_DIR, "data", "processed", "shopify_perfumes_export.csv"),
    "shopify_perfumes_sample_10.csv": os.path.join(ROOT_DIR, "data", "samples", "shopify_perfumes_sample_10.csv"),
    "ad_1701177097798374.html": os.path.join(ROOT_DIR, "data", "raw_dumps", "html", "ad_1701177097798374.html"),
    "pafen_landing.html": os.path.join(ROOT_DIR, "data", "raw_dumps", "html", "pafen_landing.html"),
    "ad_1701177097798374.txt": os.path.join(ROOT_DIR, "data", "raw_dumps", "text", "ad_1701177097798374.txt"),
    "landing_text.txt": os.path.join(ROOT_DIR, "data", "raw_dumps", "text", "landing_text.txt"),
    "rendered_pafen.txt": os.path.join(ROOT_DIR, "data", "raw_dumps", "text", "rendered_pafen.txt"),
    "last_scraped_output.json": os.path.join(ROOT_DIR, "data", "interim", "last_scraped_output.json"),
    "latest_scraped_ad.json": os.path.join(ROOT_DIR, "data", "interim", "latest_scraped_ad.json"),
}

PRODUCTS_DIR = os.path.join(ROOT_DIR, "products")
if os.path.exists(PRODUCTS_DIR):
    for f in os.listdir(PRODUCTS_DIR):
        src = os.path.join(PRODUCTS_DIR, f)
        if os.path.isfile(src):
            dst = os.path.join(ROOT_DIR, "assets", "product_images", f)
            shutil.move(src, dst)
            print(f"Moved product image {f} -> assets/product_images/")
    try:
        os.rmdir(PRODUCTS_DIR)
        print("Removed empty products/ directory.")
    except Exception as e:
        print(f"Could not remove products/ dir: {e}")

for filename, dst in ROOT_MOVES.items():
    src = os.path.join(ROOT_DIR, filename)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {filename} -> {os.path.relpath(dst, ROOT_DIR)}")

# Scripts categorization
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")

SCRAPING_SCRIPTS = [
    "parse_all_searches.py", "parse_search.py", "search_meta_ads.py",
    "search_more_brands.py", "search_algerian_parfum_competitors.py",
    "scrape_ad.py", "scrape_single_ad.py", "scrape_target_products.py",
    "process_pasted_ads.py"
]

PROCESSING_SCRIPTS = [
    "build_verified_csv.py", "export_shopify_csv.py", "clean_csv.py",
    "clean_duplicates.py", "clean_last_row.py", "sort_csv.py",
    "populate_csv.py", "add_gender_column.py", "add_published_date.py",
    "fill_missing_ad_links.py", "extract_verified_pairs.py",
    "extract_collections.py", "extract_more_landing_pages.py",
    "validate_shopify_csv.py", "verify_and_fix_links.py",
    "create_test_sample_csv.py"
]

GOOGLE_SHEETS_SCRIPTS = [
    "google_sheets_mcp.py", "sync_ads_csv_to_sheets.py",
    "create_ads_research_sheet.py", "authorize_google.py",
    "list_google_sheets.py", "sync_and_process.py",
    "sync_to_google_sheets.py", "update_and_sync_ads.py",
    "format_google_models_sheet.py", "populate_google_models_sheet.py",
    "add_charts_to_sheet.py", "test_sheets_api.py"
]

if os.path.exists(SCRIPTS_DIR):
    for f in os.listdir(SCRIPTS_DIR):
        src = os.path.join(SCRIPTS_DIR, f)
        if not os.path.isfile(src):
            continue

        ext = os.path.splitext(f)[1].lower()

        # Non-python dumps sitting in scripts/
        if ext == ".html":
            dst = os.path.join(ROOT_DIR, "data", "raw_dumps", "html", f)
            shutil.move(src, dst)
            print(f"Moved scripts/{f} -> data/raw_dumps/html/{f}")
        elif ext == ".txt":
            dst = os.path.join(ROOT_DIR, "data", "raw_dumps", "text", f)
            shutil.move(src, dst)
            print(f"Moved scripts/{f} -> data/raw_dumps/text/{f}")
        elif ext == ".json":
            dst = os.path.join(ROOT_DIR, "data", "interim", f)
            shutil.move(src, dst)
            print(f"Moved scripts/{f} -> data/interim/{f}")
        elif ext == ".py":
            if f == os.path.basename(__file__):
                continue
            if f in SCRAPING_SCRIPTS:
                dst = os.path.join(SCRIPTS_DIR, "scraping", f)
            elif f in PROCESSING_SCRIPTS:
                dst = os.path.join(SCRIPTS_DIR, "processing", f)
            elif f in GOOGLE_SHEETS_SCRIPTS:
                dst = os.path.join(SCRIPTS_DIR, "google_sheets", f)
            else:
                dst = os.path.join(SCRIPTS_DIR, "utils", f)
            shutil.move(src, dst)
            print(f"Moved scripts/{f} -> scripts/{os.path.relpath(dst, SCRIPTS_DIR)}")

print("\nWorkspace file migration completed successfully.")
