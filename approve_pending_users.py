#!/usr/bin/env python3
"""
미승인 직원 승인 처리 스크립트
"""

from app import app, db
from models import User

def approve_pending_users():
    """미승인 직원들을 승인 처리"""
    with app.app_context():
        # 미승인 직원 조회
        pending_users = User.query.filter_by(status="pending").all()
        
        if not pending_users:
            print("승인할 직원이 없습니다.")
            return
        
        print(f"승인할 직원 수: {len(pending_users)}")
        
        # 승인 처리
        for user in pending_users:
            user.status = "approved"
            print(f"승인 완료: {user.name} ({user.position} - {user.department})")
        
        # 변경사항 저장
        db.session.commit()
        
        print(f"\n총 {len(pending_users)}명의 직원이 승인되었습니다.")
        
        # 승인 후 상태 확인
        approved_count = User.query.filter_by(status="approved").count()
        pending_count = User.query.filter_by(status="pending").count()
        
        print(f"승인된 직원: {approved_count}명")
        print(f"미승인 직원: {pending_count}명")

if __name__ == '__main__':
    approve_pending_users() 