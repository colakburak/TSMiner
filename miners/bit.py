import time
import requests
import json

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


from webdriver_manager.chrome import ChromeDriverManager


from bs4 import BeautifulSoup
from fake_useragent import UserAgent




def get_html_content(url):
    ua = UserAgent(min_percentage=1.3)
    headers = {
        "User-Agent": ua.random,
        'Accept': '*/*', 
        'Accept-Encoding': 'gzip, deflate, br', 
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)
    else:
        return response.content

def extract_price(soup):
    price_container = soup.find('span', class_='currency-pricestyles__Price-sc-1v249sx-0 jobFak')
    if price_container:
        return price_container.get_text().strip()
    return None

def extract_product_name(soup):
    product_name_container = soup.find('h1', class_='typography__StyledTypography-sc-owin6q-0 kEoLlg long-title')
    if product_name_container:
        return product_name_container.get_text().strip()
    return None

def main(url):
    html_content = get_html_content(url)

    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        product_name = extract_product_name(soup)
        price = extract_price(soup)

        if product_name and price:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res = {product_name: {'price': price, 'timestamp': timestamp}}
            # res = {product_name: price}
            print(res)
        else:
            if product_name:
                print(f"Product Name: {product_name}")
            else:
                print("Product name could not be found.")

            if price:
                print(f"Price: {price}")
            else:
                print("Price information could not be found.")

def handle_cookie_popup(driver):
    try:
        # Wait for the cookie consent dialog to appear
        wait = WebDriverWait(driver, 10)
        # Find the "OK" button by its ID and click it
        ok_button = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept")))
        ok_button.click()
    except Exception as e:
        print("Cookie pop-up not found or other error: ", e)

def get_bitcoin_price(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get(url)

    handle_cookie_popup(driver)


    # Wait for the element to load
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak"))
    )

    # Extract the data
    product_name = driver.find_element(By.CSS_SELECTOR, ".typography__StyledTypography-sc-owin6q-0.kEoLlg.long-title").text
    price = driver.find_element(By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak").text

    # Close the WebDriver
    driver.quit()
    # while True:
    #     pass

    # Get the timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print({product_name: {'price': price, 'timestamp': timestamp}})
    # Return the result
    return {product_name: {'price': price, 'timestamp': timestamp}}

def monitor_bitcoin_price(url):
    # Set Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") # This may be required when running as root (e.g., in Docker containers)
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the webpage
    driver.get(url)
    handle_cookie_popup(driver)

    last_price = None

    while True:
        try:
            # Wait for the element to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak"))
            )

            # Extract the data
            product_name = driver.find_element(By.CSS_SELECTOR, ".typography__StyledTypography-sc-owin6q-0.kEoLlg.long-title").text
            price = driver.find_element(By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak").text

            # Compare with the last price
            if price != last_price:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {product_name: {'price': price, 'timestamp': timestamp}}
                print(data)
                response = requests.post('http://0.0.0.0:8000/data', json=data)
                # Check the response
                if response.status_code == 200:
                    print("Data sent successfully")
                else:
                    print("Failed to send data")

                last_price = price

            # Wait before checking again
            time.sleep(5)  # Check every minute, adjust as needed

        except Exception as e:
            print("Error occurred, retrying: ", e)
            # Optionally, refresh the page or reinitialize the driver
            driver.quit()
            driver = webdriver.Chrome(service=service)
            driver.get(url)
            handle_cookie_popup(driver)


if __name__ == "__main__":
    url = "https://www.coindesk.com/price/bitcoin/"
    
    # while True:
    #     # main(url)
    #     get_bitcoin_price(url)
    #     time.sleep(600)

    monitor_bitcoin_price(url)