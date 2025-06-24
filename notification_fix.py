#!/usr/bin/env python3
"""
app.py에서 사용할 알림 함수들
"""

from models import Notification
from extensions import db

def send_notification_enhanced(user_id, content, category='공지', link=None, is_admin_only=False):
    """향상된 알림 발송 함수"""
    try:
        n = Notification(
            user_id=user_id,
            content=content,
            category=category,
            link=link,
            is_admin_only=is_admin_only
        )
        db.session.add(n)
        db.session.commit()
        return True
    except Exception as e:
        print(f"알림 발송 실패: {e}")
        return False

def send_admin_only_notification(content, category='공지', link=None):
    """관리자 전용 알림 발송"""
    try:
        from models import User
        
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            send_notification_enhanced(
                admin.id, 
                content, 
                category, 
                link, 
                is_admin_only=True
            )
        return True
    except Exception as e:
        print(f"관리자 알림 발송 실패: {e}")
        return False

def send_notification_to_role(role, content, category='공지', link=None, is_admin_only=False):
    """특정 역할 사용자들에게 알림 발송"""
    try:
        from models import User
        
        users = User.query.filter_by(role=role).all()
        for user in users:
            send_notification_enhanced(
                user.id, 
                content, 
                category, 
                link, 
                is_admin_only
            )
        return True
    except Exception as e:
        print(f"역할별 알림 발송 실패: {e}")
        return False 