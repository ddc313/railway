from fastapi import FastAPI, Request
import os
import requests
import hmac
import hashlib
import time
import json

app = FastAPI()

# Load secrets from Render Environment Variables
API_KEY = os.getenv("cc_ee8a71b0cccddc0dbe0ec0783a6d5aea")
API_SECRET = os.getenv("a431cc8b83239afb7d4bd7691ded4de69a916e9d9203eafbf47268a99a4d5da6")
API_PASSPHRASE = os.getenv("Blue3229")
WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")

@app.get("/")
def read_root():
    return {"message": "CoinCatch Bot Running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Check password (optional security from TradingView)
    if WEBHOOK_PASSWORD:
        if data.get("password") != WEBHOOK_PASSWORD:
            return {"status": "error", "message": "Invalid password"}

    # Extract trading signal from alert
    side = data.get("signal")  # 'buy' or 'sell'
    symbol = data.get("symbol")  # like 'BTCUSDT'
    price = data.get("price")  # optional
    quantity = "0.001"

    # Create timestamp
    timestamp = str(int(time.time() * 1000))

    # Build order payload
    body = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "timestamp": timestamp
    }

    message = json.dumps(body)

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
        response = requests.post("https://api.coincatch.com/v1/order", headers=headers, data=message)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
