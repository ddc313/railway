from fastapi import FastAPI, Request
import os
import requests
import hmac
import hashlib
import time
import json

app = FastAPI()

# Load secrets from Render Environment Variables
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")
WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")

# Log loaded environment variables (for debugging - optional)
print(f"API_KEY: {API_KEY}")
print(f"API_SECRET: {API_SECRET}")
print(f"API_PASSPHRASE: {API_PASSPHRASE}")
print(f"WEBHOOK_PASSWORD: {WEBHOOK_PASSWORD}")

@app.get("/")
def read_root():
    return {"message": "CoinCatch Bot Running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Optional password check
    if WEBHOOK_PASSWORD:
        if data.get("password") != WEBHOOK_PASSWORD:
            return {"status": "error", "message": "Invalid password"}

    # Get trading info
    side = data.get("signal")  # 'buy' or 'sell'
    symbol = data.get("symbol")  # example 'BTCUSDT'
    quantity = "0.001"  # you can adjust this as needed

    if not side or not symbol:
        return {"status": "error", "message": "Missing side or symbol in alert"}

    # Create timestamp
    timestamp = str(int(time.time() * 1000))

    # Build the order payload (no price = market order)
    body = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "timestamp": timestamp
    }

    message = json.dumps(body)

    # Create HMAC SHA256 signature
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
