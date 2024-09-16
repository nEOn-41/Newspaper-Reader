from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
from ..config import CLIENT_DB_FILE
from ..utils.general_utils import load_clients, save_metadata
from ..utils.custom_exceptions import ClientManagementError, ResourceNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()

class Client(BaseModel):
    """
    Pydantic model for client data.
    """
    name: str
    keywords: List[str]
    details: str

def save_clients(clients: Dict[str, Any]) -> None:
    """
    Saves the clients dictionary to the client_database.json file.

    Args:
        clients (Dict[str, Any]): Dictionary containing client data.
    """
    try:
        with open(CLIENT_DB_FILE, 'w') as f:
            json.dump(clients, f)
        logger.info(f"Saved {len(clients)} clients to {CLIENT_DB_FILE}")
    except Exception as e:
        logger.error(f"Failed to save clients: {str(e)}")
        raise ClientManagementError(f"Failed to save clients: {str(e)}")

@router.post("/clients")
async def add_client(client: Client) -> Dict[str, str]:
    """
    Adds a new client to the database.

    Args:
        client (Client): Client data to be added.

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        ClientManagementError: If the client already exists or if there's an error adding the client.
    """
    clients = load_clients()
    
    if client.name in clients:
        raise ClientManagementError(f"Client '{client.name}' already exists")
    
    try:
        clients[client.name] = {
            "keywords": client.keywords,
            "details": client.details
        }
        save_clients(clients)
        return {"message": f"Client {client.name} added successfully"}
    except Exception as e:
        logger.error(f"Failed to add client {client.name}: {str(e)}")
        raise ClientManagementError(f"Failed to add client {client.name}: {str(e)}")

@router.get("/clients")
async def get_clients() -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves all clients from the database.

    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing a list of all clients.

    Raises:
        ClientManagementError: If there's an error retrieving clients.
    """
    try:
        clients = load_clients()
        return {"clients": [{"name": name, **data} for name, data in clients.items()]}
    except Exception as e:
        logger.error(f"Failed to retrieve clients: {str(e)}")
        raise ClientManagementError(f"Failed to retrieve clients: {str(e)}")

@router.put("/clients/{client_name}")
async def update_client(client_name: str, client: Client) -> Dict[str, str]:
    """
    Updates an existing client in the database.

    Args:
        client_name (str): Name of the client to be updated.
        client (Client): Updated client data.

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        ResourceNotFoundError: If the client is not found.
        ClientManagementError: If there's an error updating the client.
    """
    clients = load_clients()
    if client_name not in clients:
        raise ResourceNotFoundError("Client", client_name)
    
    try:
        clients[client_name] = {
            "keywords": client.keywords,
            "details": client.details
        }
        save_clients(clients)
        return {"message": f"Client {client_name} updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update client {client_name}: {str(e)}")
        raise ClientManagementError(f"Failed to update client {client_name}: {str(e)}")

@router.delete("/clients/{client_name}")
async def delete_client(client_name: str) -> Dict[str, str]:
    """
    Deletes a client from the database.

    Args:
        client_name (str): Name of the client to be deleted.

    Returns:
        Dict[str, str]: A dictionary containing a success message.

    Raises:
        ResourceNotFoundError: If the client is not found.
        ClientManagementError: If there's an error deleting the client.
    """
    clients = load_clients()
    if client_name not in clients:
        raise ResourceNotFoundError("Client", client_name)
    
    try:
        del clients[client_name]
        save_clients(clients)
        return {"message": f"Client {client_name} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete client {client_name}: {str(e)}")
        raise ClientManagementError(f"Failed to delete client {client_name}: {str(e)}")