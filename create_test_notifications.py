#!/usr/bin/env python3
"""
테스트용 알림 생성 스크립트
알림센터 고도화 기능을 테스트하기 위한 샘플 알림들을 생성합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import User, Notification
from utils.notify import send_notification_enhanced
from datetime import datetime, timedelta

def create_test_notifications():
    """테스트용 알림들을 생성합니다."""
    with app.app_context():
        # 사용자 목록 가져오기
        users = User.query.filter_by(status='approved').all()
        
        if not users:
            print("승인된 사용자가 없습니다. 먼저 사용자를 생성해주세요.")
            return
        
        print(f"총 {len(users)}명의 사용자에게 테스트 알림을 생성합니다...")
        
        # 테스트 알림 데이터
        test_notifications = [
            # 발주 관련 알림
            {
                'content': '발주 "식용유 5L" (10개)가 승인되었습니다.',
                'category': '발주',
                'link': '/order_detail/1'
            },
            {
                'content': '발주 "고기 1kg" (5개)가 거절되었습니다. 사유: 재고 부족',
                'category': '발주',
                'link': '/order_detail/2'
            },
            {
                'content': '발주 "쌀 20kg" (3개)가 배송되었습니다.',
                'category': '발주',
                'link': '/order_detail/3'
            },
            
            # 청소 관련 알림
            {
                'content': '2024년 1월 15일 청소 담당으로 배정되었습니다: 주방 청소',
                'category': '청소',
                'link': '/clean'
            },
            {
                'content': '2024년 1월 16일 청소 담당으로 배정되었습니다: 홀 청소',
                'category': '청소',
                'link': '/clean'
            },
            
            # 근무 관련 알림
            {
                'content': '2024년 1월 15일 근무 일정이 변경되었습니다: 09:00~18:00',
                'category': '근무',
                'link': '/schedule'
            },
            {
                'content': '2024년 1월 16일 출근 시간입니다. 출근 처리를 해주세요.',
                'category': '근무',
                'link': '/attendance'
            },
            
            # 교대 관련 알림
            {
                'content': '2024년 1월 15일 교대 신청이 승인되었습니다.',
                'category': '교대',
                'link': '/swap_manage'
            },
            {
                'content': '2024년 1월 16일 교대 신청이 거절되었습니다. 사유: 인력 부족',
                'category': '교대',
                'link': '/swap_manage'
            },
            
            # 공지 관련 알림
            {
                'content': '새 공지사항: 월급 지급일 안내',
                'category': '공지',
                'link': '/notice_view/1'
            },
            {
                'content': '새 공지사항: 연말연시 근무 일정',
                'category': '공지',
                'link': '/notice_view/2'
            },
            {
                'content': '새 공지사항: 안전 교육 실시',
                'category': '공지',
                'link': '/notice_view/3'
            }
        ]
        
        # 각 사용자에게 알림 생성
        success_count = 0
        for user in users:
            for i, notification_data in enumerate(test_notifications):
                try:
                    # 시간을 다르게 설정 (최근 7일 내)
                    days_ago = i % 7
                    created_at = datetime.utcnow() - timedelta(days=days_ago)
                    
                    # 알림 생성
                    notification = Notification(
                        user_id=user.id,
                        content=notification_data['content'],
                        category=notification_data['category'],
                        link=notification_data['link'],
                        created_at=created_at,
                        is_read=(i % 3 == 0)  # 일부는 읽음 처리
                    )
                    db.session.add(notification)
                    success_count += 1
                    
                except Exception as e:
                    print(f"알림 생성 실패: {e}")
        
        # 데이터베이스에 저장
        try:
            db.session.commit()
            print(f"✅ 총 {success_count}개의 테스트 알림이 생성되었습니다!")
            print("\n📊 생성된 알림 통계:")
            
            # 카테고리별 통계
            category_stats = db.session.query(
                Notification.category,
                db.func.count(Notification.id).label('total'),
                db.func.sum(db.case((Notification.is_read == False, 1), else_=0)).label('unread')
            ).group_by(Notification.category).all()
            
            for stat in category_stats:
                print(f"  - {stat.category}: {stat.total}개 (안읽음: {stat.unread}개)")
            
            print(f"\n🔗 알림센터 접속: http://localhost:5000/notifications")
            print(f"🔗 관리자 알림센터: http://localhost:5000/admin/notifications/center")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 알림 생성 중 오류 발생: {e}")

def clear_test_notifications():
    """테스트 알림들을 모두 삭제합니다."""
    with app.app_context():
        try:
            count = Notification.query.count()
            Notification.query.delete()
            db.session.commit()
            print(f"✅ {count}개의 알림이 삭제되었습니다.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 알림 삭제 중 오류 발생: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='테스트 알림 생성/삭제')
    parser.add_argument('--clear', action='store_true', help='기존 알림 모두 삭제')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_test_notifications()
    else:
        create_test_notifications() 