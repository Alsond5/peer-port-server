from typing import Dict, Optional, Any
from pydantic import BaseModel, field_validator

class JoinPayload(BaseModel):
    share_id: Optional[str] = None
    
    @field_validator('share_id')
    def validate_share_id(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("share_id must be a string if provided")

        return v

class SignalingPayload(BaseModel):
    # Generic payload for signaling messages
    pass

class SignalingMessage(BaseModel):
    type: str
    payload: Dict[str, Any] = {}
    
    @field_validator('type')
    def validate_type(cls, v):
        valid_types = {'join', 'offer', 'answer', 'candidate', 'ready', 'bye'}
        
        if v not in valid_types:
            raise ValueError(f"Message type must be one of {valid_types}")

        return v