import pandas as pd
import os
from tme_scraper import get_image_and_description_from_driver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Citește fișierul de input și reține indexul original
df_input = pd.read_excel("product_inputs.ods", engine="odf", dtype=str)
df_input = df_input.rename(columns=lambda col: col.strip())
if "Cod produs" in df_input.columns:
    df_input = df_input.rename(columns={"Cod produs": "product_code"})
df_input["row_index"] = df_input.index  # reținem poziția originală

# Selectăm rânduri din consolă
start_row = int(input("De la ce linie vrei să înceapă? (0-based): "))
end_row = int(input("Până la ce linie să se termine? (inclusiv): "))
df_selection = df_input.iloc[start_row:end_row + 1].copy()

# Dacă rezultatele există, adăugăm coloanele
result_columns = ["image_url", "description", "status"]
for col in result_columns:
    if col not in df_input.columns:
        df_input[col] = ""

# Inițializăm browserul o singură dată
options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

# Procesăm selecția și completăm în dataframe-ul original
for index, row in df_selection.iterrows():
    code = row["product_code"]
    print(f"[{index}] Procesăm: {code}")
    image_url, description, message = get_image_and_description_from_driver(driver, code)

    df_input.loc[index, "image_url"] = image_url
    df_input.loc[index, "description"] = description
    df_input.loc[index, "status"] = message if message else "OK"

driver.quit()

# Salvăm rezultatul într-un nou fișier cu ordinea păstrată
output_file = "tme_results_ordered.csv"
df_input.drop(columns=["row_index"], errors="ignore").to_csv(output_file, index=False)
print(f"Rezultatele au fost salvate păstrând ordinea în '{output_file}'.")
