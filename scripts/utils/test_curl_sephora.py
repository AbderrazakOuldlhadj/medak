import sys
from curl_cffi import requests

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

try:
    print("Sending browser TLS impersonated request to Sephora FR...")
    res = requests.get(
        "https://www.sephora.fr/p/sauvage---eau-de-toilette-P2266017.html",
        headers=headers,
        impersonate="chrome124",
        timeout=15
    )
    print("Status Code:", res.status_code)
    print("Content Length:", len(res.text))
    if res.status_code == 200:
        import re
        imgs = re.findall(r'(https://www\.sephora\.fr/dw/image/v2/[^"\'\s>]+)', res.text)
        print(f"Extracted {len(imgs)} Sephora CDN image URLs:")
        unique_imgs = list(set(imgs))
        for u in unique_imgs[:10]:
            print("  ", u)
    else:
        print("Response snippet:", res.text[:300])
except Exception as e:
    print("Error with curl_cffi:", e)
