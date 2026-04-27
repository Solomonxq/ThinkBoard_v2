from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.utils.uuid import generate_uuid
from app.utils.time import utcnow


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    idea_id = Column(
        String(36),
        ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status = Column(Boolean, nullable=False)


    vote_at = Column(DateTime(timezone=True), default=utcnow)

    idea = relationship(
        "Idea",
        back_populates="votes"
    )

    user = relationship(
        "User",
        back_populates="votes"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "idea_id", name="uq_user_idea_vote"),
    )