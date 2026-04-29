from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_user_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.boards),
            selectinload(User.member_of)
        )
        .where(User.email == email.lower())
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        email=data.email.lower(),
        username=data.username,
        password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.boards),
            selectinload(User.member_of),
            selectinload(User.favorite_boards)
        )
        .where(User.id == user_id)
    )
    return result.scalars().first()


async def update_user_profile(db: AsyncSession, user: User, data: dict) -> User:
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user
