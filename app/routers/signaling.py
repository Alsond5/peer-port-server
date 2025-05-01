from fastapi import WebSocket, APIRouter, WebSocketDisconnect, WebSocketException, status
from app.services.peer_manager import peer_manager
from contextvars import ContextVar

from app.domain.logger import logger
from app.utils.validators import validate_message
from app.websocket import send_error, join, ready, send_to_peer, disconnect, MessageType
from app.schemas.signaling import JoinPayload

router = APIRouter()

request_id_var: ContextVar[str] = ContextVar('request_id', default='')

@router.websocket("/signal")
async def signaling_gateway(websocket: WebSocket):
    client_id = None

    try:
        client_id = await peer_manager.connect(websocket)
        request_id_var.set(client_id)

        async def check_rate_limit():
            if await websocket.app.state.rate_limiter.is_rate_limited(client_id):
                logger.warning(f"Client {client_id} exceeded rate limit")
                error = "Rate limit exceeded. Please try again later."

                await send_error(websocket, error)

                raise WebSocketDisconnect(code=status.HTTP_429_TOO_MANY_REQUESTS)

        while True:
            await check_rate_limit()

            raw_data = await websocket.receive_json()

            try:
                data = await validate_message(raw_data)
            except ValueError as e:
                await send_error(websocket, str(e))

            message_type = data.type
            payload = data.payload

            if message_type == MessageType.JOIN:
                try:
                    join_payload = JoinPayload(**payload)
                    share_id = join_payload.share_id
                except ValueError as e:
                    await send_error(websocket, str(e))

                    break

                success = await join(websocket, client_id, share_id)
                
                if not success:
                    break

            elif message_type == MessageType.READY:
                success = await ready(websocket, client_id)

                if not success:
                    break

            elif message_type in [MessageType.OFFER, MessageType.ANSWER, MessageType.CANDIDATE]:
                success = await send_to_peer(client_id, message_type, payload)

                if not success:
                    error = "Failed to send message to peer. Peer may have disconnected."
                    await send_error(websocket, error)

                    break

            elif message_type == MessageType.DISCONNECT:
                await disconnect(client_id)

                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client {client_id}")
    except WebSocketException as e:
        logger.error(f"Error handling WebSocket for {client_id}: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Error handling WebSocket for {client_id}: {str(e)}", exc_info=True)
    finally:
        if not client_id:
            return
        
        peers_to_notify = await peer_manager.disconnect(client_id)

        for peer_id in peers_to_notify:
            if peer_id not in peer_manager.connections:
                continue
            
            try:
                await peer_manager.send_to_client(peer_id, {
                    "type": "peer_disconnected",
                    "payload": {
                        "client_id": client_id
                    }
                })
                
                peers_websocket = peer_manager.connections.get(peer_id)

                if peers_websocket:
                    logger.info(f"Closing peer {peer_id} connection due to disconnection of {client_id}")

                    await peers_websocket.close(code=1000, reason="Peer disconnected")
                    await peer_manager.disconnect(peer_id)

            except Exception as e:
                logger.error(f"Error notifying peer {peer_id} about disconnection: {str(e)}")