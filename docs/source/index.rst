=============================
IdenHQ Product Scraper Docs
=============================

Welcome to the documentation for **IdenHQ Product Scraper**, a Python project that scrapes product data from IdenHQ using Playwright.

=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Project Overview
================

The **IdenHQ Product Scraper** automates extraction of product details from IdenHQ inventory tables. It can:

- Log in automatically using credentials stored securely  
- Navigate through Start Journey → Continue Search → Inventory Section  
- Scrape all products including categories and attributes  
- Handle lazy-loaded content and multiple pages  
- Deduplicate results and autosave progress  
- Export data to structured JSON for analysis  

Features
========

- Login using `.env` file for credentials  
- Automatic navigation through workflow  
- Scrape visible products, categories, and attributes  
- Handle pagination and lazy-loading  
- Deduplicate products automatically  
- Autosave progress every N products  
- Save failed products in `failed_products.json`  
- Optional headless mode for faster scraping  
- Robust against page reloads and dynamic content  

Setup
=====

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/Sharanya-Gowda/playwright-tests
      cd iden_challenge

2. Install required Python packages:

   .. code-block:: bash

      pip install playwright python-dotenv
      playwright install

3. Create a `.env` file in the project root:

   .. code-block:: text

      SCRAPER_USERNAME=your_email@example.com
      SCRAPER_PASSWORD=your_password

Usage
=====

Run the scraper:

.. code-block:: bash

   python scraper.py

- Logs in using `.env` credentials
- Navigates to the product table
- Scrapes all products across pages and lazy-loaded content
- Autosaves progress every 20 products by default
- Failed products are saved in `failed_products.json`

Interrupting the Scraper
------------------------

- Press `Ctrl+C` to stop the scraper.
- Progress is saved automatically.

Headless Mode
-------------

To run the scraper without opening a browser window:

.. code-block:: python

   context = await p.chromium.launch_persistent_context(
       user_data_dir="./user_data",
       headless=True
   )



Output
======

- `products.json`:

.. code-block:: json

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

- `failed_products.json`: logs products that could not be scraped, including reason and HTML snippet for debugging.

Project Structure
=================

.. code-block:: text

   iden_challenge/
   ├─ scraper.py
   ├─ products.json
   ├─ failed_products.json
   ├─ user_data/
   ├─ .env
   └─ README.md

Best Practices
==============

- Use `.env` for credentials
- Avoid closing the browser manually
- Enable headless mode for faster execution
- Adjust `autosave_interval` for large tables
- Review `failed_products.json` for failed products

Troubleshooting
===============

- Empty `products.json`: check selectors in `scraper.py` match the website structure
- `TargetClosedError`: browser closed manually during scraping
- Login fails: verify `.env` values

API Reference
=============

.. automodule:: scraper
   :members:
   :undoc-members:
   :show-inheritance:
