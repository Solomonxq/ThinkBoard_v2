from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.uuid import generate_uuid
from app.utils.time import utcnow
from sqlalchemy import UniqueConstraint


class Idea(Base):
    __tablename__ = "ideas"


    id = Column(String(36), primary_key=True, default=generate_uuid)

    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utcnow)

    board_id = Column(
        String(36),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    board = relationship(
        "Board",
        back_populates="ideas"
    )

    user = relationship(
        "User",
        back_populates="ideas"
    )

    __table_args__ = (
        UniqueConstraint("board_id", "title", name="uq_board_idea_title"),
    )