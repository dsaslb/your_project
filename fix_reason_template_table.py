#!/usr/bin/env python3
"""
사유 템플릿 테이블 구조 수정 스크립트
"""

from app import app, db
from models import ReasonTemplate
import sqlite3

def fix_reason_template_table():
    """사유 템플릿 테이블 구조 수정"""
    print("=== 사유 템플릿 테이블 구조 수정 시작 ===")
    
    with app.app_context():
        # 1. 기존 테이블 삭제
        print("\n1. 기존 reason_templates 테이블 삭제:")
        try:
            db.session.execute("DROP TABLE IF EXISTS reason_templates")
            db.session.commit()
            print("  - 기존 테이블 삭제 완료")
        except Exception as e:
            print(f"  - 테이블 삭제 오류: {e}")
        
        # 2. 새 테이블 생성
        print("\n2. 새 reason_templates 테이블 생성:")
        try:
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
            db.session.execute(create_table_sql)
            db.session.commit()
            print("  - 새 테이블 생성 완료")
        except Exception as e:
            print(f"  - 테이블 생성 오류: {e}")
        
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
        
        for text, team in sample_templates:
            try:
                template = ReasonTemplate(
                    text=text,
                    team=team,
                    created_by=1  # 관리자 ID
                )
                db.session.add(template)
                print(f"  - {text} (팀: {team or '전체'}) 추가됨")
            except Exception as e:
                print(f"  - {text} 추가 실패: {e}")
        
        db.session.commit()
        
        # 4. 테이블 구조 확인
        print("\n4. 테이블 구조 확인:")
        try:
            result = db.session.execute("PRAGMA table_info(reason_templates)")
            columns = result.fetchall()
            print(f"  컬럼 수: {len(columns)}")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
        except Exception as e:
            print(f"  테이블 구조 확인 오류: {e}")
        
        # 5. 데이터 확인
        print("\n5. 데이터 확인:")
        try:
            templates = ReasonTemplate.query.all()
            print(f"  총 템플릿 수: {len(templates)}")
            for t in templates:
                print(f"    - {t.text} (팀: {t.team or '전체'})")
        except Exception as e:
            print(f"  데이터 확인 오류: {e}")
        
        print("\n=== 사유 템플릿 테이블 구조 수정 완료 ===")

if __name__ == "__main__":
    fix_reason_template_table() 