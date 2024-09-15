# backend/app/routes/clients.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
from config import CLIENT_DB_FILE
from utils.general_utils import load_clients, save_metadata

# Add this line to configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class Client(BaseModel):
    name: str
    keywords: List[str]
    details: str

def save_clients(clients):
    """
    Saves the clients dictionary to the client_database.json file.
    """
    with open(CLIENT_DB_FILE, 'w') as f:
        json.dump(clients, f)
    logger.info(f"Saved {len(clients)} clients to {CLIENT_DB_FILE}")

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
