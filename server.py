from fastapi import FastAPI, Request
import os
import hmac
import hashlib
import time
import json
import requests

app = FastAPI()

# Environment Variables (set these in Render)
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("API_PASSPHRASE")
WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")

@app.get("/")
def read_root():
    return {"status": "CoinCatch Bot Live"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Validate TradingView password
    if WEBHOOK_PASSWORD and data.get("password") != WEBHOOK_PASSWORD:
        return {"status": "error", "message": "Invalid password"}

    # Parse fields
    symbol = data.get("symbol", "XRPUSDT_UMCBL")
    marginCoin = data.get("marginCoin", "USDT")
    side = data.get("side", "open_long")  # open_long or open_short
    orderType = data.get("orderType", "market")
    quantity = data.get("size", "30")  # YOU can change this per trade
    timeInForceValue = data.get("timeInForceValue", "normal")

    timestamp = str(int(time.time() * 1000))

    payload = {
        "symbol": symbol,
        "marginCoin": marginCoin,
        "size": quantity,
        "side": side,
        "orderType": orderType,
        "timeInForceValue": timeInForceValue,
        "timestamp": timestamp
    }

    message = json.dumps(payload)

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
        return {
            "status": "success",
            "response": response.json()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
