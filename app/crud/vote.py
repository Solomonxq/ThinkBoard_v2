from app.models.vote import Vote
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_vote(db: AsyncSession, user_id: str, idea_id: str) -> Vote | None:
    result = await db.execute(
        select(Vote).where(Vote.user_id == user_id, Vote.idea_id == idea_id)
    )
    return result.scalar_one_or_none()


async def create_vote(db: AsyncSession, user_id: str, idea_id: str, status: bool) -> Vote:
    vote = Vote(user_id=user_id, idea_id=idea_id, status=status)
    db.add(vote)
    await db.commit()
    await db.refresh(vote)
    return vote


async def update_vote(db: AsyncSession, user_id: str, idea_id: str, status: bool) -> Vote | None:
    vote = await get_vote(db, user_id, idea_id)
    if not vote:
        return None
    vote.status = status
    await db.commit()
    await db.refresh(vote)
    return vote


async def get_vote_counts(db: AsyncSession, idea_id: str) -> dict:
    result = await db.execute(
        select(Vote.status, func.count(Vote.id))
        .where(Vote.idea_id == idea_id)
        .group_by(Vote.status)
    )
    counts = {True: 0, False: 0}
    for status, count in result.all():
        counts[status] = count
    return {"approve": counts[True], "reject": counts[False]}
