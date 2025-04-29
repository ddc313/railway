from fastapi import FastAPI, Request
import os
import requests
import hmac
import hashlib
import time
import json

app = FastAPI()

# Load secrets from environment
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

    # Verify TradingView password
    if WEBHOOK_PASSWORD and data.get("password") != WEBHOOK_PASSWORD:
        return {"status": "error", "message": "Invalid password"}

    # Extract fields
    side = data.get("side")         # "buy" or "sell"
    symbol = data.get("symbol")     # like "BTCUSDT"
    quantity = data.get("quantity") # like "0.0005"

    if not side or not symbol or not quantity:
        return {"status": "error", "message": "Missing side, symbol, or quantity"}

    timestamp = str(int(time.time() * 1000))

    # Build the order payload
    payload = {
        "symbol": symbol,
        "side": side,
        "orderType": "market",
        "quantity": quantity,
        "reduceOnly": False,          # Important: allows flipping, not just closing
        "timestamp": timestamp
    }

    # Prepare signature
    message = json.dumps(payload)
    signature = hmac.new(
        API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Headers for CoinCatch API
    headers = {
        "X-API-KEY": API_KEY,
        "X-API-PASSPHRASE": API_PASSPHRASE,
        "X-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

    try:
        # Send market order
        response = requests.post("https://api.coincatch.com/v1/order", headers=headers, data=message)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
