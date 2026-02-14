from enum import Enum
import sqlalchemy as sa
from models.DB import Base
from datetime import datetime


class Permission(Enum):
    BAN_USERS = "ban_users"
    BROADCAST = "broadcast"
    MANAGE_FORCE_JOIN = "manage_force_join"
    VIEW_IDS = "view_ids"
    MANAGE_USERS = "manage_users"


class AdminPermission(Base):
    __tablename__ = "admin_permissions"
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    admin_id = sa.Column(sa.BigInteger, sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    permission = sa.Column(sa.Enum(Permission), nullable=False)
    
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        sa.UniqueConstraint('admin_id', 'permission', name='unique_admin_permission'),
    )
    
    def __repr__(self):
        return f"AdminPermission(admin_id={self.admin_id}, permission={self.permission.value})"

