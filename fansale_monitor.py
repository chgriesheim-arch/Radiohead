import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

FANSALE_URL = "https://www.fansale.de/tickets/all/radiohead/520"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LAST_STATE_FILE = "last_tickets.json"

def send_telegram(msg: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

def load_last_state():
    if not os.path.exists(LAST_STATE_FILE):
        return []
    try:
        with open(LAST_STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_last_state(state):
    with open(LAST_STATE_FILE, "w") as f:
        json.dump(state, f)

def fetch_fansale_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(FANSALE_URL)
        time.sleep(5)

        tickets = []
        rows = driver.find_elements(By.CSS_SELECTOR, ".ticket-list-entry")
        for row in rows:
            try:
                price = row.find_element(By.CSS_SELECTOR, ".price").text
                block = row.find_element(By.CSS_SELECTOR, ".block").text
                tickets.append({"price": price, "block": block})
            except:
                pass

        return tickets

    except Exception as e:
        print("Selenium error:", e)
        return []

    finally:
        driver.quit()

def main():
    print("Fetching Fansale page via Selenium ...")

    new_tickets = fetch_fansale_selenium()
    last_tickets = load_last_state()

    if new_tickets != last_tickets:
        print("Change detected!")
        save_last_state(new_tickets)
        send_telegram("Neue Tickets oder Änderungen auf Fansale!")
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
