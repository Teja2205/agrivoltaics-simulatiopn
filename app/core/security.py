
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import jwt as jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.models import schemas
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# In security.py - Update create_access_token function

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Increase default expiration time (e.g., from minutes to hours or days)
        expire = datetime.now(timezone.utc) + timedelta(
            days=7  # Extend to 7 days instead of minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hash password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Decode JWT token
def decode_token(token: str) -> Optional[schemas.TokenPayload]:
    try:
        # Log token information
        logger.info(f"Decoding token starting with: {token[:10]}...")
        
        # Log algorithm and other relevant info
        logger.info(f"Using algorithm: {settings.ALGORITHM}")
        
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.info(f"Token decoded successfully. Payload: {payload}")
        
        # Check required fields
        if 'sub' not in payload:
            logger.error("Token missing 'sub' field")
            return None
            
        if 'exp' not in payload:
            logger.error("Token missing 'exp' field")
            return None
        
        # Check expiration
        current_time = datetime.now(timezone.utc).timestamp()
        if payload['exp'] < current_time:
            logger.error(f"Token expired: {payload['exp']} < {current_time}")
            return None
        
        # Create token data
        try:
            token_data = schemas.TokenPayload(**payload)
            return token_data
        except ValidationError as val_err:
            logger.error(f"Validation error: {val_err}")
            return None
            
    except jwt.JWTError as e:
        logger.error(f"JWT error in decode_token: {str(e)}")
        return None
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in decode_token: {str(e)}")
        logger.error(traceback.format_exc())
        return None