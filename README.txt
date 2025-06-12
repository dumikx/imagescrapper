=== Woo Image Uploader (cu fallback și SKU) ===

1. Asigură-te că ai instalat:
   pip install pandas requests

2. Pregătește fișierul tme_results.csv cu coloanele:
   - product_code: numele produsului (exact ca în WooCommerce)
   - image_url: link către imagine (începe cu http)
   - sku: (opțional) codul SKU, cu zerouri păstrate (ex: 00015204)

3. Rulează scriptul:
   python uploader.py

Ce face scriptul:
- Caută produsul mai întâi după nume.
- Dacă nu-l găsește și există un SKU, caută și după SKU.
- Încarcă imaginea în media library.
- Setează imaginea ca "featured image" pentru produs.
- Afișează progresul și orice eroare detaliată în consolă.
