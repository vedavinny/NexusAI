"""Business logic for user signup and login."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.security import create_access_token, hash_password, verify_password
from backend.models.user import User
from backend.schemas.auth import UserCreate


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


async def register_user(db: AsyncSession, payload: UserCreate) -> User:
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none() is not None:
        raise EmailAlreadyRegisteredError("An account with this email already exists.")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> str:
    """Validate credentials and return a signed JWT access token."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Incorrect email or password.")

    return create_access_token(subject=str(user.id))
