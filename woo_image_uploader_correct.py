import os
import requests
import base64
import mimetypes
import pandas as pd

WC_API_URL = "https://microstore.ro/wp-json/wc/v3"
WP_API_URL = "https://microstore.ro/wp-json/wp/v2"
USERNAME = "dumikx"
PASSWORD = "fodB 2szI 3IiG ntyV eflS iZOk"
APPROVED_FOLDER = "approved"
HEADERS = {"Content-Type": "application/json"}

# Încarcă CSV-ul cu coduri și SKU-uri
df = pd.read_csv("tme_results.csv", dtype=str).fillna("")
product_list = df.to_dict(orient="records")

# Încărcare imagine în WordPress media
def upload_image_to_wp(image_path):
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        image_data = f.read()

    mime_type, _ = mimetypes.guess_type(filename)
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": mime_type or "image/jpeg"
    }

    response = requests.post(
        f"{WP_API_URL}/media",
        headers=headers,
        data=image_data,
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"   ❌ Eroare upload imagine: {response.status_code} - {response.text}")
        return None

# Găsește produsul întâi după nume, apoi după SKU
def find_product_id(product_code):
    for p in product_list:
        if p["product_code"] == product_code:
            name = p["product_code"]
            sku = p["sku"]

            # Caută după nume
            r = requests.get(
                f"{WC_API_URL}/products",
                params={"search": name},
                auth=(USERNAME, PASSWORD)
            )
            results = r.json()
            if results:
                return results[0]["id"]

            # Fallback: caută după SKU
            if sku:
                r = requests.get(
                    f"{WC_API_URL}/products",
                    params={"sku": sku},
                    auth=(USERNAME, PASSWORD)
                )
                results = r.json()
                if results:
                    return results[0]["id"]
    return None

# Parcurge folderul de imagini aprobate
results = []
files = [f for f in os.listdir(APPROVED_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
files.sort()

for i, file in enumerate(files, start=1):
    code = os.path.splitext(file)[0]
    print(f"[{i}/{len(files)}] Upload pentru: {code}")

    image_path = os.path.join(APPROVED_FOLDER, file)
    media_id = upload_image_to_wp(image_path)

    if not media_id:
        results.append({"product_code": code, "status": "❌ Eroare upload"})
        continue

    product_id = find_product_id(code)
    if not product_id:
        print(f"   ❌ Produsul nu a fost găsit pentru: {code}")
        results.append({"product_code": code, "status": "❌ Produs negăsit"})
        continue

    # Asociază imaginea la produs
    r = requests.put(
        f"{WC_API_URL}/products/{product_id}",
        json={"images": [{"id": media_id}]},
        auth=(USERNAME, PASSWORD)
    )

    if r.status_code == 200:
        print(f"   ✅ Imagine asociată cu produsul {product_id}")
        results.append({"product_code": code, "status": "✅ Success"})
    else:
        print(f"   ❌ Eroare asociere imagine: {r.status_code}")
        results.append({"product_code": code, "status": f"❌ {r.status_code}"})

# Salvează rezultatul
pd.DataFrame(results).to_csv("upload_results.csv", index=False)
print("✔️ Gata. Rezultatele sunt salvate în upload_results.csv")
