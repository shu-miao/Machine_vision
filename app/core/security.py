# 认证和安全相关功能
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from .config import settings

# 鉴权配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    """令牌数据结构"""
    user_id: str
    platform_id: str
    exp: datetime

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成JWT令牌"""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

async def verify_platform_token(token: str) -> bool:
    """验证平台令牌有效性"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.RESOURCE_ID
        )
        if payload is not None:
            return True
        else:
            return False
    except JWTError:
        return False

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not await verify_platform_token(token):
        raise credentials_exception
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.RESOURCE_ID
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return TokenData(**payload)
    except JWTError:
        raise credentials_exception