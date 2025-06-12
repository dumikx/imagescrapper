import pandas as pd
import requests
from io import BytesIO
import os

# CONFIG
WC_API_URL = "https://microstore.ro/wp-json/wc/v3"
WP_API_URL = "https://microstore.ro/wp-json/wp/v2"
AUTH = ("dumikx", "fodB2szI3IiGntyVeflSiZOk")

LOG_FILE = "upload_log.csv"

def load_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE, dtype=str).fillna("")
    return pd.DataFrame(columns=["product_code", "sku", "status"])

def save_log(log_df):
    log_df.to_csv(LOG_FILE, index=False)

def get_product_by_name(name):
    r = requests.get(f"{WC_API_URL}/products", params={"search": name}, auth=AUTH)
    products = r.json()
    for p in products:
        if p["name"].strip().lower() == name.strip().lower():
            return p
    return None

def get_product_by_sku(sku):
    r = requests.get(f"{WC_API_URL}/products", params={"sku": sku}, auth=AUTH)
    products = r.json()
    if isinstance(products, list) and len(products) > 0:
        return products[0]
    return None

def upload_image_to_media(img_url, file_name):
    try:
        img_data = requests.get(img_url).content
        media_endpoint = f"{WP_API_URL}/media"
        files = {'file': (file_name, BytesIO(img_data), 'image/jpeg')}
        headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
        r = requests.post(media_endpoint, files=files, headers=headers, auth=AUTH)
        r.raise_for_status()
        return r.json().get("id")
    except Exception as e:
        print(f"   ❌ Eroare la upload imagine: {e}")
        return None

def set_product_featured_image(product_id, image_id):
    update_endpoint = f"{WC_API_URL}/products/{product_id}"
    r = requests.put(update_endpoint, json={"images": [{"id": image_id}]}, auth=AUTH)
    return r.status_code == 200

def process_uploads():
    df = pd.read_csv("tme_results.csv", dtype={"product_code": str, "sku": str}).fillna("")
    log_df = load_log()
    already_done = set(log_df[log_df["status"] == "✅"]["product_code"])

    total = len(df)
    updated_log = log_df.copy()

    for index, row in df.iterrows():
        name = row["product_code"]
        sku = row.get("sku", "")
        image_url = row["image_url"]

        print(f"[{index+1}/{total}] Procesăm: {name}")

        if name in already_done:
            print(f"   ⏭️ Sărit (deja procesat cu succes)")
            continue

        if not image_url or "http" not in image_url:
            print(f"   ⚠️ Fără link valid pentru: {name}")
            updated_log = pd.concat([updated_log, pd.DataFrame([{"product_code": name, "sku": sku, "status": "❌"}])], ignore_index=True)
            continue

        product = get_product_by_name(name)
        if not product and sku:
            print(f"   🔄 Caut produs după SKU: {sku}")
            product = get_product_by_sku(sku)

        if not product:
            print(f"   ❌ Produsul '{name}' nu a fost găsit")
            updated_log = pd.concat([updated_log, pd.DataFrame([{"product_code": name, "sku": sku, "status": "❌"}])], ignore_index=True)
            continue

        image_id = upload_image_to_media(image_url, f"{name}.jpg")
        if not image_id:
            updated_log = pd.concat([updated_log, pd.DataFrame([{"product_code": name, "sku": sku, "status": "❌"}])], ignore_index=True)
            continue

        success = set_product_featured_image(product["id"], image_id)
        if success:
            print(f"   ✅ Imagine setată cu succes")
            updated_log = pd.concat([updated_log, pd.DataFrame([{"product_code": name, "sku": sku, "status": "✅"}])], ignore_index=True)
        else:
            print(f"   ⚠️ Imagine uploadată, dar produsul nu a fost actualizat.")
            updated_log = pd.concat([updated_log, pd.DataFrame([{"product_code": name, "sku": sku, "status": "❌"}])], ignore_index=True)

    save_log(updated_log.drop_duplicates(subset=["product_code"], keep="last"))

if __name__ == "__main__":
    process_uploads()
