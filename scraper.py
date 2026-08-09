import os
import requests

# Ang Webhook URL na kinopya mo mula sa Make.com
WEBHOOK_URL = "https://hook.eu1.make.com/ys71tgwopbgnfogxguktq3cuiftud9l9"

def send_to_make():
    # Dito ilalagay ang code para kunin ang pinakabagong post o advisory
    # Halimbawa ng data na ipapadala:
    payload = {
    "substation": "Daraga Substation",
    "date": "2026-08-10",
    "post_time": "1:04 AM"
}

    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {response.status_code}")

if __name__ == "__main__":
    send_to_make()
