from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests
import json
from bs4 import BeautifulSoup

app = FastAPI()
TG_PF_TOKEN = "8045296664:AAEZH-p2ukcxSIYofzl5EkuwzZe2wNJ36uk"
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
        text = payload.message.get("text", "") or ""
        print(f"Message from chat {chat_id}: {text}" + str(payload))
        print(text.lower().strip())
        if text.lower().strip() == "start":
            body = {
                "chat_id" : chat_id,
                "text" : """💬 <b>Please send the exact perfume name starting with N:</b>
📌 <i>Example:</i> N: rasasi hawas ice""",
                "parse_mode" : "HTML"
            }
            response = requests.post(f"https://api.telegram.org/bot{TG_PF_TOKEN}/sendMessage",data=body)
            print(response)
            if response.status_code == 200:
                print("message sent")
        
        elif text.lower().strip().startswith("n:") :
            perfume_name = text.split(":")[1].strip()
            found_products = []
            found_products.append(scrape_frag_flex(perfume_name))
            message = "<b>🛍️ Perfume Price List:</b>\n\n"

            for perfume in found_products:
                message += f"🔹 <b>{perfume['name']}</b>\n"
                message += f"💵 Price: <i>{perfume['price']}</i>\n"
                message += f"🔗 <a href=\"{perfume['url']}\">View Product</a>\n\n"
                
            body = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(f"https://api.telegram.org/bot{TG_PF_TOKEN}/sendMessage",data=body)
            print(response)
            if response.status_code == 200:
                print("message sent")

            
            
        # Here you can add logic like saving to DB, triggering another service, etc.
    return {"status": "ok"}

async def scrape_frag_flex(perfume_name: str):
    product_name = perfume_name.lower().strip()
    matched_product = None
    URL = "https://fragflex.com/search?q="+product_name.replace(" ","+")  # Replace with the actual URL
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Fetch the page
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    perfumes_list = []

    # Select all matching elements
    item_names = soup.select(
        "div.ctm-vendor.caption-with-letter-spacing.light"
    )

    item_prices = soup.select(
        "div.price__container",
    )

    base_url = "https://fragflex.com"
    links = [
        base_url + tag.get("href")
        for tag in soup.select("a.full-unstyled-link.product")
    ]

    for item_name,item_price,link,perfume in zip(item_names,item_prices,links,perfumes_list):
        # Try to get sale price first
        sale = item_price.select_one("span.price-item--sale span.transcy-money")
        if sale:
            price = sale.get_text(strip=True)
        else:
            # Fall back to regular price if no sale price
            regular = item_price.select_one("span.price-item--regular span.transcy-money")
            price = regular.get_text(strip=True) if regular else "Sold out"

        perfumes_list.append({
            "name":item_name.get_text(strip=True),
            "price" : price,
            "url" : link
        })

    for perfume in perfumes_list:
        print(perfume)
        if perfume.name.lower().strip().includes(product_name.lower().strip()):
            matched_product = perfume

    return matched_product
    
# update_id=286367997 message={'message_id': 10, 'from': {'id': 831992637, 'is_bot': False, 'first_name': 'S#EIK#', 'language_code': 'en'}, 'chat': {'id': 831992637, 'first_name': 'S#EIK#', 'type': 'private'}, 'date': 1748461075, 'text': 'Start'}