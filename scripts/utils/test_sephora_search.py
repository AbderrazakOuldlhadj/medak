import sys
import requests
import re
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

def search_sephora_images(perfume_name):
    query = f"sephora fr {perfume_name}"
    encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded}&form=HDRSC2&first=1"
    res = requests.get(url, headers=HEADERS, timeout=10)
    
    matches = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
    if not matches:
        matches = re.findall(r'"murl":"(http[^"]+)"', res.text)

    sephora_urls = []
    other_urls = []

    for m in matches:
        m_clean = urllib.parse.unquote(m)
        if 'sephora.fr' in m_clean or 'sephora.com' in m_clean or 'sephora' in m_clean:
            sephora_urls.append(m_clean)
        else:
            other_urls.append(m_clean)

    print(f"\nSearch: '{query}'")
    print(f"Direct Sephora URLs found ({len(sephora_urls)}):")
    for u in sephora_urls[:5]:
        print("  [SEPHORA]", u)
    print(f"Other Product URLs found ({len(other_urls)}):")
    for u in other_urls[:3]:
        print("  [OTHER]", u)

if __name__ == '__main__':
    search_sephora_images("Dior Sauvage Eau de Toilette")
    search_sephora_images("Azzaro The Most Wanted EDP")
    search_sephora_images("Yves Saint Laurent Y EDP")
