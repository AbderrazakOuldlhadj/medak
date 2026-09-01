import re
from bs4 import BeautifulSoup

with open('pafen_landing.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Look for price patterns
prices = re.findall(r'\b\d{1,3}(?:[.,\s]\d{3})*\s*(?:DA|DZD|د\.ج|دج)\b', html, re.IGNORECASE)
print("Prices with currency tag:", prices)

# Look for standalone 4-digit or 5-digit numbers
numbers = re.findall(r'\b\d{4,5}\b', html)
print("Standalone 4-5 digit numbers:", set(numbers))

# Print all text in landing page
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text(separator="\n", strip=True)
with open('landing_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved landing text to landing_text.txt")
