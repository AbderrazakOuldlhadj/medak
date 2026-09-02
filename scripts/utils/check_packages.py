import importlib.util

pkgs = ['playwright', 'selenium', 'cloudscraper', 'curl_cffi', 'bs4', 'requests', 'urllib3']
for p in pkgs:
    spec = importlib.util.find_spec(p)
    print(f"{p}: {'INSTALLED' if spec else 'MISSING'}")
