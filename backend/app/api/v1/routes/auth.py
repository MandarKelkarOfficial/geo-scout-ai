from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.db import crud
from app.db.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.security import create_access_token
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = await crud.create_user(db, user_in)
    # Auto-login: set the auth cookie immediately after registration
    token = create_access_token(user.id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   # Set to True in production with HTTPS
        max_age=60 * 60 * 24 * 7  # 7 days
    )
    return UserRead.model_validate(user)

@router.post("/login")
async def login(login_data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await crud.verify_user_password(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   # Set to True in production with HTTPS
        max_age=60 * 60 * 24 * 7  # 7 days
    )
    return {"message": "Logged in successfully", "user": UserRead.model_validate(user)}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserRead)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated = await crud.update_user(db, current_user.id, update_data.full_name)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated
