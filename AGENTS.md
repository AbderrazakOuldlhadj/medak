# AGENTS.md - Workspace Context & Technical Guidelines

Welcome to the **Algeria Parfums Market & Ads Research** project. This file provides AI coding assistants and agents with full context regarding project goals, architecture, data schemas, API authentication, and common automation workflows.

---

## 🎯 Project Overview
This project focuses on competitive intelligence, market research, price analysis, and Facebook/Meta Ads Library tracking for perfume e-commerce stores in Algeria (*Parfums DZ*).

The primary outputs are:
1. Structured CSV datasets ([ads_research.csv](file:///c:/Users/msipc/Desktop/products/parfums/ads_research.csv)) tracking active perfume ads, store names, prices, target gender, landing pages, Meta Ad links, and publication dates.
2. Automated synchronization and custom formatting with **Google Sheets** for real-time team view and filtering.

---

## 📁 Repository Structure

```
c:/Users/msipc/Desktop/products/parfums/
├── ads_research.csv                 # Primary CSV database for competitor ads research
├── client_secret_*.json             # Google OAuth2 client credentials
├── token.json                       # Google OAuth2 authorized user tokens (Drive & Sheets API)
├── AGENTS.md                        # Workspace documentation & AI context (this file)
└── scripts/                         # Python automation & API integration scripts
    ├── sync_ads_csv_to_sheets.py    # Syncs ads_research.csv to Google Sheets while preserving formatting
    ├── create_ads_research_sheet.py # Creates and formats the initial Google Sheet
    ├── google_sheets_mcp.py         # Google Sheets service helper module (handles authentication & API clients)
    ├── list_google_sheets.py        # Lists all Google Sheets in the user's Drive
    ├── authorize_google.py          # Refreshes OAuth2 credentials flow if needed
    ├── build_verified_csv.py        # Validates and builds clean competitor CSV datasets
    ├── parse_all_searches.py        # Parses raw HTML search dumps from Meta Ads Library
    ├── search_meta_ads.py           # Meta Ads Library research helpers
    └── ...
```

---

## 📊 Core Data Schemas

### `ads_research.csv`
The primary dataset schema consists of 7 columns:
1. `Store Name`: Name of the e-commerce store (e.g., *Pafen Dz*, *Smell Good Dz*, *Fragrance Dz*, *Auraluxe Dz*).
2. `Product Name`: Specific fragrance title, volume, and concentration (e.g., *Armaf Club De Nuit Intense Man 105ml EDP*).
3. `Product Price`: Price string formatted with comma separators and currency (e.g., `"12,000 DZD"`).
4. `Gender`: Audience target — strictly restricted to `Homme`, `Femme`, or `Unisex`.
5. `Landing Page Link`: URL to the store product/order page.
6. `Ad Link`: URL to the active Meta/Facebook Ad Library entry (may be empty `""` if unlinked).
7. `Date Published`: Publication date formatted as `mmm d, yyyy` (e.g., `"Jan 3, 2026"`).

---

## 🔐 Google API & Authentication Setup

- **Google OAuth2**: Token file `token.json` at root handles authentication with scopes:
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`
- **Active Spreadsheet**:
  - **Title**: `Algeria Parfums Ads Research`
  - **Spreadsheet ID**: `1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A`
  - **Direct URL**: `https://docs.google.com/spreadsheets/d/1bNNR9wgq0rw4cNeP8SEU-WlXCxx1pe-5_1aWq_YXO_A/edit`

---

## 🎨 Google Sheets Formatting Guidelines

When updating the Google Sheet, **never wipe out the existing user-configured sheet formatting**:
1. **Dropdown Data Validation**: Applied on Column D (`Gender`) with allowed options `['Homme', 'Unisex', 'Femme']`.
2. **Date Formatting**: Column G (`Date Published`) uses Google Sheets pattern `mmm d, yyyy`.
3. **Alignment & Wrapping**:
   - Headers: Navy Blue background `(0.10, 0.18, 0.36)`, Bold White text, Centered.
   - Data Cells: Horizontal alignment `CENTER`, Vertical alignment `MIDDLE`, Text wrapping `WRAP`.
4. **Basic Filter**: Filter view enabled across all data columns (`A1:G{N}`).

---

## 🛠️ Common Operations for Agents

### 1. Syncing `ads_research.csv` to Google Sheets
Run the sync script directly via python:
```bash
python scripts/sync_ads_csv_to_sheets.py
```
*Note*: This script uses `google_sheets_mcp.py` to auto-refresh expired OAuth credentials, clears previous cell values in `Sheet1!A1:Z50`, updates new rows, and updates the basic filter range.

### 2. Inspecting Sheet Formats
If checking spreadsheet structure or user changes:
```bash
python scripts/inspect_sheet_format.py
```

---

## ⚠️ Important Rules for Agents
- **Script Location**: Always place or save new scripts directly inside the `scripts/` directory (never leave python or helper scripts in the project root).
- **Preserve Formatting**: When modifying CSV rows or pushing updates to Google Sheets, avoid overwriting cell formatting, dropdown data validations, or date format patterns.
- **Currency & Gender Conventions**: Ensure prices end with `DZD` and gender values strictly adhere to `Homme`, `Femme`, or `Unisex`.
- **Windows Encoding**: Always run Python scripts with UTF-8 stdout reconfigured (`sys.stdout.reconfigure(encoding='utf-8')`) to prevent `UnicodeEncodeError` in Windows terminals.
