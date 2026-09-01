# Algeria Parfums Market & Ads Research

Competitive intelligence, market research, price analysis, and Meta Ads Library tracking for perfume e-commerce stores in Algeria (*Parfums DZ*).

---

## 📁 Folder Architecture

```text
parfums/
├── AGENTS.md                            # Main AI context & workspace guidelines
├── README.md                            # High-level project documentation
├── client_secret_*.json                 # Google OAuth credentials
├── token.json                           # Google OAuth user tokens
│
├── assets/                              # Media & static assets
│   └── product_images/                  # Fragrance product photos (.jpg, .png)
│
├── data/                                # Project datasets & scraped dumps
│   ├── processed/                       # Production datasets (ads_research.csv, shopify_perfumes_export.csv)
│   ├── samples/                         # Test and sample datasets
│   ├── raw_dumps/                       # Scraped HTML & text dumps (data/raw_dumps/html, data/raw_dumps/text)
│   └── interim/                         # Intermediate extracted JSON data
│
└── scripts/                             # Categorized Python automation modules
    ├── scraping/                        # Meta Ads Library scrapers & HTML parsers
    ├── processing/                      # Data validation, cleaning & CSV builders
    ├── google_sheets/                   # Google Sheets API integrations & sync tools
    └── utils/                           # Inspection, diffing & debug helpers
```

---

## 🚀 Quick Execution Commands

### Sync Primary Dataset (`ads_research.csv`) to Google Sheets:
```bash
python scripts/google_sheets/sync_ads_csv_to_sheets.py
```

### Build Verified Competitor CSV:
```bash
python scripts/processing/build_verified_csv.py
```

### Inspect Spreadsheet Structure:
```bash
python scripts/utils/inspect_sheet_format.py
```
