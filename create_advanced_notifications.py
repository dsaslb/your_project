#!/usr/bin/env python3
"""
고급 알림 기능 테스트 스크립트
- 특정 카테고리/키워드 필터링
- 권한별 알림 발송
- 관리자 전용 알림
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Notification
from utils.notify import (
    send_notification_enhanced, 
    send_admin_only_notification,
    send_notification_to_role,
    send_notification_with_keyword_filter
)
from datetime import datetime

def create_advanced_notifications():
    """고급 알림 기능 테스트용 알림 생성"""
    
    with app.app_context():
        print("🔔 고급 알림 기능 테스트를 위한 알림을 생성합니다...")
        
        # 사용자 조회
        users = User.query.filter_by(role='employee').all()
        admins = User.query.filter_by(role='admin').all()
        
        if not users:
            print("❌ 직원 사용자가 없습니다.")
            return
        
        if not admins:
            print("❌ 관리자 사용자가 없습니다.")
            return
        
        print(f"📊 총 {len(users)}명의 직원, {len(admins)}명의 관리자에게 알림을 생성합니다.")
        
        # 1. 발주 승인 관련 알림 (키워드 필터링 테스트용)
        print("\n1️⃣ 발주 승인 관련 알림 생성...")
        for i, user in enumerate(users[:3]):
            send_notification_enhanced(
                user.id,
                f"발주 '{['커피원두', '청소용품', '식재료'][i]}' (10개)가 승인되었습니다.",
                "발주",
                f"/order_detail/{i+1}"
            )
        
        # 2. 청소 관련 알림 (카테고리 필터링 테스트용)
        print("2️⃣ 청소 관련 알림 생성...")
        for i, user in enumerate(users[3:6]):
            send_notification_enhanced(
                user.id,
                f"{['주방', '홀', '창고'][i]} 청소가 완료되었습니다.",
                "청소",
                "/clean"
            )
        
        # 3. 교대 신청 알림 (상태 필터링 테스트용)
        print("3️⃣ 교대 신청 알림 생성...")
        for i, user in enumerate(users[6:9]):
            send_notification_enhanced(
                user.id,
                f"{datetime.now().strftime('%m월 %d일')} 교대 신청이 대기 중입니다.",
                "교대",
                "/swap_manage"
            )
        
        # 4. 관리자 전용 시스템 알림
        print("4️⃣ 관리자 전용 시스템 알림 생성...")
        send_admin_only_notification(
            "시스템 점검이 예정되어 있습니다. (2024년 1월 15일 02:00-04:00)",
            "공지",
            "/admin/system_maintenance"
        )
        
        send_admin_only_notification(
            "데이터베이스 백업이 완료되었습니다.",
            "공지",
            "/admin/backup/db"
        )
        
        # 5. 역할별 알림 발송
        print("5️⃣ 역할별 알림 발송...")
        send_notification_to_role(
            "manager",
            "매니저 회의가 예정되어 있습니다. (내일 오후 2시)",
            "공지",
            "/admin/meeting"
        )
        
        # 6. 키워드 필터링 테스트용 추가 알림
        print("6️⃣ 키워드 필터링 테스트용 알림 생성...")
        for user in users[:2]:
            send_notification_enhanced(
                user.id,
                "승인 처리가 지연되고 있습니다. 확인 부탁드립니다.",
                "공지",
                "/admin/pending"
            )
        
        # 7. 다양한 카테고리 알림
        print("7️⃣ 다양한 카테고리 알림 생성...")
        categories = ["근무", "공지", "일반"]
        for i, user in enumerate(users[9:12]):
            category = categories[i % len(categories)]
            send_notification_enhanced(
                user.id,
                f"{category} 관련 중요 알림입니다.",
                category,
                f"/{category.lower()}"
            )
        
        # 통계 출력
        total_notifications = Notification.query.count()
        unread_notifications = Notification.query.filter_by(is_read=False).count()
        admin_only_notifications = Notification.query.filter_by(is_admin_only=True).count()
        
        print(f"\n✅ 알림 생성 완료!")
        print(f"📊 통계:")
        print(f"   - 총 알림: {total_notifications}개")
        print(f"   - 안읽음: {unread_notifications}개")
        print(f"   - 관리자 전용: {admin_only_notifications}개")
        
        print(f"\n🔗 테스트 링크:")
        print(f"   - 일반 알림센터: http://localhost:5000/notifications")
        print(f"   - 고급 검색: http://localhost:5000/notifications/advanced_search")
        print(f"   - 발주 승인 필터: http://localhost:5000/notifications/filtered?category=발주&keyword=승인")
        print(f"   - 안읽음 필터: http://localhost:5000/notifications/filtered?is_read=false")
        print(f"   - 관리자 전용: http://localhost:5000/notifications/filtered?is_admin_only=true")
        
        print(f"\n🎯 테스트 시나리오:")
        print(f"   1. 발주 승인 알림만 필터링: 카테고리='발주', 키워드='승인'")
        print(f"   2. 안읽음 알림만 조회: 읽음상태='안읽음'")
        print(f"   3. 관리자 전용 알림: 알림유형='관리자 전용'")
        print(f"   4. 키워드 검색: '승인', '청소', '교대' 등")

if __name__ == "__main__":
    create_advanced_notifications() 