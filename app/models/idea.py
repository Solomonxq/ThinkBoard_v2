from app.db.base import Base
from app.utils.time import utcnow
from app.utils.uuid import generate_uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    board_id = Column(
        String(36),
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    voting_ends_at = Column(DateTime(timezone=True), nullable=True, index=True)
    accepted = Column(Boolean, default=False, nullable=False)

    board = relationship(
        "Board",
        back_populates="ideas",
        lazy="selectin",
    )
    user = relationship(
        "User",
        back_populates="ideas",
        lazy="selectin",
    )
    votes = relationship(
        "Vote",
        back_populates="idea",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("board_id", "title", name="uq_board_idea_title"),
    )