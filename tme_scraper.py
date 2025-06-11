from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_tme_image_if_page_exists(product_code):
    url = f"https://www.tme.eu/ro/details/{product_code}"
    options = Options()
    options.add_argument("--headless")

    try:
        driver = webdriver.Firefox(options=options)
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "PS48B"))
        )

        img = driver.find_element(By.CLASS_NAME, "PS48B")
        img_url = img.get_attribute("src")

        driver.quit()
        return img_url, None

    except Exception as e:
        driver.quit()
        return None, f"Eroare: {str(e)}"
