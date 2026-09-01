import os
import sys
import json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def verify_assets():
    target_json = os.path.join(ROOT_DIR, "data", "interim", "target_perfumes_from_sheet.json")
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        return

    with open(target_json, "r", encoding="utf-8") as f:
        perfumes = json.load(f)

    total = len(perfumes)
    missing_report = []

    verified_count = 0
    total_images_found = 0

    print("=================== ASSET VERIFICATION REPORT ===================")
    for i, item in enumerate(perfumes, start=1):
        full_name = item['full_name']
        folder_name = full_name.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '').strip()
        
        perfume_dir = os.path.join(ROOT_DIR, "assets", "product_images", folder_name)
        
        missing = []
        for img_type in ['bottle.webp', 'package.webp', 'both.webp']:
            filepath = os.path.join(perfume_dir, img_type)
            if not os.path.exists(filepath):
                missing.append(img_type)
            else:
                try:
                    img = Image.open(filepath)
                    if img.width != 1000 or img.height != 1000 or img.format != 'WEBP':
                        missing.append(f"{img_type} (Invalid spec: {img.size}, {img.format})")
                    else:
                        total_images_found += 1
                except Exception as e:
                    missing.append(f"{img_type} (Corrupt: {e})")

        if not missing:
            verified_count += 1
        else:
            missing_report.append((full_name, missing))

    print(f"Total Target Perfumes: {total}")
    print(f"Fully Complete Perfumes (3/3 images valid): {verified_count}/{total}")
    print(f"Total Valid .webp Images Generated: {total_images_found}/{total * 3}")

    if missing_report:
        print("\n--- Items Needing Attention ---")
        for name, m_list in missing_report:
            print(f"• {name}: Missing/Invalid -> {', '.join(m_list)}")
    else:
        print("\n🎉 ALL 55 PERFUMES HAVE ALL 3 REQUIRED IMAGES VALIDATED PERFECTLY!")

if __name__ == '__main__':
    verify_assets()
