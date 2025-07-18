#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 데이터베이스 초기화 스크립트
"""

import sqlite3
import os

def create_simple_db():
    """간단한 DB 테이블 생성"""
    
    # DB 파일 경로
    db_path = 'instance/your_program.db'
    
    # 기존 파일 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"기존 DB 파일 삭제: {db_path}")
    
    # DB 연결 및 테이블 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 기본 테이블들 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                industry_id INTEGER,
                logo_url TEXT,
                website_url TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                address TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (industry_id) REFERENCES industry (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                brand_id INTEGER,
                address TEXT,
                phone TEXT,
                manager_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_id) REFERENCES brand (id),
                FOREIGN KEY (manager_id) REFERENCES user (id)
            )
        ''')
        
        # 기본 데이터 삽입
        cursor.execute('''
            INSERT OR IGNORE INTO user (username, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', 'admin123', 'admin', 1))
        
        cursor.execute('''
            INSERT OR IGNORE INTO industry (name, code, description, icon, color)
            VALUES (?, ?, ?, ?, ?)
        ''', ('음식점', 'RESTAURANT', '음식점 업종', '🍽️', '#FF6B6B'))
        
        # 커밋
        conn.commit()
        
        print("=== 간단한 DB 초기화 완료 ===")
        print("생성된 테이블:")
        print("- user (사용자)")
        print("- industry (업종)")
        print("- brand (브랜드)")
        print("- branch (매장)")
        print("\n기본 데이터:")
        print("- 관리자 계정: admin / admin123")
        print("- 업종: 음식점")
        
    except Exception as e:
        print(f"DB 초기화 실패: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_simple_db() 