"""
Shared FastAPI dependencies, mainly for authentication.
"""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.db.database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise CREDENTIALS_EXCEPTION

    try:
        user_id = ObjectId(payload["sub"])
    except InvalidId:
        raise CREDENTIALS_EXCEPTION

    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise CREDENTIALS_EXCEPTION
    return user


def object_id_or_404(id_str: str, entity_name: str = "Resource") -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found")
