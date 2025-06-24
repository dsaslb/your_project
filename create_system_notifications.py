#!/usr/bin/env python3
"""
시스템 알림 발송 테스트 스크립트
- 관리자 전용 시스템 알림
- 발주 승인 알림
- 권한별 알림 발송
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Notification, Order
from utils.notify import (
    send_notification_enhanced, 
    send_admin_only_notification,
    send_notification_to_role
)
from datetime import datetime

def create_system_notifications():
    """시스템 알림 발송 테스트"""
    
    with app.app_context():
        print("🔔 시스템 알림 발송 테스트를 시작합니다...")
        
        # 사용자 조회
        users = User.query.filter_by(role='employee').all()
        admins = User.query.filter_by(role='admin').all()
        
        if not users:
            print("❌ 직원 사용자가 없습니다.")
            return
        
        if not admins:
            print("❌ 관리자 사용자가 없습니다.")
            return
        
        print(f"📊 총 {len(users)}명의 직원, {len(admins)}명의 관리자")
        
        # 1. 관리자 전용 시스템 알림 발송
        print("\n1️⃣ 관리자 전용 시스템 알림 발송...")
        
        system_notifications = [
            {
                "content": "시스템 점검이 예정되어 있습니다. (2024년 1월 15일 02:00-04:00)",
                "category": "공지",
                "link": "/admin/system_maintenance"
            },
            {
                "content": "데이터베이스 백업이 완료되었습니다.",
                "category": "공지",
                "link": "/admin/backup/db"
            },
            {
                "content": "새로운 보안 업데이트가 적용되었습니다.",
                "category": "공지",
                "link": "/admin/security_update"
            },
            {
                "content": "월말 급여 정산이 시작되었습니다.",
                "category": "공지",
                "link": "/admin/payroll/bulk"
            }
        ]
        
        for noti in system_notifications:
            send_admin_only_notification(
                noti["content"],
                noti["category"],
                noti["link"]
            )
            print(f"   ✅ {noti['content'][:30]}...")
        
        # 2. 발주 승인 알림 테스트
        print("\n2️⃣ 발주 승인 알림 테스트...")
        
        # 테스트 발주 데이터 생성
        test_orders = [
            {"item": "커피원두", "quantity": 10, "ordered_by": users[0].id if users else None},
            {"item": "청소용품", "quantity": 5, "ordered_by": users[1].id if len(users) > 1 else None},
            {"item": "식재료", "quantity": 20, "ordered_by": users[2].id if len(users) > 2 else None}
        ]
        
        for i, order_data in enumerate(test_orders):
            if order_data["ordered_by"]:
                # 발주자에게 승인 알림
                send_notification_enhanced(
                    order_data["ordered_by"],
                    f"발주 '{order_data['item']}' ({order_data['quantity']}개)가 승인되었습니다.",
                    "발주",
                    f"/order_detail/{i+1}"
                )
                
                # 매니저들에게도 알림
                managers = User.query.filter(User.role.in_(['admin', 'manager'])).all()
                for manager in managers:
                    if manager.id != order_data["ordered_by"]:
                        send_notification_enhanced(
                            manager.id,
                            f"발주 '{order_data['item']}' ({order_data['quantity']}개)가 승인 처리되었습니다.",
                            "발주",
                            f"/order_detail/{i+1}"
                        )
                
                print(f"   ✅ 발주 '{order_data['item']}' 승인 알림 발송")
        
        # 3. 역할별 알림 발송
        print("\n3️⃣ 역할별 알림 발송...")
        
        role_notifications = [
            {
                "role": "manager",
                "content": "매니저 회의가 예정되어 있습니다. (내일 오후 2시)",
                "category": "공지",
                "link": "/admin/meeting"
            },
            {
                "role": "employee",
                "content": "월말 근무 시간 확인 부탁드립니다.",
                "category": "근무",
                "link": "/attendance"
            }
        ]
        
        for noti in role_notifications:
            send_notification_to_role(
                noti["role"],
                noti["content"],
                noti["category"],
                noti["link"]
            )
            print(f"   ✅ {noti['role']} 역할 알림 발송")
        
        # 4. 일반 알림 발송
        print("\n4️⃣ 일반 알림 발송...")
        
        general_notifications = [
            "오늘 점심 메뉴가 업데이트되었습니다.",
            "새로운 공지사항이 등록되었습니다.",
            "청소 일정이 변경되었습니다."
        ]
        
        for content in general_notifications:
            for user in users[:3]:  # 처음 3명에게만
                send_notification_enhanced(
                    user.id,
                    content,
                    "공지"
                )
            print(f"   ✅ {content[:20]}...")
        
        # 통계 출력
        total_notifications = Notification.query.count()
        admin_only_notifications = Notification.query.filter_by(is_admin_only=True).count()
        order_notifications = Notification.query.filter_by(category='발주').count()
        unread_notifications = Notification.query.filter_by(is_read=False).count()
        
        print(f"\n✅ 시스템 알림 발송 완료!")
        print(f"📊 통계:")
        print(f"   - 총 알림: {total_notifications}개")
        print(f"   - 관리자 전용: {admin_only_notifications}개")
        print(f"   - 발주 관련: {order_notifications}개")
        print(f"   - 안읽음: {unread_notifications}개")
        
        print(f"\n🔗 테스트 링크:")
        print(f"   - 발주 승인 알림: http://localhost:5000/notifications/orders/approved")
        print(f"   - 관리자 시스템 알림: http://localhost:5000/admin/system_notifications")
        print(f"   - 전체 알림센터: http://localhost:5000/notifications")
        print(f"   - 고급 검색: http://localhost:5000/notifications/advanced_search")
        
        print(f"\n🎯 테스트 시나리오:")
        print(f"   1. 발주 승인 알림만 조회: /notifications/orders/approved")
        print(f"   2. 관리자 전용 알림: /admin/system_notifications")
        print(f"   3. 발주 승인 필터: /notifications/filtered?category=발주&keyword=승인")
        print(f"   4. 안읽음 필터: /notifications/filtered?is_read=false")

if __name__ == "__main__":
    create_system_notifications() 