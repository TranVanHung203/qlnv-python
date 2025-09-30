from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

# don't let HTTPBearer raise automatically — handle missing creds ourselves to return 401
security = HTTPBearer(auto_error=False)


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"], audience=settings.jwt_audience, issuer=settings.jwt_issuer)
        return payload
    except JWTError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        # no Authorization header or empty token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

    token = credentials.credentials
    payload = decode_jwt(token)
    return payload


def require_role(role: str):
    def _checker(user=Depends(get_current_user)):
        user_role = user.get('role') or user.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/role')
        if user_role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
        return user

    return _checker
