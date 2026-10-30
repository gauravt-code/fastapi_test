from fastapi import APIRouter, Depends, HTTPException, status, Body
from database import get_session
from sqlmodel import select, Session
from models import User, UserCreate, UserResponse
from security import generate_hashed_password, verify_password, create_access_token, create_refresh_token, decode_token
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated


router = APIRouter(prefix="/auth",tags=["Authentication"])


# Register user endpoint
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register( user_data:UserCreate, session: Session = Depends(get_session)):
    # Existing user check
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    new_user = User(
        username=user_data.username,
        hashed_password=generate_hashed_password(user_data.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

# User login endpoint
@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == form_data.username)).first()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # If user does not exist, then raising error
    if not existing_user:
        raise credentials_exception

    # If password does not match, then raising error
    if not verify_password(form_data.password, existing_user.hashed_password):
        raise credentials_exception

    data = {"sub":existing_user.username}
    acc_token = create_access_token(data)
    ref_token = create_refresh_token(data)

    return {
        "access_token": acc_token,
        "refresh_token": ref_token,
        "token_type": "bearer"
    }

# Get new access token using refresh token
@router.post("/login/refresh")
def refresh_token(refresh_token: Annotated[str, Body(embed=True)],
                  session: Session = Depends(get_session)):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )

    payload = decode_token(refresh_token)

    # If there is no payload, raise error
    if not payload:
        raise invalid_token_exception

    # If type of token is not refresh token then raise error
    if payload.get("type") != "refresh":
        raise invalid_token_exception

    email = payload.get("sub")
    if not email:
        raise invalid_token_exception

    user = session.exec(select(User).where(User.username == email)).first()
    if not user:
        raise invalid_token_exception

    new_access_token = create_access_token(data={"sub": user.username})
    return {"access_token": new_access_token, "token_type": "bearer"}
