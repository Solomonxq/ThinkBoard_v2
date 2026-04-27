from app.schemas.idea import IdeaCreate
from app.models.idea import Idea
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession



async def create_idea(db: AsyncSession, data: IdeaCreate,user_id: str, board_id: str) -> Idea   :
    idea = Idea(
        title=data.title,
        description=data.description,
        user_id=user_id,
        board_id=board_id
    )

    db.add(idea)
    await db.commit()
    await db.refresh(idea)
    return idea

async def get_idea_by_title(db: AsyncSession, title: str, board_id: str) -> Idea | None:
    result = await db.execute(select(Idea).where(and_(Idea.board_id == board_id, Idea.title == title)))
    return result.scalars().first()



async def owner_of_idea(db:AsyncSession,user_id:str,idea_id:str) -> bool:
    result = await db.execute(
        select(Idea)
        .where(and_(Idea.id == idea_id, Idea.user_id == user_id))
    )
    return result.scalars().first() is not None

async def delete_idea(db: AsyncSession, idea_id: str) -> None:
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalars().first()
    if idea:
        await db.delete(idea)
        await db.commit()

async def get_idea_by_id(db: AsyncSession, idea_id: str) -> Idea | None:
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    return result.scalars().first()

async def check_idea_in_board(db: AsyncSession, idea_id: str, board_id: str) -> bool:
    result = await db.execute(
        select(Idea).where(and_(Idea.id == idea_id, Idea.board_id == board_id))
    )
    return result.scalars().first() is not None