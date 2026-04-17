from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead, summary="Get current user profile")
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.put("/me", response_model=UserRead, summary="Update current user profile")
async def update_current_user(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if user_in.email is not None:
        result = await db.execute(select(User).where(User.email == user_in.email, User.id != current_user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        current_user.email = user_in.email

    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name

    if user_in.membership_tier is not None:
        current_user.membership_tier = user_in.membership_tier

    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)

    await db.flush()
    await db.refresh(current_user)
    return current_user


# ---------------------------------------------------------------------------
# Admin-only endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[UserRead],
    summary="List all users (admin only)",
    dependencies=[Depends(get_current_superuser)],
)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a specific user by ID (admin only)",
    dependencies=[Depends(get_current_superuser)],
)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user (admin only)",
    dependencies=[Depends(get_current_superuser)],
)
async def admin_update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field == "password" and value is not None:
            user.hashed_password = get_password_hash(value)
        elif field != "password":
            setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (admin only)",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
