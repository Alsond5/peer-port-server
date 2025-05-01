from fastapi import WebSocket
from typing import Dict, Optional, List, Set, Tuple
from app.domain.logger import logger
import uuid
import time
import asyncio

class PeerConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
        self.connections: Dict[str, WebSocket] = {}
        self.client_rooms: Dict[str, str] = {}
        self.active_clients: Set[str] = set()
        self.last_activity: Dict[str, float] = {}
        
    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()

        client_id = str(uuid.uuid4())

        self.connections[client_id] = websocket
        self.active_clients.add(client_id)
        self.last_activity[client_id] = time.time()

        logger.info(f"Client connected: {client_id}")

        return client_id

    async def disconnect(self, client_id: str) -> List[str]:
        peers_to_notify = []
        
        share_id = self.client_rooms.pop(client_id, None)
        
        self.connections.pop(client_id, None)
        self.active_clients.discard(client_id)
        self.last_activity.pop(client_id, None)

        if not share_id or share_id not in self.rooms:
            logger.info(f"Client disconnected: {client_id}")
            return peers_to_notify
        
        initiator_id, receiver_id = self.rooms[share_id]
        
        if initiator_id == client_id and receiver_id:
            peers_to_notify.append(receiver_id)
            self.client_rooms.pop(receiver_id, None)
        elif receiver_id == client_id and initiator_id:
            peers_to_notify.append(initiator_id)
            self.client_rooms.pop(initiator_id, None)
            
        self.rooms.pop(share_id, None)
                
        logger.info(f"Client disconnected: {client_id}")
        return peers_to_notify

    async def create_room(self, client_id: str) -> str:
        old_room = self.client_rooms.pop(client_id, None)

        if old_room and old_room in self.rooms:
            initiator_id, receiver_id = self.rooms[old_room]

            if initiator_id == client_id or receiver_id == client_id:
                self.rooms.pop(old_room, None)
        
        share_id = str(uuid.uuid4())

        self.rooms[share_id] = (client_id, None)
        self.client_rooms[client_id] = share_id
        self.last_activity[client_id] = time.time()

        logger.info(f"Room created: {share_id} by initiator {client_id}")
        return share_id

    async def join_room(self, client_id: str, share_id: str) -> Optional[str]:
        if share_id not in self.rooms:
            logger.warning(f"Room {share_id} not found")
            return None
            
        initiator_id, receiver_id = self.rooms[share_id]
        
        if receiver_id is not None:
            logger.warning(f"Room {share_id} is already full")
            return None
            
        self.rooms[share_id] = (initiator_id, client_id)
        
        self.client_rooms[client_id] = share_id
        self.last_activity[client_id] = time.time()
        
        logger.info(f"Client {client_id} joined room {share_id}")
        return initiator_id

    def get_peer_id(self, client_id: str) -> Optional[str]:
        share_id = self.client_rooms.get(client_id)
        if not share_id or share_id not in self.rooms:
            return None
            
        initiator_id, receiver_id = self.rooms[share_id]
        
        if client_id == initiator_id:
            return receiver_id
        elif client_id == receiver_id:
            return initiator_id
            
        return None

    async def send_to_peer(self, client_id: str, message: dict) -> bool:
        self.last_activity[client_id] = time.time()
        
        peer_id = self.get_peer_id(client_id)
        if not peer_id:
            logger.warning(f"No peer found for client {client_id}")
            return False
            
        websocket = self.connections.get(peer_id)
        if not websocket:
            logger.warning(f"Peer {peer_id} not found or not connected")
            return False
            
        try:
            await websocket.send_json({
                **message,
                "from": client_id
            })
            return True
        except Exception as e:
            logger.error(f"Failed to send message to peer {peer_id}: {str(e)}")
            return False
    
    async def send_to_client(self, target_id: str, message: dict) -> bool:
        websocket = self.connections.get(target_id)
        if not websocket:
            logger.warning(f"Client {target_id} not found or not connected")
            return False
            
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to client {target_id}: {str(e)}")
            return False
    
    def cleanup_inactive(self, timeout_seconds: int = 300) -> None:
        now = time.time()
        inactive_clients = [
            client_id for client_id, last_time in self.last_activity.items()
            if now - last_time > timeout_seconds
        ]
        
        for client_id in inactive_clients:
            logger.info(f"Cleaning up inactive client: {client_id}")
            asyncio.create_task(self.disconnect(client_id))

peer_manager = PeerConnectionManager()