from app.schemas.signaling import SignalingMessage
from app.domain.logger import logger

async def validate_message(message: dict) -> SignalingMessage:
    """Validate incoming message against schema."""
    try:
        return SignalingMessage(**message)
    except Exception as e:
        logger.warning(f"Invalid message: {str(e)}")
        raise ValueError(f"Message validation failed: {str(e)}")