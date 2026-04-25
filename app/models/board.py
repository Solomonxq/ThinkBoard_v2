from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.associations import board_members, user_favorite_boards
from app.utils.uuid import generate_uuid
from app.utils.time import utcnow


class Board(Base):
    __tablename__ = "boards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    board_name = Column(String(25), nullable=False, index=True)

    owner_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), default=utcnow)
    access = Column(Boolean, default=False)
    description = Column(String(500), nullable=False)

    owner = relationship(
        "User",
        back_populates="boards",
        foreign_keys=[owner_id]
    )

    members = relationship(
        "User",
        secondary=board_members,
        back_populates="member_of"
    )

    favorite_by = relationship(
        "User",
        secondary=user_favorite_boards,
        back_populates="favorite_boards"
    )

    ideas = relationship(
        "Idea",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
