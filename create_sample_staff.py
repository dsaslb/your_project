#!/usr/bin/env python3
"""
직원 예시 데이터 생성 스크립트
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import User

def create_sample_staff():
    """다양한 직원 예시를 생성합니다."""
    
    # 직원 예시 데이터
    sample_staff = [
        # 주방 부서
        {
            "username": "kitchen_kim",
            "name": "김주방",
            "email": "kitchen_kim@restaurant.com",
            "phone": "010-1111-1111",
            "position": "주방장",
            "department": "주방",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "kitchen_lee",
            "name": "이보조",
            "email": "kitchen_lee@restaurant.com",
            "phone": "010-1111-1112",
            "position": "주방보조",
            "department": "주방",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "kitchen_park",
            "name": "박요리",
            "email": "kitchen_park@restaurant.com",
            "phone": "010-1111-1113",
            "position": "요리사",
            "department": "주방",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "kitchen_choi",
            "name": "최조리",
            "email": "kitchen_choi@restaurant.com",
            "phone": "010-1111-1114",
            "position": "조리사",
            "department": "주방",
            "role": "employee",
            "status": "approved"
        },
        
        # 홀서비스 부서
        {
            "username": "service_jung",
            "name": "정서버",
            "email": "service_jung@restaurant.com",
            "phone": "010-2222-2221",
            "position": "서버",
            "department": "홀서비스",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "service_han",
            "name": "한홀보조",
            "email": "service_han@restaurant.com",
            "phone": "010-2222-2222",
            "position": "홀보조",
            "department": "홀서비스",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "service_yoon",
            "name": "윤서빙",
            "email": "service_yoon@restaurant.com",
            "phone": "010-2222-2223",
            "position": "서빙",
            "department": "홀서비스",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "service_lim",
            "name": "임홀매니저",
            "email": "service_lim@restaurant.com",
            "phone": "010-2222-2224",
            "position": "홀매니저",
            "department": "홀서비스",
            "role": "manager",
            "status": "approved"
        },
        
        # 매니지먼트 부서
        {
            "username": "manager_kang",
            "name": "강매니저",
            "email": "manager_kang@restaurant.com",
            "phone": "010-3333-3331",
            "position": "매니저",
            "department": "매니지먼트",
            "role": "manager",
            "status": "approved"
        },
        {
            "username": "cashier_song",
            "name": "송캐셔",
            "email": "cashier_song@restaurant.com",
            "phone": "010-3333-3332",
            "position": "캐셔",
            "department": "매니지먼트",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "accountant_kim",
            "name": "김회계",
            "email": "accountant_kim@restaurant.com",
            "phone": "010-3333-3333",
            "position": "회계",
            "department": "매니지먼트",
            "role": "employee",
            "status": "approved"
        },
        
        # 배달 부서
        {
            "username": "delivery_wang",
            "name": "왕배달",
            "email": "delivery_wang@restaurant.com",
            "phone": "010-4444-4441",
            "position": "배달원",
            "department": "배달",
            "role": "employee",
            "status": "approved"
        },
        {
            "username": "delivery_zhang",
            "name": "장배달",
            "email": "delivery_zhang@restaurant.com",
            "phone": "010-4444-4442",
            "position": "배달원",
            "department": "배달",
            "role": "employee",
            "status": "approved"
        },
        
        # 청소 부서
        {
            "username": "cleaning_lee",
            "name": "이청소",
            "email": "cleaning_lee@restaurant.com",
            "phone": "010-5555-5551",
            "position": "청소원",
            "department": "청소",
            "role": "employee",
            "status": "approved"
        },
        
        # 대기 중인 직원들
        {
            "username": "waiting_kim",
            "name": "김대기",
            "email": "waiting_kim@restaurant.com",
            "phone": "010-6666-6661",
            "position": "서버",
            "department": "홀서비스",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "waiting_park",
            "name": "박대기",
            "email": "waiting_park@restaurant.com",
            "phone": "010-6666-6662",
            "position": "주방보조",
            "department": "주방",
            "role": "employee",
            "status": "pending"
        }
    ]
    
    with app.app_context():
        created_count = 0
        skipped_count = 0
        
        print("🚀 직원 예시 데이터 생성을 시작합니다...")
        print("=" * 60)
        
        for staff_data in sample_staff:
            # 기존 사용자 확인
            existing_user = User.query.filter_by(username=staff_data["username"]).first()
            
            if existing_user:
                print(f"⚠️  이미 존재: {staff_data['username']} ({staff_data['name']})")
                skipped_count += 1
                continue
            
            # 새 직원 생성
            new_staff = User(
                username=staff_data["username"],
                name=staff_data["name"],
                email=staff_data["email"],
                phone=staff_data["phone"],
                position=staff_data["position"],
                department=staff_data["department"],
                role=staff_data["role"],
                status=staff_data["status"]
            )
            
            # 기본 비밀번호 설정 (username + "123")
            new_staff.set_password(f"{staff_data['username']}123")
            
            try:
                db.session.add(new_staff)
                db.session.commit()
                
                print(f"✅ 생성됨: {staff_data['username']} ({staff_data['name']}) - {staff_data['department']} {staff_data['position']}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ 생성 실패: {staff_data['username']} - {str(e)}")
                db.session.rollback()
        
        print("=" * 60)
        print(f"📊 생성 결과:")
        print(f"   새로 생성: {created_count}명")
        print(f"   이미 존재: {skipped_count}명")
        print(f"   총 직원 수: {User.query.count()}명")
        
        print("\n🔐 로그인 정보 (새로 생성된 직원들):")
        print("   비밀번호 형식: {username}123")
        print("   예시: kitchen_kim123, service_jung123, manager_kang123")
        
        print("\n📋 부서별 직원 현황:")
        departments = db.session.query(User.department, db.func.count(User.id)).group_by(User.department).all()
        for dept, count in departments:
            if dept:
                print(f"   {dept}: {count}명")
        
        print("\n🎯 상태별 직원 현황:")
        statuses = db.session.query(User.status, db.func.count(User.id)).group_by(User.status).all()
        for status, count in statuses:
            if status:
                print(f"   {status}: {count}명")

def main():
    """메인 실행 함수"""
    print("🍽️  레스토랑 직원 예시 데이터 생성기")
    print("=" * 60)
    
    try:
        create_sample_staff()
        print("\n🎉 직원 예시 데이터 생성이 완료되었습니다!")
        print("이제 직원 관리 페이지와 스케줄 페이지에서 다양한 직원들을 확인할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")

if __name__ == "__main__":
    main() 