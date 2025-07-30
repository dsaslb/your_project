# -*- coding: utf-8 -*-
"""
AI 모델 훈련을 위한 테스트 성능 데이터 생성
실제 성능 데이터가 충분하지 않을 때 사용
"""

import sqlite3
import random
import time
from datetime import datetime, timedelta
import os

def generate_test_performance_data():
    """테스트 성능 데이터 생성"""
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect('data/performance_metrics.db')
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_available_gb REAL,
                disk_percent REAL,
                disk_free_gb REAL,
                network_bytes_sent INTEGER,
                network_bytes_recv INTEGER,
                process_count INTEGER,
                response_time REAL,
                status TEXT
            )
        ''')
        
        # 기존 데이터 확인
        cursor.execute('SELECT COUNT(*) FROM performance_metrics')
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 100:
            print(f"이미 충분한 데이터가 있습니다: {existing_count}개")
            conn.close()
            return
            
        # 테스트 데이터 생성 (7일간, 30분 간격)
        print("테스트 성능 데이터 생성 중...")
        
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()
        
        current_time = start_time
        data_count = 0
        
        while current_time <= end_time:
            # 시간대별 패턴 생성
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # 기본값 설정
            base_cpu = 20
            base_memory = 50
            base_response = 1.5
            
            # 시간대별 변동
            if 9 <= hour <= 18:  # 업무시간
                base_cpu += 30
                base_memory += 20
                base_response += 0.5
            elif 19 <= hour <= 23:  # 저녁시간
                base_cpu += 15
                base_memory += 10
                base_response += 0.3
            elif 0 <= hour <= 6:  # 새벽시간
                base_cpu -= 10
                base_memory -= 5
                base_response -= 0.2
                
            # 요일별 변동
            if day_of_week >= 5:  # 주말
                base_cpu -= 20
                base_memory -= 15
                base_response -= 0.3
                
            # 랜덤 변동 추가
            cpu_percent = max(5, min(95, base_cpu + random.uniform(-10, 10)))
            memory_percent = max(20, min(90, base_memory + random.uniform(-15, 15)))
            response_time = max(0.5, min(5.0, base_response + random.uniform(-0.5, 0.5)))
            
            # 가끔 성능 이슈 시뮬레이션
            if random.random() < 0.05:  # 5% 확률로 성능 이슈
                cpu_percent = min(95, cpu_percent + 30)
                memory_percent = min(90, memory_percent + 25)
                response_time = min(5.0, response_time + 2.0)
                
            # 데이터 삽입
            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, cpu_percent, memory_percent, memory_available_gb,
                    disk_percent, disk_free_gb, network_bytes_sent, network_bytes_recv,
                    process_count, response_time, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_time.isoformat(),
                round(cpu_percent, 2),
                round(memory_percent, 2),
                round(random.uniform(2.0, 8.0), 2),
                round(random.uniform(40, 70), 2),
                round(random.uniform(50, 200), 2),
                random.randint(1000000, 10000000),
                random.randint(2000000, 15000000),
                random.randint(80, 150),
                round(response_time, 3),
                'healthy' if response_time < 3 else 'warning'
            ))
            
            data_count += 1
            current_time += timedelta(minutes=30)
            
        conn.commit()
        conn.close()
        
        print(f"테스트 데이터 생성 완료: {data_count}개 데이터 추가")
        
    except Exception as e:
        print(f"테스트 데이터 생성 오류: {e}")

if __name__ == "__main__":
    generate_test_performance_data() 