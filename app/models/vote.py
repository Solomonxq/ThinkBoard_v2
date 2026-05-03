from app.db.base import Base
from app.utils.time import utcnow
from app.utils.uuid import generate_uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    idea_id = Column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(Boolean, nullable=False)
    vote_at = Column(DateTime(timezone=True), default=utcnow)

    idea = relationship(
        "Idea",
        back_populates="votes",
        lazy="selectin",
    )
    user = relationship(
        "User",
        back_populates="votes",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "idea_id", name="uq_user_idea_vote"),
    )