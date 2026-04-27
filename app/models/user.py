from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.associations import board_members, user_favorite_boards
from app.utils.uuid import generate_uuid
from app.utils.time import utcnow


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(25), nullable=False, unique=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)

    refresh_token = Column(String, nullable=True)

    bio = Column(String(500), nullable=True)
    avatar_url = Column(String, nullable=True)

    boards = relationship(
        "Board",
        back_populates="owner",
        foreign_keys="Board.owner_id",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    member_of = relationship(
        "Board",
        secondary=board_members,
        back_populates="members"
    )

    favorite_boards = relationship(
        "Board",
        secondary=user_favorite_boards,
        back_populates="favorite_by"
    )

    ideas = relationship(
        "Idea",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    votes = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def all_boards(self):
        return list(set(self.boards + self.member_of))