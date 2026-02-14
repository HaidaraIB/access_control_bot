from telegram import Update
from telegram.ext.filters import UpdateFilter
from Config import Config
import models


class PermissionFilter(UpdateFilter):
    """فلتر للتحقق من صلاحية معينة للأدمن"""
    
    def __init__(self, permission: models.Permission):
        self.permission = permission
    
    def filter(self, update: Update):
        user_id = update.effective_user.id if update.effective_user else None
        if not user_id:
            return False
        
        # المالك لديه جميع الصلاحيات
        if user_id == Config.OWNER_ID:
            return True
        
        with models.session_scope() as s:
            user = s.get(models.User, user_id)
            if not user or not user.is_admin:
                return False
            
            # التحقق من وجود الصلاحية
            permission = s.query(models.AdminPermission).filter(
                models.AdminPermission.admin_id == user_id,
                models.AdminPermission.permission == self.permission
            ).first()
            
            return permission is not None


class HasPermission:
    """دالة مساعدة للتحقق من الصلاحية في الكود"""
    
    @staticmethod
    def check(user_id: int, permission: models.Permission) -> bool:
        """التحقق من صلاحية معينة لمستخدم"""
        # المالك لديه جميع الصلاحيات
        if user_id == Config.OWNER_ID:
            return True
        
        with models.session_scope() as s:
            user = s.get(models.User, user_id)
            if not user or not user.is_admin:
                return False
            
            permission_obj = s.query(models.AdminPermission).filter(
                models.AdminPermission.admin_id == user_id,
                models.AdminPermission.permission == permission
            ).first()
            
            return permission_obj is not None

