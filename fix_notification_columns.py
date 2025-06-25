#!/usr/bin/env python3
"""
notifications 테이블에 누락된 컬럼들을 추가하는 스크립트
"""

import sqlite3
import os

def add_missing_columns():
    """notifications 테이블에 누락된 컬럼들을 추가"""
    
    # 데이터베이스 파일 경로
    db_path = 'instance/restaurant_dev.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return False
    
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 notifications 테이블 컬럼 확인 중...")
        
        # 현재 컬럼 확인
        cursor.execute("PRAGMA table_info(notifications)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"현재 컬럼: {existing_columns}")
        
        # 추가할 컬럼들
        columns_to_add = [
            ('recipient_role', 'TEXT'),
            ('recipient_team', 'TEXT'),
            ('priority', 'INTEGER DEFAULT 0'),
            ('ai_priority', 'INTEGER DEFAULT 0')
        ]
        
        added_columns = []
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE notifications ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    added_columns.append(column_name)
                    print(f"✅ {column_name} 컬럼 추가 완료")
                except Exception as e:
                    print(f"❌ {column_name} 컬럼 추가 실패: {e}")
            else:
                print(f"ℹ️ {column_name} 컬럼이 이미 존재합니다")
        
        # 변경사항 저장
        conn.commit()
        conn.close()
        
        if added_columns:
            print(f"\n🎉 성공적으로 추가된 컬럼: {added_columns}")
            return True
        else:
            print("\nℹ️ 추가할 컬럼이 없습니다")
            return True
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("🚀 notifications 테이블 컬럼 수정 시작...")
    success = add_missing_columns()
    
    if success:
        print("\n✅ 컬럼 수정이 완료되었습니다!")
        print("이제 서버를 다시 실행하세요.")
    else:
        print("\n❌ 컬럼 수정에 실패했습니다.") 