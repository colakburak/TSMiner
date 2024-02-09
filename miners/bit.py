import time
import requests
import json
import asyncio
import websockets

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

# TODO useragent rotater
# ua = UserAgent(min_percentage=1.3)

# Global variable for the WebSocket
websocket_connection = None

async def connect_websocket(miner_id):
    global websocket_connection
    try:
        websocket_uri = f"ws://localhost:8000/ws/{miner_id}"
        websocket_connection = await websockets.connect(websocket_uri)
    except Exception as e:
        print(f"Failed to connect to WebSocket: {e}")
        # Implement reconnection logic if needed

async def send_via_websocket(data, miner_id):
    global websocket_connection
    if not websocket_connection or not websocket_connection.open:
        await connect_websocket(miner_id)  # Pass the miner_id
    try:
        await websocket_connection.send(json.dumps(data))
    except Exception as e:
        print(f"Error sending data: {e}")
        # Reconnect if sending failed
        await connect_websocket(miner_id)  # Pass the miner_id
        await websocket_connection.send(json.dumps(data))


def handle_cookie_popup(driver):
    try:
        # Wait for the cookie consent dialog to appear
        wait = WebDriverWait(driver, 10)
        # Find the "OK" button by its ID and click it
        ok_button = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonAccept")))
        ok_button.click()
    except Exception as e:
        print("Cookie pop-up not found or other error: ", e)

async def monitor_bitcoin_price(url, miner_id):
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

    while True:
        try:
            # Wait for the element to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak"))
            )

            # Extract the data
            product_name = driver.find_element(By.CSS_SELECTOR, ".typography__StyledTypography-sc-owin6q-0.kEoLlg.long-title").text
            price = driver.find_element(By.CSS_SELECTOR, ".currency-pricestyles__Price-sc-1v249sx-0.jobFak").text

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {product_name: {'price_in_usd': price, 'timestamp': timestamp}}
            print(data, miner_id)
            await send_via_websocket(data, miner_id)

            # Wait before checking again
            await asyncio.sleep(5)

        except Exception as e:
            print("Error occurred, retrying: ", e)
            # Optionally, refresh the page or reinitialize the driver
            driver.quit()
            driver = webdriver.Chrome(service=service)
            driver.get(url)
            handle_cookie_popup(driver)


async def main():
    url1 = "https://www.coindesk.com/price/bitcoin/"
    url2 = "https://www.coindesk.com/price/ethereum/"
    url3 = "https://www.coindesk.com/price/solana/"
    miner_id1 = 'btc-miner-01'
    miner_id2 = 'eth-miner-01'
    miner_id3 = 'sol-miner-01'

    # asyncio.run(monitor_bitcoin_price(url2, miner_id))
    # asyncio.run(monitor_bitcoin_price(url, miner_id2))

    await asyncio.gather(
        monitor_bitcoin_price(url1, miner_id1),
        monitor_bitcoin_price(url2, miner_id2),
        monitor_bitcoin_price(url3, miner_id3)
    )

if __name__ == "__main__":
    asyncio.run(main())
