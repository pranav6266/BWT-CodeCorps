# backend/utils/clerk_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    print(f"[Auth] Received token: {token[:30] if token else 'None'}...")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        # Decode JWT without verification to get the user ID (sub claim)
        # This works because Clerk tokens are signed but we just need the payload
        # For production, you'd want to verify with Clerk's JWKS
        decoded = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded.get("sub")
        print(f"[Auth] Decoded user_id: {user_id}")
        return user_id
    except jwt.PyJWTError as e:
        print(f"[Auth] JWT decode error: {e}")
        # Fallback: return token as user_id (for development/testing)
        return token
