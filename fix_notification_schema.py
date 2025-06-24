#!/usr/bin/env python3
"""
Notification 테이블에 is_admin_only 컬럼 추가
"""

import sqlite3
import os

def fix_notification_schema():
    """Notification 테이블에 is_admin_only 컬럼 추가"""
    
    # 데이터베이스 파일 경로
    db_path = "instance/restaurant_dev.sqlite3"
    
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return False
    
    try:
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 현재 테이블 구조 확인
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 현재 notifications 테이블 컬럼: {columns}")
        
        # is_admin_only 컬럼이 없으면 추가
        if 'is_admin_only' not in columns:
            print("🔧 is_admin_only 컬럼을 추가합니다...")
            cursor.execute("ALTER TABLE notifications ADD COLUMN is_admin_only BOOLEAN DEFAULT 0")
            conn.commit()
            print("✅ is_admin_only 컬럼이 성공적으로 추가되었습니다.")
        else:
            print("✅ is_admin_only 컬럼이 이미 존재합니다.")
        
        # 업데이트된 테이블 구조 확인
        cursor.execute("PRAGMA table_info(notifications)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 업데이트된 notifications 테이블 컬럼: {updated_columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Notification 테이블 스키마 수정을 시작합니다...")
    success = fix_notification_schema()
    
    if success:
        print("\n✅ 스키마 수정이 완료되었습니다!")
        print("이제 시스템 알림 발송 테스트를 다시 실행할 수 있습니다.")
    else:
        print("\n❌ 스키마 수정에 실패했습니다.") 