import sqlalchemy as sa
from sqlalchemy.orm import relationship
from models.DB import Base
from datetime import datetime
from enum import Enum


class AccessRequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submitted_username = sa.Column(sa.String, nullable=True)
    submitted_password = sa.Column(sa.String, nullable=True)
    order_id = sa.Column(sa.String, nullable=True)
    status = sa.Column(
        sa.Enum(AccessRequestStatus),
        nullable=False,
        default=AccessRequestStatus.PENDING,
        index=True,
    )
    invite_link = sa.Column(sa.String, nullable=True)
    is_revoked = sa.Column(sa.Boolean, default=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="access_requests")
