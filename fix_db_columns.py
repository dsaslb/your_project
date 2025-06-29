#!/usr/bin/env python3
"""
데이터베이스 컬럼 추가 스크립트
"""

from app import app, db
from models import Notification


def add_notification_columns():
    """알림 테이블에 새로운 컬럼들 추가"""
    with app.app_context():
        try:
            # 새로운 컬럼들 추가
            db.engine.execute(
                "ALTER TABLE notifications ADD COLUMN recipient_role VARCHAR(20)"
            )
            print("recipient_role 컬럼 추가 완료")
        except Exception as e:
            print(f"recipient_role 컬럼 추가 실패 (이미 존재할 수 있음): {e}")

        try:
            db.engine.execute(
                "ALTER TABLE notifications ADD COLUMN recipient_team VARCHAR(20)"
            )
            print("recipient_team 컬럼 추가 완료")
        except Exception as e:
            print(f"recipient_team 컬럼 추가 실패 (이미 존재할 수 있음): {e}")

        try:
            db.engine.execute(
                'ALTER TABLE notifications ADD COLUMN priority VARCHAR(10) DEFAULT "일반"'
            )
            print("priority 컬럼 추가 완료")
        except Exception as e:
            print(f"priority 컬럼 추가 실패 (이미 존재할 수 있음): {e}")

        try:
            db.engine.execute(
                "ALTER TABLE notifications ADD COLUMN ai_priority VARCHAR(10)"
            )
            print("ai_priority 컬럼 추가 완료")
        except Exception as e:
            print(f"ai_priority 컬럼 추가 실패 (이미 존재할 수 있음): {e}")

        print("모든 컬럼 추가 작업 완료!")


if __name__ == "__main__":
    add_notification_columns()
