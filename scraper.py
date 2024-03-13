from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import json

# Calea către Edge Driver
service = Service('C:\\edgedrivers\\msedgedriver.exe')
driver = webdriver.Edge(service=service)

# Maximizarea ferestrei browserului la modul fullscreen
driver.maximize_window()

wait = WebDriverWait(driver, 10)

# Deschide pagina de logare
driver.get("https://www.adpress.ro/contul-meu/")

# Așteaptă ca elementul de email să fie încărcat și apoi completează-l
email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
email_input.send_keys("my_mail@gmail.com")

# Așteaptă ca elementul de parolă să fie încărcat și apoi completează-l
password_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
password_input.send_keys("my_password")

# Găsește și apasă butonul de logare
login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][name="login"]')
login_button.click()

time.sleep(3)

# După logare, navighează către pagina de produse
driver.get("https://www.adpress.ro/comanda-advertoriale/")

time.sleep(3)

# Funcția pentru extragerea datelor despre produse
def extract_product_data(html_source):
    soup = BeautifulSoup(html_source, 'html.parser')

    # Lista pentru a colecta datele despre produse
    products_data = []

    # Găsim toate elementele pentru denumirea produselor
    for product_name_element in soup.find_all('h3', class_='product-name product_title'):
        product_data = {'product_name': '', 'initial_price': '', 'reduced_price': ''}

        # Extragem denumirea produsului și eliminăm cuvântul "Advertorial"
        product_name = product_name_element.get_text(strip=True).replace('Advertorial', '').strip()
        product_data['product_name'] = product_name

        # Extragem prețul inițial și prețul redus asociat acestui produs
        price_container = product_name_element.find_next('span', class_='price')

        # Verificăm dacă price_container este None
        if price_container:
            initial_price_element = price_container.find('del')
            reduced_price_element = price_container.find('ins')

            if initial_price_element:
                initial_price = initial_price_element.find('span', class_='woocommerce-Price-amount amount').get_text(strip=True)
            else:
                # Presupunem că prețul standard este prezentat direct în price_container dacă nu există <del>
                initial_price = price_container.find('span', class_='woocommerce-Price-amount amount').get_text(strip=True)

            if reduced_price_element:
                reduced_price = reduced_price_element.find('span', class_='woocommerce-Price-amount amount').get_text(strip=True)
            else:
                # Înlocuim None cu "fără reducere"
                reduced_price = "fără reducere"
        else:
            # Dacă price_container este None, nu putem extrage niciun preț
            initial_price = "Informație indisponibilă"
            reduced_price = "fără reducere"

        # Salvăm prețul inițial și prețul redus în dicționar
        product_data['initial_price'] = initial_price
        product_data['reduced_price'] = reduced_price

        # Adăugăm datele produsului în listă
        products_data.append(product_data)

    return products_data


# Lista pentru a colecta datele de pe toate paginile cu produse
all_products_data = []

# Extragem datele de pe pagina curentă
current_page_html = driver.page_source
current_products_data = extract_product_data(current_page_html)
all_products_data.extend(current_products_data)

# Trecem la următoarea pagină (de la 2 la 8)
for page_number in range(2, 9):
    next_page_url = f"https://www.adpress.ro/comanda-advertoriale/page/{page_number}/"
    driver.get(next_page_url)
    time.sleep(3)
    next_page_html = driver.page_source
    next_page_products_data = extract_product_data(next_page_html)
    all_products_data.extend(next_page_products_data)

# Scriem informațiile extrase într-un fișier JSON
json_path = 'product_data_with_prices.json'
with open(json_path, 'w', encoding='utf-8') as json_file:
    json.dump(all_products_data, json_file, indent=4, ensure_ascii=False)

json_path  # Întoarcem calea fișierului pentru a informa utilizatorul unde a fost salvat JSON-ul

# Închidem driver-ul
driver.quit()
