import pandas as pd
import os
from tme_scraper import get_tme_image_if_page_exists

# Citește codurile de produs din fișier .ods
df_input = pd.read_excel("product_inputs.ods", engine="odf", dtype=str)
df_input = df_input.rename(columns=lambda col: col.strip())
if "Cod produs" in df_input.columns:
    df_input = df_input.rename(columns={"Cod produs": "product_code"})

# Input din consolă pentru intervalul de rânduri
start_row = int(input("De la ce linie vrei să înceapă? (0-based): "))
end_row = int(input("Până la ce linie să se termine? (inclusiv): "))
df_input = df_input.iloc[start_row:end_row + 1]

# Verifică existența rezultatului anterior
existing_file = "tme_results.csv"
if os.path.exists(existing_file):
    df_existing = pd.read_csv(existing_file, dtype={"product_code": str})
    processed_codes = set(df_existing[df_existing["image_url"].notnull()]["product_code"])
else:
    df_existing = pd.DataFrame(columns=["product_code", "image_url", "status"])
    processed_codes = set()

# Coduri neprocesate
df_new = df_input[~df_input["product_code"].isin(processed_codes)]

# Procesare cu progres în consolă
results = []
for index, code in enumerate(df_new['product_code'], start=1):
    print(f"[{index}/{len(df_new)}] Procesăm: {code}")
    image_url, message = get_tme_image_if_page_exists(code)
    results.append({
        "product_code": code,
        "image_url": image_url,
        "status": message if message else "OK"
    })

# Combină cu rezultatele existente
df_combined = pd.concat([df_existing, pd.DataFrame(results)], ignore_index=True)
df_combined.to_csv(existing_file, index=False)

print(f"Procesate {len(df_new)} produse noi. Rezultatul complet salvat în '{existing_file}'.")
