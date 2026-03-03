# backend/utils/clerk_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    # TODO: Implement full PyJWT decoding using your Clerk Secret Key
    # For now, this ensures the endpoint requires a Bearer token.
    # While testing in Postman/Swagger, whatever string you put as the token
    # will act as your "clerk_user_id".

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return token  # Returning the token as the user_id for immediate routing setup