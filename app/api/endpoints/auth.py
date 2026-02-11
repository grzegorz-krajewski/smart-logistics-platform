from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.deps import get_current_user
from app.models.user import User

from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.auth import create_access_token, get_password_hash, verify_password, pwd_context
from app.services.users import get_user_by_username, create_user

router = APIRouter()

# @router.post("/register", status_code=201)
# async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
#     existing = await get_user_by_username(db, payload.username)
#     if existing:
#         raise HTTPException(status_code=409, detail="Username already exists")

#     user = await create_user(db, payload.username, get_password_hash(payload.password))
#     return {"id": user.id, "username": user.username}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niepoprawny login lub hasło",
        )

    if pwd_context.needs_update(user.hashed_password):
        user.hashed_password = get_password_hash(form_data.password)
        await db.commit()

    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token, token_type="bearer")

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}