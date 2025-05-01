from fastapi import WebSocket
from typing import Optional, Any
from app.services.peer_manager import peer_manager
from app.domain.logger import logger

async def send_error(websocket: WebSocket, error: str):
    await websocket.send_json({
        "type": "error",
        "payload": {
            "message": error
        }
    })

async def send_message(websocket: WebSocket, type: str, payload: Any):
    await websocket.send_json({
        "type": type,
        "payload": payload
    })

async def send_to_client(client_id: str, type: str, payload: Any):
    await peer_manager.send_to_client(client_id, {
        "type": type,
        "payload": payload
    })

async def send_to_peer(client_id: str, type: str, payload: Any):
    return await peer_manager.send_to_peer(client_id, {
        "type": type,
        "payload": payload
    })

async def join(websocket: WebSocket, client_id: str, share_id: Optional[str]):
    if not share_id:
        share_id = await peer_manager.create_room(client_id)

        type = "create"
        payload = {
            "share_id": share_id,
            "client_id": client_id
        }
        
        await send_message(websocket, type, payload)
        return True
    
    initiator_id = await peer_manager.join_room(client_id, share_id)

    if not initiator_id:
        error = "Failed to join room. Room may not exist or is already full."

        await send_error(websocket, error)
        
        logger.info(f"Closing connection for client {client_id} - invalid room join attempt")
        return False
        
    type = "join"
    payload = {
        "client_id": client_id,
        "peer_id": initiator_id
    }

    await send_message(websocket, type, payload)

    type = "joined"
    payload = {
        "peer_id": client_id
    }

    await send_to_client(initiator_id, type, payload)
    return True

async def ready(websocket: WebSocket, client_id: str):
    type = "ready"
    payload = {
        "peer_id": client_id
    }

    success = await send_to_peer(client_id, type, payload)
    
    if not success:
        error = "Failed to send message to peer. Peer may have disconnected."

        await send_error(websocket, error)

    return success

async def disconnect(client_id: str):
    peer_id = peer_manager.get_peer_id(client_id)
    
    if not peer_id:
        return
    
    type = "disconnect"
    payload = {
        "client_id": client_id
    }

    await send_to_client(peer_id, type, payload)
    
    if peer_id not in peer_manager.connections:
        return

    logger.info(f"Disconnecting peer {peer_id} due to disconnect message from {client_id}")
    peers_websocket = peer_manager.connections.get(peer_id)
    
    if peers_websocket:
        await peers_websocket.close(code=1000, reason="Peer sent disconnect message")
    