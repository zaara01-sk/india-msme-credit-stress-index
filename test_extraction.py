import pdfplumber
import pandas as pd
import os

# ============================================================
# CGTMSE Data Extraction — Full Cleaning Pipeline
# ============================================================

pdf_path = r"C:\Users\Zaara\Desktop\MSME\data\raw\sidbi\sidbi_pulse_2025_05.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[33]
    tables = page.extract_tables()
    raw_table = tables[0]

# Step 1 — Convert to DataFrame
df_raw = pd.DataFrame(raw_table)
print("Step 1 — Raw DataFrame:")
print(df_raw)
print()

# Step 2 — Set proper column names from row 1
df_raw.columns = df_raw.iloc[1]
df_raw = df_raw.iloc[2:].reset_index(drop=True)
print("Step 2 — After setting headers:")
print(df_raw)
print()

# Step 3 — Remove cumulation row (last row) — not annual data
df_clean = df_raw[~df_raw['Period'].str.contains('Cumulation', na=False)].copy()
print("Step 3 — After removing cumulation row:")
print(df_clean)
print()

# Step 4 — Clean the Period column
# Remove "Till 31/02/2025" suffix from FY 2024-25 row
df_clean['Period'] = df_clean['Period'].str.replace(
    r'\s*Till.*$', '', regex=True
).str.strip()

# Step 5 — Clean numeric columns
# Remove commas and convert to integers
df_clean['No.'] = df_clean['No.'].str.replace(',', '').astype(int)
df_clean['Amt. (In Crs)'] = df_clean['Amt. (In Crs)'].str.replace(',', '').astype(int)

# Step 6 — Rename columns to clean names
df_clean.columns = ['fiscal_year', 'guarantees_count', 'guarantee_amt_cr']

# Step 7 — Add year-on-year growth rate for guarantee amount
# This becomes our third pillar metric
df_clean['guarantee_growth_pct'] = df_clean['guarantee_amt_cr'].pct_change() * 100
df_clean['guarantee_growth_pct'] = df_clean['guarantee_growth_pct'].round(2)

print("Step 4-7 — Final cleaned DataFrame:")
print(df_clean)
print()

# Step 8 — Add source documentation column
df_clean['source'] = 'SIDBI MSME Pulse May 2025, Page 29'

# Step 9 — Save to processed folder
output_path = r"C:\Users\Zaara\Desktop\MSME\data\processed\cgtmse_guarantees.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_clean.to_csv(output_path, index=False)

print(f"Saved to: {output_path}")
print()
print("Final verification — what your third pillar looks like:")
print(df_clean[['fiscal_year', 'guarantee_amt_cr', 'guarantee_growth_pct']].to_string())