from fastapi import FastAPI, Request
import os
import requests
import hmac
import hashlib
import time
import json

app = FastAPI()

# Load environment variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")
WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")

# Simple health check
@app.get("/")
def read_root():
    return {"message": "CoinCatch Bot Running"}

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Optional password check
    if WEBHOOK_PASSWORD:
        if data.get("password") != WEBHOOK_PASSWORD:
            print("Invalid password attempt!")
            return {"status": "error", "message": "Invalid password"}

    # Check important fields
    side = data.get("signal")  # 'buy' or 'sell'
    symbol = data.get("symbol")
    price = data.get("price")

    if not all([side, symbol, price]):
        print("Missing required fields in webhook payload")
        return {"status": "error", "message": "Missing signal, symbol, or price"}

    quantity = "0.001"  # you can adjust quantity if needed

    # Create order payload
    timestamp = str(int(time.time() * 1000))
    order_payload = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "timestamp": timestamp
    }
    message = json.dumps(order_payload)

    # Make sure secrets are loaded
    if not all([API_KEY, API_SECRET, API_PASSPHRASE]):
        print("Environment variables not loaded properly")
        return {"status": "error", "message": "Server configuration error"}

    # Create signature
    signature = hmac.new(
        API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-API-KEY": API_KEY,
        "X-API-PASSPHRASE": API_PASSPHRASE,
        "X-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

    # Send order to CoinCatch
    try:
        response = requests.post("https://api.coincatch.com/v1/order", headers=headers, data=message)
        response.raise_for_status()

        resp_json = response.json()

        # Check if API returns an error inside 200 OK
        if "error" in resp_json:
            print(f"ORDER ERROR: {resp_json['error']}")
            return {"status": "error", "message": resp_json['error']}

        print(f"SUCCESS: Order sent to CoinCatch for {symbol} {side} at {price}")
        return {"status": "success", "response": resp_json}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ERROR: {http_err.response.status_code} {http_err.response.text}")
        return {"status": "error", "message": f"HTTP error {http_err.response.status_code}"}
    except Exception as e:
        print(f"GENERAL ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}
