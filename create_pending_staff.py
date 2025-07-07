#!/usr/bin/env python3
"""
미승인 직원 예시 데이터 생성 스크립트
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import User

def create_pending_staff():
    """미승인 직원 예시를 생성합니다."""
    
    # 미승인 직원 예시 데이터
    pending_staff = [
        # 주방 부서 미승인
        {
            "username": "pending_kitchen_choi",
            "name": "최신입",
            "email": "pending_kitchen_choi@restaurant.com",
            "phone": "010-7777-7771",
            "position": "주방보조",
            "department": "주방",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_kitchen_kim",
            "name": "김신입",
            "email": "pending_kitchen_kim@restaurant.com",
            "phone": "010-7777-7772",
            "position": "요리사",
            "department": "주방",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_kitchen_lee",
            "name": "이신입",
            "email": "pending_kitchen_lee@restaurant.com",
            "phone": "010-7777-7773",
            "position": "조리사",
            "department": "주방",
            "role": "employee",
            "status": "pending"
        },
        
        # 홀서비스 부서 미승인
        {
            "username": "pending_service_park",
            "name": "박신입",
            "email": "pending_service_park@restaurant.com",
            "phone": "010-7777-7774",
            "position": "서버",
            "department": "홀서비스",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_service_jung",
            "name": "정신입",
            "email": "pending_service_jung@restaurant.com",
            "phone": "010-7777-7775",
            "position": "홀보조",
            "department": "홀서비스",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_service_han",
            "name": "한신입",
            "email": "pending_service_han@restaurant.com",
            "phone": "010-7777-7776",
            "position": "서빙",
            "department": "홀서비스",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_service_manager",
            "name": "김홀매니저",
            "email": "pending_service_manager@restaurant.com",
            "phone": "010-7777-7777",
            "position": "홀매니저",
            "department": "홀서비스",
            "role": "manager",
            "status": "pending"
        },
        
        # 매니지먼트 부서 미승인
        {
            "username": "pending_manager_lee",
            "name": "이매니저",
            "email": "pending_manager_lee@restaurant.com",
            "phone": "010-7777-7778",
            "position": "매니저",
            "department": "매니지먼트",
            "role": "manager",
            "status": "pending"
        },
        {
            "username": "pending_cashier_kim",
            "name": "김캐셔",
            "email": "pending_cashier_kim@restaurant.com",
            "phone": "010-7777-7779",
            "position": "캐셔",
            "department": "매니지먼트",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_accountant_park",
            "name": "박회계",
            "email": "pending_accountant_park@restaurant.com",
            "phone": "010-7777-7780",
            "position": "회계",
            "department": "매니지먼트",
            "role": "employee",
            "status": "pending"
        },
        
        # 배달 부서 미승인
        {
            "username": "pending_delivery_choi",
            "name": "최배달",
            "email": "pending_delivery_choi@restaurant.com",
            "phone": "010-7777-7781",
            "position": "배달원",
            "department": "배달",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_delivery_jung",
            "name": "정배달",
            "email": "pending_delivery_jung@restaurant.com",
            "phone": "010-7777-7782",
            "position": "배달원",
            "department": "배달",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_delivery_han",
            "name": "한배달",
            "email": "pending_delivery_han@restaurant.com",
            "phone": "010-7777-7783",
            "position": "배달원",
            "department": "배달",
            "role": "employee",
            "status": "pending"
        },
        
        # 청소 부서 미승인
        {
            "username": "pending_cleaning_kim",
            "name": "김청소",
            "email": "pending_cleaning_kim@restaurant.com",
            "phone": "010-7777-7784",
            "position": "청소원",
            "department": "청소",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_cleaning_park",
            "name": "박청소",
            "email": "pending_cleaning_park@restaurant.com",
            "phone": "010-7777-7785",
            "position": "청소원",
            "department": "청소",
            "role": "employee",
            "status": "pending"
        },
        
        # 특별한 케이스들
        {
            "username": "pending_parttime_lee",
            "name": "이파트타임",
            "email": "pending_parttime_lee@restaurant.com",
            "phone": "010-7777-7786",
            "position": "파트타임",
            "department": "홀서비스",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_intern_kim",
            "name": "김인턴",
            "email": "pending_intern_kim@restaurant.com",
            "phone": "010-7777-7787",
            "position": "인턴",
            "department": "주방",
            "role": "employee",
            "status": "pending"
        },
        {
            "username": "pending_supervisor_park",
            "name": "박수퍼바이저",
            "email": "pending_supervisor_park@restaurant.com",
            "phone": "010-7777-7788",
            "position": "수퍼바이저",
            "department": "매니지먼트",
            "role": "manager",
            "status": "pending"
        }
    ]
    
    with app.app_context():
        created_count = 0
        skipped_count = 0
        
        print("🚀 미승인 직원 예시 데이터 생성을 시작합니다...")
        print("=" * 60)
        
        for staff_data in pending_staff:
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
        
        print("\n🔐 로그인 정보 (새로 생성된 미승인 직원들):")
        print("   비밀번호 형식: {username}123")
        print("   예시: pending_kitchen_choi123, pending_service_park123")
        
        print("\n📋 부서별 미승인 직원 현황:")
        pending_departments = db.session.query(
            User.department, 
            db.func.count(User.id)
        ).filter(User.status == 'pending').group_by(User.department).all()
        
        for dept, count in pending_departments:
            if dept:
                print(f"   {dept}: {count}명")
        
        print("\n🎯 전체 직원 상태 현황:")
        statuses = db.session.query(User.status, db.func.count(User.id)).group_by(User.status).all()
        for status, count in statuses:
            if status:
                print(f"   {status}: {count}명")
        
        print("\n📝 미승인 직원 승인 방법:")
        print("   1. 직원 관리 → 직원 승인 페이지로 이동")
        print("   2. 각 직원의 '승인' 버튼 클릭")
        print("   3. 권한 설정 후 최종 승인")

def main():
    """메인 실행 함수"""
    print("🍽️  레스토랑 미승인 직원 예시 데이터 생성기")
    print("=" * 60)
    
    try:
        create_pending_staff()
        print("\n🎉 미승인 직원 예시 데이터 생성이 완료되었습니다!")
        print("이제 직원 승인 페이지에서 다양한 미승인 직원들을 확인하고 승인할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")

if __name__ == "__main__":
    main() 