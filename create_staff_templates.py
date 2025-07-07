#!/usr/bin/env python3
"""
직원 등록 템플릿 생성 스크립트
"""

import os
import sys
from datetime import datetime, timedelta
import json

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import StaffTemplate

def create_staff_templates():
    """직원 등록을 위한 기본 템플릿들을 생성합니다."""
    
    # 기본 템플릿 데이터
    templates = [
        # 주방 부서 템플릿
        {
            "name": "주방장 기본 템플릿",
            "position": "주방장",
            "department": "주방",
            "template_type": "position",
            "salary_min": 3000000,
            "salary_max": 4000000,
            "salary_base": 3500000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "08:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "order_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": True, "edit": True, "delete": False},
                "kitchen_monitoring": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": True, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card", "food_safety_license"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "주방장 기본 템플릿 - 주방 전체 관리 및 조리 업무"
        },
        {
            "name": "요리사 기본 템플릿",
            "position": "요리사",
            "department": "주방",
            "template_type": "position",
            "salary_min": 2500000,
            "salary_max": 3200000,
            "salary_base": 2800000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": True, "edit": False, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "kitchen_monitoring": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "요리사 기본 템플릿 - 메인 요리 조리 업무"
        },
        {
            "name": "주방보조 기본 템플릿",
            "position": "주방보조",
            "department": "주방",
            "template_type": "position",
            "salary_min": 2000000,
            "salary_max": 2500000,
            "salary_base": 2200000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "kitchen_monitoring": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "주방보조 기본 템플릿 - 주방 보조 업무"
        },
        
        # 홀서비스 부서 템플릿
        {
            "name": "홀매니저 기본 템플릿",
            "position": "홀매니저",
            "department": "홀서비스",
            "template_type": "position",
            "salary_min": 2800000,
            "salary_max": 3500000,
            "salary_base": 3200000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "order_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": True, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": True, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "홀매니저 기본 템플릿 - 홀서비스 전체 관리"
        },
        {
            "name": "서버 기본 템플릿",
            "position": "서버",
            "department": "홀서비스",
            "template_type": "position",
            "salary_min": 2000000,
            "salary_max": 2500000,
            "salary_base": 2200000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "서버 기본 템플릿 - 고객 서비스 및 주문 처리"
        },
        {
            "name": "홀보조 기본 템플릿",
            "position": "홀보조",
            "department": "홀서비스",
            "template_type": "position",
            "salary_min": 1800000,
            "salary_max": 2200000,
            "salary_base": 2000000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "홀보조 기본 템플릿 - 홀서비스 보조 업무"
        },
        
        # 매니지먼트 부서 템플릿
        {
            "name": "매니저 기본 템플릿",
            "position": "매니저",
            "department": "매니지먼트",
            "template_type": "position",
            "salary_min": 3500000,
            "salary_max": 4500000,
            "salary_base": 4000000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원", "야근수당", "상여금"],
            "permissions": {
                "dashboard": {"view": True, "edit": True, "admin_only": False},
                "employee_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": True, "assign_roles": True},
                "schedule_management": {"view": True, "create": True, "edit": True, "delete": True, "approve": True},
                "order_management": {"view": True, "create": True, "edit": True, "delete": True, "approve": True},
                "inventory_management": {"view": True, "create": True, "edit": True, "delete": True},
                "notification_management": {"view": True, "send": True, "delete": True},
                "system_management": {"view": True, "backup": False, "restore": False, "settings": True, "monitoring": True},
                "reports": {"view": True, "export": True, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card", "resume"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "매니저 기본 템플릿 - 매장 전체 관리"
        },
        {
            "name": "캐셔 기본 템플릿",
            "position": "캐셔",
            "department": "매니지먼트",
            "template_type": "position",
            "salary_min": 2200000,
            "salary_max": 2800000,
            "salary_base": 2500000,
            "work_days": ["월", "화", "수", "목", "금", "토"],
            "work_hours_start": "09:00",
            "work_hours_end": "18:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": True, "edit": True, "delete": False, "approve": False},
                "inventory_management": {"view": True, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": True, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 3,
            "notice_period": 1,
            "description": "캐셔 기본 템플릿 - 결제 및 회계 업무"
        },
        
        # 배달 부서 템플릿
        {
            "name": "배달원 기본 템플릿",
            "position": "배달원",
            "department": "배달",
            "template_type": "position",
            "salary_min": 2000000,
            "salary_max": 2500000,
            "salary_base": 2200000,
            "work_days": ["월", "화", "수", "목", "금", "토", "일"],
            "work_hours_start": "10:00",
            "work_hours_end": "20:00",
            "benefits": ["4대보험", "연차휴가", "식대지원", "교통비지원", "배달수당"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "inventory_management": {"view": False, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card", "driver_license"],
            "probation_period": 1,
            "notice_period": 1,
            "description": "배달원 기본 템플릿 - 배달 업무"
        },
        
        # 청소 부서 템플릿
        {
            "name": "청소원 기본 템플릿",
            "position": "청소원",
            "department": "청소",
            "template_type": "position",
            "salary_min": 1800000,
            "salary_max": 2200000,
            "salary_base": 2000000,
            "work_days": ["월", "화", "수", "목", "금"],
            "work_hours_start": "08:00",
            "work_hours_end": "17:00",
            "benefits": ["4대보험", "연차휴가", "식대지원"],
            "permissions": {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False, "assign_roles": False},
                "schedule_management": {"view": True, "create": False, "edit": False, "delete": False, "approve": False},
                "order_management": {"view": False, "create": False, "edit": False, "delete": False, "approve": False},
                "inventory_management": {"view": False, "create": False, "edit": False, "delete": False},
                "notification_management": {"view": True, "send": False, "delete": False},
                "system_management": {"view": False, "backup": False, "restore": False, "settings": False, "monitoring": False},
                "reports": {"view": False, "export": False, "admin_only": False},
            },
            "required_documents": ["health_certificate", "id_card"],
            "probation_period": 1,
            "notice_period": 1,
            "description": "청소원 기본 템플릿 - 청소 업무"
        }
    ]
    
    with app.app_context():
        created_count = 0
        skipped_count = 0
        
        print("🚀 직원 등록 템플릿 생성을 시작합니다...")
        print("=" * 60)
        
        for template_data in templates:
            # 기존 템플릿 확인
            existing_template = StaffTemplate.query.filter_by(
                position=template_data["position"],
                department=template_data["department"],
                template_type=template_data["template_type"]
            ).first()
            
            if existing_template:
                print(f"⚠️  이미 존재: {template_data['name']}")
                skipped_count += 1
                continue
            
            # 새 템플릿 생성
            new_template = StaffTemplate(
                name=template_data["name"],
                position=template_data["position"],
                department=template_data["department"],
                template_type=template_data["template_type"],
                salary_min=template_data["salary_min"],
                salary_max=template_data["salary_max"],
                salary_base=template_data["salary_base"],
                work_days=template_data["work_days"],
                work_hours_start=template_data["work_hours_start"],
                work_hours_end=template_data["work_hours_end"],
                benefits=template_data["benefits"],
                permissions=template_data["permissions"],
                required_documents=template_data["required_documents"],
                probation_period=template_data["probation_period"],
                notice_period=template_data["notice_period"],
                description=template_data["description"]
            )
            
            try:
                db.session.add(new_template)
                db.session.commit()
                
                print(f"✅ 생성됨: {template_data['name']} - {template_data['department']} {template_data['position']}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ 생성 실패: {template_data['name']} - {str(e)}")
                db.session.rollback()
        
        print("=" * 60)
        print(f"📊 생성 결과:")
        print(f"   새로 생성: {created_count}개")
        print(f"   이미 존재: {skipped_count}개")
        print(f"   총 템플릿 수: {StaffTemplate.query.count()}개")
        
        print("\n📋 부서별 템플릿 현황:")
        departments = db.session.query(
            StaffTemplate.department, 
            db.func.count(StaffTemplate.id)
        ).group_by(StaffTemplate.department).all()
        
        for dept, count in departments:
            if dept:
                print(f"   {dept}: {count}개")
        
        print("\n🎯 직책별 템플릿 현황:")
        positions = db.session.query(
            StaffTemplate.position, 
            db.func.count(StaffTemplate.id)
        ).group_by(StaffTemplate.position).all()
        
        for pos, count in positions:
            if pos:
                print(f"   {pos}: {count}개")

def main():
    """메인 실행 함수"""
    print("🍽️  레스토랑 직원 등록 템플릿 생성기")
    print("=" * 60)
    
    try:
        create_staff_templates()
        print("\n🎉 직원 등록 템플릿 생성이 완료되었습니다!")
        print("이제 단계별 직원 등록 시스템에서 템플릿을 활용할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        print("데이터베이스 연결이나 모델 설정을 확인해주세요.")

if __name__ == "__main__":
    main() 