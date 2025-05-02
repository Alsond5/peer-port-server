from fastapi import Request, HTTPException, status, Depends
import os

def verify_admin_token(request: Request):
    expected_token = os.getenv("ADMIN_SECRET")
    provided_token = request.headers.get("X-Admin-Token")

    if not expected_token or provided_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )