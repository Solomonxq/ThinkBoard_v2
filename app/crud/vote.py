from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vote import Vote


async def get_vote(db: AsyncSession, user_id: str, idea_id: str):
    stmt = select(Vote).where(
        Vote.user_id == user_id,
        Vote.idea_id == idea_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_vote(db: AsyncSession, user_id: str, idea_id: str, status: bool):
    vote = Vote(
        user_id=user_id,
        idea_id=idea_id,
        status=status
    )

    db.add(vote)
    await db.commit()
    await db.refresh(vote)
    return vote


async def update_vote(db: AsyncSession, user_id: str, idea_id: str, status: bool):
    vote = await get_vote(db, user_id, idea_id)

    if not vote:
        return None

    vote.status = status
    await db.commit()
    await db.refres