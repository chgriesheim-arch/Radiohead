import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

FANSALE_URL = "https://www.fansale.de/tickets/all/radiohead/520"
CHECK_INTERVAL = 60  # Sekunden

MIN_TICKETS = 2
MAX_TICKETS = 4
DATES = ["08.12.2025", "09.12.2025", "11.12.2025", "12.12.2025"]

# Telegram Token und Chat-ID aus Umgebungsvariablen
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

known_offers = set()

def telegram_notify(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)


def check_fansale():
    print(f"[{datetime.now()}] Checking FanSale…")

    r = requests.get(FANSALE_URL, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = soup.select(".article")

    new_hits = []

    for offer in offers:
        text = offer.get_text(strip=True)
        offer_id = hash(text)

        if any(date in text for date in DATES):
            for n in range(MIN_TICKETS, MAX_TICKETS + 1):
                if f"{n} Ticket" in text or f"{n} Tickets" in text:
                    if offer_id not in known_offers:
                        known_offers.add(offer_id)
                        new_hits.append(text)

    return new_hits


def main():
    telegram_notify("FanSale Monitor gestartet (GitHub Actions).")
    print("Monitor läuft…")

    new = check_fansale()
    if new:
        message = "🎟️ **Neue Radiohead Tickets!**\n\n"
        message += "\n\n".join(new)
        message += f"\n\nLink: {FANSALE_URL}"
        telegram_notify(message)
    else:
        print("Keine neuen Tickets.")


if __name__ == "__main__":
    main()
