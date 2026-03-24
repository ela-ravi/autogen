from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def create_user(
    db: AsyncSession, email: str, password: str, full_name: str
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        auth_provider="local",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_google_id(db: AsyncSession, google_id: str) -> User | None:
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def get_or_create_google_user(
    db: AsyncSession, google_id: str, email: str, full_name: str
) -> User:
    user = await get_by_google_id(db, google_id)
    if user:
        return user

    # Check if email exists (link accounts)
    user = await get_by_email(db, email)
    if user:
        user.google_id = google_id
        user.auth_provider = "google"
        await db.commit()
        await db.refresh(user)
        return user

    user = User(
        email=email,
        full_name=full_name,
        auth_provider="google",
        google_id=google_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
