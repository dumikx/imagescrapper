import pandas as pd
import os
import time
import requests
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Citește codurile fără imagine
df = pd.read_csv("tme_results.csv", dtype=str)
df = df[df["image_url"].isna() | (df["image_url"] == "")]
df = df.reset_index(drop=True)

# Selectează intervalul dorit
start = int(input("De la ce rând să înceapă? (0-based index): "))
end = int(input("Până la ce rând să se termine? (inclusiv): "))
df = df.iloc[start:end + 1]

# Creează folderul pentru salvare dacă nu există
os.makedirs("pending_review", exist_ok=True)

# Pornește browserul vizibil
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)

for i, row in df.iterrows():
    code = row["product_code"]
    query = code.replace(",", " ").replace("/", " ")
    print(f"[{i}] Caut pe DuckDuckGo: {query}")

    try:
        driver.get("https://duckduckgo.com/?iax=images&ia=images&q=" + query)
        time.sleep(3)

        thumbnails = driver.find_elements(By.CSS_SELECTOR, "img")

        img_url = None
        for img in thumbnails:
            src = img.get_attribute("src")
            if src and src.startswith("/iu/?u="):
                encoded = src.split("/iu/?u=")[-1].split("&")[0]
                img_url = unquote(encoded)
                break
            elif src and src.startswith("http"):
                img_url = src
                break

        if not img_url:
            print(f"   ❌ Nicio imagine validă pentru {code}")
            continue

        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            path = os.path.join("pending_review", f"{code}.jpg")
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"   ✅ Imagine salvată pentru {code}")
        else:
            print(f"   ❌ Eroare la descărcare pentru {code}")

    except Exception as e:
        print(f"   ❌ Eroare pentru {code}: {e}")

driver.quit()
print("Gata. Imaginile au fost salvate în folderul pending_review.")
