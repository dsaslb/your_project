#!/usr/bin/env python3
"""
데이터베이스 직접 수정 스크립트
"""

import sqlite3
import os

def fix_database():
    """데이터베이스 직접 수정"""
    print("=== 데이터베이스 직접 수정 시작 ===")
    
    db_path = "instance/restaurant_dev.sqlite3"
    
    if not os.path.exists(db_path):
        print(f"데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return
    
    # SQLite 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 기존 테이블 삭제
        print("\n1. 기존 reason_templates 테이블 삭제:")
        cursor.execute("DROP TABLE IF EXISTS reason_templates")
        print("  - 기존 테이블 삭제 완료")
        
        # 2. 새 테이블 생성
        print("\n2. 새 reason_templates 테이블 생성:")
        create_table_sql = """
        CREATE TABLE reason_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text VARCHAR(100) NOT NULL UNIQUE,
            team VARCHAR(30),
            is_active BOOLEAN DEFAULT 1,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        """
        cursor.execute(create_table_sql)
        print("  - 새 테이블 생성 완료")
        
        # 3. 샘플 데이터 추가
        print("\n3. 샘플 데이터 추가:")
        sample_templates = [
            ("월요일 컨디션 저하", None),
            ("금요일 야근", None),
            ("수요일 중간점검", None),
            ("개인사정", None),
            ("교통사고", None),
            ("병원진료", None),
            ("조리 준비", "주방"),
            ("재료 정리", "주방"),
            ("고객 응대", "홀"),
            ("테이블 정리", "홀")
        ]
        
        insert_sql = """
        INSERT INTO reason_templates (text, team, is_active, created_by)
        VALUES (?, ?, 1, 1)
        """
        
        for text, team in sample_templates:
            cursor.execute(insert_sql, (text, team))
            print(f"  - {text} (팀: {team or '전체'}) 추가됨")
        
        # 4. 테이블 구조 확인
        print("\n4. 테이블 구조 확인:")
        cursor.execute("PRAGMA table_info(reason_templates)")
        columns = cursor.fetchall()
        print(f"  컬럼 수: {len(columns)}")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # 5. 데이터 확인
        print("\n5. 데이터 확인:")
        cursor.execute("SELECT text, team FROM reason_templates")
        templates = cursor.fetchall()
        print(f"  총 템플릿 수: {len(templates)}")
        for text, team in templates:
            print(f"    - {text} (팀: {team or '전체'})")
        
        # 변경사항 저장
        conn.commit()
        print("\n=== 데이터베이스 직접 수정 완료 ===")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database() 