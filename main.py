from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class TelegramMessage(BaseModel):
    update_id: int
    message: Optional[dict]  # You can also model this in more detail if needed

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app!"}

@app.post("/webhook/telegram")
async def receive_telegram_message(payload: TelegramMessage):
    if payload.message:
        chat_id = payload.message["chat"]["id"]
        text = payload.message.get("text", "")
        print(f"Message from chat {chat_id}: {text}" + str(payload))
        # Here you can add logic like saving to DB, triggering another service, etc.
    return {"status": "ok"}
