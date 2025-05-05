import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="WSBANK API")

DATA_FILE = "cards.json"  # Change this to an absolute path if needed

# Load users from a JSON file
def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save users to JSON file
def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Load initial user data
users_db: Dict[str, Dict] = load_users()

# Data models
class CardAuth(BaseModel):
    card_number: str
    pin: str
    cvv: str
    exp: str

class Deposit(BaseModel):
    card_number: str
    amount: float

# Routes
@app.post("/atm/login")
def atm_login(data: CardAuth):
    user = users_db.get(data.card_number)
    if not user:
        raise HTTPException(status_code=404, detail="Card not found")
    if user["pin"] != data.pin or user["cvv"] != data.cvv or user["exp"] != data.exp:
        raise HTTPException(status_code=401, detail="Invalid card credentials")
    return {"message": f"Welcome {user['name']}", "balance": user["balance"]}

@app.post("/atm/deposit")
def deposit_check(data: Deposit):
    user = users_db.get(data.card_number)
    if not user:
        raise HTTPException(status_code=404, detail="Card not found")
    user["balance"] += data.amount
    save_users(users_db)
    return {"message": f"Deposit successful. New balance: ${user['balance']:.2f}"}

@app.get("/")
def root():
    return {"status": "API STARTED SUCCESSFULLY WITH JSON BACKEND"}
