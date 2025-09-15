# EMEA Major Cities Extractor

This repository contains a Python script to generate a **list of major cities** for countries in the **EMEA region** (Europe, Middle East, and Africa). The script uses **GeoNames** data and produces both **CSV** and **Excel** outputs containing city information, including population, coordinates, and administrative regions.

---

## Features

- Filters cities to EMEA countries defined in a **country list file**.
- Keeps **major cities** based on population threshold and top N cities per country.
- Outputs:
  - `CSV` file: `emea_major_cities.csv`
  - `Excel` file: `emea_major_cities.xlsx`
- Easy to modify population cutoff or top N cities.

---

## Prerequisites

- Python 3.9+
- Required Python packages:
  - `pandas`
  - `requests`
  - `openpyxl` (for Excel output)

Install packages with:

```bash
pip install pandas requests openpyxl
