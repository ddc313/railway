from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received webhook:", data)

    action = data.get("action")
    symbol = data.get("symbol", "BTCUSDT")

    if action == "buy":
        print(f"Execute BUY order for {symbol}")
        # TODO: Add CoinCatch buy logic here

    elif action == "sell":
        print(f"Execute SELL order for {symbol}")
        # TODO: Add CoinCatch sell logic here

    return {"message": "Webhook received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
