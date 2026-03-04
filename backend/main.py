from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from stellar_sdk import Server
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


wish_wall = []

class Wish(BaseModel):
    address: str
    content: str

@app.get("/")
def home():
    return {
        "project": "Stellar Wish Wall dApp",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/api/balance/{address}")
def get_stellar_balance(address: str):
    server = Server("https://horizon-testnet.stellar.org")
    try:
        account = server.accounts().account_id(address).call()
        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                return {"balance": balance['balance'], "asset": "XLM"}
        return {"balance": "0", "asset": "XLM"}
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found on Testnet")


@app.post("/api/wish")
async def post_wish(wish: Wish):
    if len(wish.content) < 2:
        raise HTTPException(status_code=400, detail="Wish too short")
    
    new_entry = {
        "address": wish.address,
        "content": wish.content,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    wish_wall.insert(0, new_entry) 
    return {"status": "success", "data": new_entry}


@app.get("/api/wishes")
def get_wishes():
    return wish_wall

from fastapi.staticfiles import StaticFiles
import os

app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "..", "frontend")), name="static")