from fastapi import FastAPI, Request
import os
import requests
import hmac
import hashlib
import time
import json

app = FastAPI()

# Load secrets from environment variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")
WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")

@app.get("/")
def read_root():
    return {"message": "CoinCatch Bot Running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Verify webhook password
    if WEBHOOK_PASSWORD and data.get("password") != WEBHOOK_PASSWORD:
        return {"status": "error", "message": "Invalid password"}

    # Extract trading details
    side = data.get("signal")  # 'buy' or 'sell'
    symbol = data.get("symbol")  # like 'BTCUSDT'
    price = data.get("price")
    quantity = "0.001"  # You can adjust quantity if needed

    # Build order payload
    timestamp = str(int(time.time() * 1000))
    order_payload = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "timestamp": timestamp
    }
    message = json.dumps(order_payload)

    # Create HMAC signature
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

    try:
        response = requests.post(
            "https://api.coincatch.com/v1/order",
            headers=headers,
            data=message
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
