from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from config import CLIENT_DB_FILE

router = APIRouter()

class Client(BaseModel):
    name: str
    keywords: List[str]
    details: str

def load_clients():
    if CLIENT_DB_FILE.exists():
        with open(CLIENT_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_clients(clients):
    with open(CLIENT_DB_FILE, 'w') as f:
        json.dump(clients, f)

@router.post("/clients")
async def add_client(client: Client):
    clients = load_clients()
    
    if client.name in clients:
        raise HTTPException(status_code=400, detail="Client already exists")
    
    clients[client.name] = {
        "keywords": client.keywords,
        "details": client.details
    }
    save_clients(clients)
    return {"message": f"Client {client.name} added successfully"}

@router.get("/clients")
async def get_clients():
    clients = load_clients()
    return {"clients": [{"name": name, **data} for name, data in clients.items()]}

@router.put("/clients/{client_name}")
async def update_client(client_name: str, client: Client):
    clients = load_clients()
    if client_name not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    clients[client_name] = {
        "keywords": client.keywords,
        "details": client.details
    }
    save_clients(clients)
    return {"message": f"Client {client_name} updated successfully"}

@router.delete("/clients/{client_name}")
async def delete_client(client_name: str):
    clients = load_clients()
    if client_name not in clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    del clients[client_name]
    save_clients(clients)
    return {"message": f"Client {client_name} deleted successfully"}