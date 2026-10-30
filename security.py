from datetime import datetime, UTC, timedelta
from pwdlib import PasswordHash
import jwt
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = "HS256"

password_hash = PasswordHash.recommended()

# Generate a hashed password
def generate_hashed_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# Create an access token
def create_access_token(data: dict) -> str:
    token_expiry = datetime.now(UTC) + timedelta(minutes=10)

    payload = {**data, "iat": datetime.now(UTC), "exp": token_expiry, "type": "access"}
    return jwt.encode(
            payload=payload, key=secret_key, algorithm=algorithm
        )

# Create a refresh token
def create_refresh_token(data: dict) -> str:
    token_expiry = datetime.now(UTC) + timedelta(days=7)

    payload = {**data, "iat": datetime.now(UTC), "exp": token_expiry, "type": "refresh"}
    return jwt.encode(
            payload=payload, key=secret_key, algorithm=algorithm
        )

# Decode token
def decode_token(token:str) -> dict | None:
    try:
        payload = jwt.decode(
                    token, key=secret_key, algorithms=[algorithm]
                )
        return payload
    except jwt.PyJWTError:
        return None
