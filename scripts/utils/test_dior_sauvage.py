import os
import sys
import requests
import io
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT_DIR, "scripts", "processing"))
from process_image_assets import format_image_to_square_webp

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

test_urls = {
    'bottle': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRge-bo2xqXR2oPVRhWMCh72dPTTPAgGT2q7gzzHYmcKw&s',
    'both': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjR-Ha_iVycp2UZSZHe7br9UuRihKIpTQqnrmWkhMUjA&s'
}

perfume = "DIOR SAUVAGE EDT 100ML"
output_dir = os.path.join(ROOT_DIR, "assets", "product_images", perfume)
os.makedirs(output_dir, exist_ok=True)

for img_type, url in test_urls.items():
    print(f"Fetching user-provided real image for {img_type}...")
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        out_path = os.path.join(output_dir, f"{img_type}.webp")
        success = format_image_to_square_webp(io.BytesIO(res.content), out_path, remove_bg=True)
        if success:
            print(f"  ✓ {img_type}.webp created with AI background removal -> {out_path}")
        else:
            print(f"  ✗ Failed to format {img_type}.webp")

