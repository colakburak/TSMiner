import time
import requests
from datetime import datetime

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
    # First, try to find the price in the 'apexPriceToPay' format
    price_container_apex = soup.find('span', class_='a-price a-text-price a-size-medium apexPriceToPay')
    if price_container_apex:
        price = price_container_apex.find('span', class_='a-offscreen')
        if price:
            return price.get_text().strip()

    # If not found, try the 'priceToPay' format
    price_container_pay = soup.find('span', class_='priceToPay')
    if price_container_pay:
        price_whole_container = price_container_pay.find('span', class_='a-price-whole')
        price_fraction_container = price_container_pay.find('span', class_='a-price-fraction')

        if price_whole_container and price_fraction_container:
            price_whole = price_whole_container.get_text().strip().rstrip('.')
            price_fraction = price_fraction_container.get_text().strip()
            return f"${price_whole}.{price_fraction}"

    # If neither format is found, return None
    return None


def extract_product_name(soup):
    product_title_container = soup.find('span', id='productTitle')
    if product_title_container:
        full_title = product_title_container.get_text().strip()
        # Extract the first word from the full title
        product_name = full_title.split()[0] + ' ' + full_title.split()[1] #TODO
        return product_name
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

if __name__ == "__main__":
    url1 = "https://www.amazon.com/Apple-iPhone-12-Pro-Max/dp/B09JFFG8D7/ref=sr_1_6?crid=8MSO83FCDWUG&keywords=iphone%2B15&qid=1706805433&sprefix=iphon%2Caps%2C183&sr=8-6&th=1"
    url2 = "https://www.amazon.com/Apple-MacBook-13-inch-256GB-Storage/dp/B08N5M7S6K/ref=sr_1_2?crid=20RP4A2A3OG&keywords=macbook&qid=1706808707&sprefix=macbook%2Caps%2C217&sr=8-2"
    url3 = "https://www.amazon.com/PHILIPS-Fully-Automatic-Espresso-Machine/dp/B08SJ7NFY1?ref_=Oct_DLandingS_D_db300cfc_1&th=1"
    
    urlList = [url1, url2, url3]
    
    # for url in urlList:
    #     main(url)

    while True:
        for url in urlList:
            main(url)
            print(f"Completed scraping {url}. Waiting for next hour...")
        print("Completed all URLs. Waiting for one hour to restart...")
        time.sleep(600)  # Every 10 min