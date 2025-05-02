from fastapi import APIRouter, Depends
from app.services.peer_manager import peer_manager
from app.dependencies import verify_admin_token

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(verify_admin_token)]
)

@router.get("/health")
async def health_check():
    peer_manager.cleanup_inactive()
    
    return {
        "status": "ok", 
        "active_rooms": len(peer_manager.rooms),
        "active_clients": len(peer_manager.connections)
    }

@router.get("/stats")
async def server_stats():
    room_details = {
        share_id: {
            "initiator": initiator_id,
            "receiver": receiver_id
        } 
        for share_id, (initiator_id, receiver_id) in peer_manager.rooms.items()
    }
    
    return {
        "active_rooms": len(peer_manager.rooms),
        "active_clients": len(peer_manager.connections),
        "active_client_ids": list(peer_manager.active_clients),
        "room_details": room_details
    }