import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image

sys.path.append(os.path.join(r'c:\Users\msipc\Desktop\products\parfums', 'scripts', 'processing'))
from process_image_assets import format_image_to_square_webp

sys.stdout.reconfigure(encoding='utf-8')

def fetch_ysl_y_intense():
    target_dir = r"c:\Users\msipc\Desktop\products\parfums\assets\product_images\YVES SAINT LAURENT Y INTENSE EDP 100ML"
    os.makedirs(target_dir, exist_ok=True)

    # Clean directory
    for f in os.listdir(target_dir):
        fp = os.path.join(target_dir, f)
        if os.path.isfile(fp):
            try: os.remove(fp)
            except Exception: pass

    urls = [
        'https://odorem-dz.com/produit/y-eau-de-parfum-intense-100ml-yves-saint-laurent/',
        'https://odorem-dz.com/produit/y-eau-de-parfum-200ml-yves-saint-laurent/',
        'https://media.sephora.eu/PIM/3456037_main.jpg?scaleWidth=1000&scaleMode=fit',
        'https://media.sephora.eu/PIM/3456037_1.jpg?scaleWidth=1000&scaleMode=fit',
        'https://media.sephora.eu/PIM/3456037_2.jpg?scaleWidth=1000&scaleMode=fit',
        'https://cdn.notinoimg.com/detail_main_hq/yves-saint-laurent/3614273898492_01-o/y___250515.jpg',
        'https://cdn.notinoimg.com/detail_main_hq/yves-saint-laurent/3614273898492_02/y___250515.jpg'
    ]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

    img_urls = []
    for u in urls[:2]:
        try:
            res = session.get(u, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                gallery = soup.find_all(class_=re.compile(r'woocommerce-product-gallery|product-gallery|gallery', re.I))
                for g in gallery:
                    for a in g.find_all('a', href=True):
                        if any(ext in a['href'].lower() for ext in ['.jpg', '.png', '.webp']):
                            img_urls.append(a['href'])
                    for img in g.find_all('img'):
                        val = img.get('data-large_image') or img.get('src') or img.get('data-src')
                        if val and any(ext in val.lower() for ext in ['.jpg', '.png', '.webp']):
                            img_urls.append(val)
        except Exception as e:
            print(f"Note: {e}")

    img_urls.extend(urls[2:])

    base_map = {}
    for u in img_urls:
        if u.startswith('data:'): continue
        clean_u = re.sub(r'-\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', u)
        base_map[clean_u] = clean_u

    unique_urls = list(base_map.values())
    print('Found unique gallery URLs:', unique_urls)

    saved = 0
    for idx, u in enumerate(unique_urls, 1):
        try:
            r = session.get(u, timeout=12)
            if r.status_code == 200 and len(r.content) > 5000:
                ext = 'png' if u.endswith('.png') else 'jpg'
                raw_name = f'raw_{saved+1}.{ext}'
                raw_path = os.path.join(target_dir, raw_name)
                with open(raw_path, 'wb') as f:
                    f.write(r.content)

                img = Image.open(raw_path)
                if img.width >= 200 and img.height >= 200:
                    webp_name = 'bottle.webp' if saved == 0 else f'image_{saved+1}.webp'
                    webp_path = os.path.join(target_dir, webp_name)

                    success = format_image_to_square_webp(img, webp_path, remove_bg=True)
                    if success:
                        print(f'  [✓ Saved Authentic Perfume Image {saved+1}] {raw_name} -> {webp_name} ({img.width}x{img.height}px, {len(r.content)//1024} KB)')
                        saved += 1
        except Exception as e:
            print(f'  Error {u}: {e}')

    print(f"Done! Successfully saved {saved} authentic YSL Y Intense EDP 100ml photos into YVES SAINT LAURENT Y INTENSE EDP 100ML/")

if __name__ == '__main__':
    fetch_ysl_y_intense()
