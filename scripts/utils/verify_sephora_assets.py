import os
import sys
import json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def verify_sephora_assets():
    target_json = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return

    with open(target_json, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    total = len(perfumes)

    perfumes_with_images = 0
    total_images_saved = 0
    summary_report = []

    print("=================== SEPHORA FR ASSET VERIFICATION ===================")

    for item in perfumes:
        full_name = item['full_name']
        folder_name = full_name.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '').strip()
        perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)

        if not os.path.exists(perfume_dir):
            summary_report.append((full_name, 0, "Folder missing"))
            continue

        valid_files = []
        for f in os.listdir(perfume_dir):
            if f.endswith('.webp'):
                fpath = os.path.join(perfume_dir, f)
                try:
                    img = Image.open(fpath)
                    if img.format == 'WEBP':
                        valid_files.append((f, img.size))
                except Exception:
                    pass

        count = len(valid_files)
        total_images_saved += count
        if count > 0:
            perfumes_with_images += 1
            summary_report.append((full_name, count, f"{count} images valid"))
        else:
            summary_report.append((full_name, 0, "No valid WebP images"))

    print(f"Total Target Perfumes: {total}")
    print(f"Perfumes with Sephora FR Images: {perfumes_with_images}/{total}")
    print(f"Total WebP Images Saved: {total_images_saved}")

    print("\n--- Detailed Summary per Perfume ---")
    for name, count, status in summary_report:
        print(f"• {name} -> {status}")

if __name__ == '__main__':
    verify_sephora_assets()
