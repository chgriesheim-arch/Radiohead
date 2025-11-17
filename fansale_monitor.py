import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests


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


def check_fansale():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(FANSALE_URL)
        time.sleep(5)

        offers = driver.find_elements(By.CSS_SELECTOR, "div.ticket-overview")

        results = []
        for offer in offers:
            try:
                title = offer.find_element(By.CSS_SELECTOR, ".ticket-title").text.strip()
                price = offer.find_element(By.CSS_SELECTOR, ".price").text.strip()
                link = offer.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                results.append({
                    "title": title,
                    "price": price,
                    "url": link
                })
            except:
                continue

        return results

    finally:
        driver.quit()


def main():
    print("Checking FanSale...")
    new_state = check_fansale()
    old_state = load_last_state()

    if new_state != old_state:
        save_last_state(new_state)

        if len(new_state) > 0:
            msg = f"🎟️ Neue Radiohead-Tickets gefunden!\n\n"
            for t in new_state:
                msg += f"- {t['title']} – {t['price']}\n{t['url']}\n\n"
        else:
            msg = "❌ Tickets wieder ausverkauft."

        send_telegram(msg)
        print(msg)
    else:
        print("Keine Änderungen.")

    print("Fertig.")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
