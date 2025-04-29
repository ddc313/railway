from fastapi import FastAPI, Request
import os

app = FastAPI()

# Optional security check
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')

@app.get("/")
def read_root():
    return {"message": "CoinCatch Bot Running!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    # If you set a webhook password, validate it
    if WEBHOOK_PASSWORD:
        if data.get("password") != WEBHOOK_PASSWORD:
            return {"code": 403, "message": "Forbidden: Incorrect password"}
    
    # Log received data
    print("Received data:", data)

    # Here, you would add logic to send the signal to CoinCatch, Binance, Bybit, etc.
    # For now, just return a success
    return {"code": 200, "message": "Signal received!"}
