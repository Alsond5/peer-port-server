from enum import Enum

class MessageType(str, Enum):
    JOIN = "join"
    READY = "ready"
    OFFER = "offer"
    ANSWER = "answer"
    CANDIDATE = "candidate"
    DISCONNECT = "disconnect"
    ERROR = "error"