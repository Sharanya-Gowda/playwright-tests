# IdenHQ Product Scraper

A robust Python scraper built with **Playwright** to extract all product data from IdenHQ. Handles **lazy-loading, pagination, and dynamic content**, and exports it to a structured JSON file for analysis.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Requirements](#requirements)  
4. [Setup](#setup)  
5. [Usage](#usage)  
6. [Output](#output)  
7. [Project Structure](#project-structure)  
8. [Best Practices](#best-practices)  
9. [Troubleshooting](#troubleshooting)  

---

## Project Overview

The IdenHQ Product Scraper automates extraction of product details from IdenHQ inventory tables. It can:

- Log in automatically using credentials stored securely  
- Navigate through Start Journey → Continue Search → Inventory Section  
- Scrape all products including categories and attributes  
- Handle lazy-loaded content and multiple pages  
- Deduplicate results and autosave progress  
- Export data to structured JSON for analysis  

---

## Features

- ✅ Login using `.env` file for credentials  
- ✅ Automatic navigation through workflow  
- ✅ Scrape all visible products, categories, and attributes  
- ✅ Handle **pagination** and **lazy-loading**  
- ✅ Deduplicate products automatically  
- ✅ Autosave progress every N products (`autosave_interval`)  
- ✅ Save failed products in `failed_products.json`  
- ✅ Optional **headless mode** for faster scraping  
- ✅ Robust against page reloads and dynamic content  

---

## Requirements

- Python 3.10+  
- [Playwright](https://playwright.dev/python/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sharanya-Gowda/playwright-tests
cd iden_challenge
```

### 2. Install Python packages

```bash
pip install playwright python-dotenv
playwright install
```

### 3. Create a `.env` file in the project root

```env
SCRAPER_USERNAME=your_email@example.com
SCRAPER_PASSWORD=your_password
```

---

## Usage

Run the scraper:

```bash
python scraper.py
```

- Logs in using .env credentials
- Navigates to the product table
- Scrapes all products across pages and lazy-loaded content
- Autosaves progress every 20 products by default
- Failed products are saved in `failed_products.json`

### Interrupting the Scraper

- Press Ctrl+C to stop the scraper.
- Progress is saved automatically, so no data is lost.

---

## Output

- `products.json`

Example output:

```json
[
  {
    "name": "Product 1",
    "category": "Category A",
    "attributes": {
      "Price": "$10",
      "Stock": "20"
    }
  }
]
```

---

## Project Structure

```bash
iden_challenge/
├─ scraper.py             # Main scraper script
├─ products.json          # Scraped product data
├─ failed_products.json   # Failed product logs
├─ user_data/             # Persistent Playwright login session
├─ .env                   # Credentials file (ignored by git)
└─ README.md              # Project documentation
```

---

## Best Practices

- Use `.env` for credentials
- Avoid closing the browser manually
- Enable headless mode for faster execution
- Adjust `autosave_interval` for large tables
- Review `failed_products.json` for failed products

---

## Troubleshooting

- **Empty products.json:** Check selectors in `scraper.py` match the website structure
- **TargetClosedError:** Browser closed manually during scraping
- **Login fails:** Verify `.env` values