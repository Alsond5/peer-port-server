from typing import Dict, List
import time

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = 50, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.request_records: Dict[str, List[float]] = {}
        
    async def is_rate_limited(self, client_id: str) -> bool:
        """Check if a client is rate limited"""
        now = time.time()
        
        # Initialize client record if not exists
        if client_id not in self.request_records:
            self.request_records[client_id] = []
            
        # Remove requests outside time window
        self.request_records[client_id] = [
            timestamp for timestamp in self.request_records[client_id]
            if now - timestamp <= self.time_window
        ]
        
        # Check if client has exceeded rate limit
        if len(self.request_records[client_id]) >= self.max_requests:
            return True
            
        # Add current request
        self.request_records[client_id].append(now)
        return False
        
    def cleanup(self):
        """Remove old rate limit records"""
        now = time.time()
        to_remove = []
        
        for client_id, timestamps in self.request_records.items():
            # Remove timestamps outside the window
            filtered = [t for t in timestamps if now - t <= self.time_window]
            if filtered:
                self.request_records[client_id] = filtered
            else:
                to_remove.append(client_id)
                
        for client_id in to_remove:
            del self.request_records[client_id]