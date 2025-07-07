#!/usr/bin/env python3
"""
레스토랑 관리 시스템 예시 데이터 생성 스크립트
"""

import os
import sys
from datetime import datetime, timedelta
from random import choice, randint, uniform

# Flask 앱 컨텍스트를 위해 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Order, Schedule, Notice, Notification, Report
from werkzeug.security import generate_password_hash

def create_sample_users():
    """예시 사용자 데이터 생성"""
    print("예시 사용자 데이터 생성 중...")
    
    # 기존 사용자 확인
    if User.query.count() > 1:  # admin 계정만 있다면
        print("이미 사용자 데이터가 존재합니다. 건너뜁니다.")
        return
    
    # 매니저 계정들
    managers = [
        {"username": "manager1", "email": "manager1@restaurant.com", "role": "manager", "branch": "본점"},
        {"username": "manager2", "email": "manager2@restaurant.com", "role": "manager", "branch": "강남점"},
        {"username": "manager3", "email": "manager3@restaurant.com", "role": "manager", "branch": "홍대점"},
    ]
    
    # 직원 계정들
    employees = [
        {"username": "chef1", "email": "chef1@restaurant.com", "role": "employee", "branch": "본점"},
        {"username": "chef2", "email": "chef2@restaurant.com", "role": "employee", "branch": "본점"},
        {"username": "server1", "email": "server1@restaurant.com", "role": "employee", "branch": "본점"},
        {"username": "server2", "email": "server2@restaurant.com", "role": "employee", "branch": "본점"},
        {"username": "server3", "email": "server3@restaurant.com", "role": "employee", "branch": "강남점"},
        {"username": "chef3", "email": "chef3@restaurant.com", "role": "employee", "branch": "강남점"},
        {"username": "server4", "email": "server4@restaurant.com", "role": "employee", "branch": "홍대점"},
        {"username": "chef4", "email": "chef4@restaurant.com", "role": "employee", "branch": "홍대점"},
    ]
    
    # 매니저 생성
    for manager_data in managers:
        user = User(
            username=manager_data["username"],
            email=manager_data["email"],
            password_hash=generate_password_hash("password123"),
            role=manager_data["role"],
            status="approved",
            branch=manager_data["branch"]
        )
        db.session.add(user)
    
    # 직원 생성
    for emp_data in employees:
        user = User(
            username=emp_data["username"],
            email=emp_data["email"],
            password_hash=generate_password_hash("password123"),
            role=emp_data["role"],
            status="approved",
            branch=emp_data["branch"]
        )
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ {len(managers)}명의 매니저, {len(employees)}명의 직원 생성 완료")

def create_sample_orders():
    """예시 주문 데이터 생성"""
    print("예시 주문 데이터 생성 중...")
    
    # 기존 주문 확인
    if Order.query.count() > 0:
        print("이미 주문 데이터가 존재합니다. 건너뜁니다.")
        return
    
    menu_items = [
        "김치찌개", "된장찌개", "비빔밥", "불고기", "갈비찜", "삼겹살",
        "파스타", "피자", "스테이크", "스시", "초밥", "라멘",
        "치킨", "햄버거", "샐러드", "스프", "빵", "케이크"
    ]
    
    statuses = ["pending", "cooking", "completed", "cancelled"]
    
    # 최근 30일간의 주문 데이터 생성
    for i in range(100):
        # 랜덤 날짜 (최근 30일 내)
        days_ago = randint(0, 30)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        # 랜덤 시간
        hour = randint(6, 22)  # 6시~22시
        minute = randint(0, 59)
        order_date = order_date.replace(hour=hour, minute=minute)
        
        # 랜덤 메뉴 아이템들
        num_items = randint(1, 4)
        items = [choice(menu_items) for _ in range(num_items)]
        
        # 랜덤 가격 (5000~50000원)
        total_amount = randint(5000, 50000)
        
        # 랜덤 상태
        status = choice(statuses)
        
        order = Order(
            customer_name=f"고객{i+1}",
            items=", ".join(items),
            total_amount=total_amount,
            status=status,
            table_number=randint(1, 20),
            created_at=order_date
        )
        db.session.add(order)
    
    db.session.commit()
    print("✅ 100개의 예시 주문 데이터 생성 완료")

def create_sample_schedules():
    """예시 스케줄 데이터 생성"""
    print("예시 스케줄 데이터 생성 중...")
    
    # 기존 스케줄 확인
    if Schedule.query.count() > 0:
        print("이미 스케줄 데이터가 존재합니다. 건너뜁니다.")
        return
    
    # 직원들 가져오기
    employees = User.query.filter_by(role="employee").all()
    
    if not employees:
        print("직원 데이터가 없습니다. 스케줄 생성을 건너뜁니다.")
        return
    
    shifts = ["오전", "오후", "야간", "휴식"]
    
    # 다음 30일간의 스케줄 생성
    for i in range(30):
        date = datetime.now().date() + timedelta(days=i)
        
        for employee in employees:
            # 랜덤하게 스케줄 생성 (80% 확률로 출근)
            if randint(1, 100) <= 80:
                shift = choice(shifts)
                
                schedule = Schedule(
                    user_id=employee.id,
                    date=date,
                    shift=shift,
                    start_time="09:00" if shift == "오전" else "14:00" if shift == "오후" else "18:00",
                    end_time="17:00" if shift == "오전" else "22:00" if shift == "오후" else "02:00",
                    status="approved"
                )
                db.session.add(schedule)
    
    db.session.commit()
    print("✅ 30일간의 예시 스케줄 데이터 생성 완료")

def create_sample_notices():
    """예시 공지사항 데이터 생성"""
    print("예시 공지사항 데이터 생성 중...")
    
    # 기존 공지사항 확인
    if Notice.query.count() > 0:
        print("이미 공지사항 데이터가 존재합니다. 건너뜁니다.")
        return
    
    notices = [
        {
            "title": "신메뉴 출시 안내",
            "content": "이번 주부터 새로운 메뉴 '트러플 파스타'가 출시됩니다. 많은 관심 부탁드립니다.",
            "category": "menu"
        },
        {
            "title": "직원 교육 일정",
            "content": "다음 주 화요일 오후 2시에 새로운 POS 시스템 교육이 있습니다. 모든 직원 참석 필수입니다.",
            "category": "education"
        },
        {
            "title": "위생 점검 결과",
            "content": "이번 달 위생 점검에서 우수한 성적을 거두었습니다. 계속해서 깨끗한 환경을 유지해주세요.",
            "category": "hygiene"
        },
        {
            "title": "재고 관리 주의사항",
            "content": "최근 재고 부족 사례가 늘고 있습니다. 주문 전 재고 확인을 철저히 해주세요.",
            "category": "inventory"
        },
        {
            "title": "고객 만족도 향상",
            "content": "고객 만족도 조사 결과가 좋습니다. 더 나은 서비스를 위해 노력해주세요.",
            "category": "service"
        }
    ]
    
    for notice_data in notices:
        notice = Notice(
            title=notice_data["title"],
            content=notice_data["content"],
            category=notice_data["category"],
            author_id=1,  # admin
            is_published=True
        )
        db.session.add(notice)
    
    db.session.commit()
    print("✅ 5개의 예시 공지사항 데이터 생성 완료")

def create_sample_reports():
    """예시 리포트 데이터 생성"""
    print("예시 리포트 데이터 생성 중...")
    
    # 기존 리포트 확인
    if Report.query.count() > 0:
        print("이미 리포트 데이터가 존재합니다. 건너뜁니다.")
        return
    
    # 직원들 가져오기
    employees = User.query.filter_by(role="employee").all()
    
    if not employees:
        print("직원 데이터가 없습니다. 리포트 생성을 건너뜁니다.")
        return
    
    report_types = ["daily", "weekly", "monthly"]
    report_categories = ["sales", "inventory", "staff", "customer"]
    
    # 최근 30일간의 리포트 생성
    for i in range(50):
        # 랜덤 날짜
        days_ago = randint(0, 30)
        report_date = datetime.now() - timedelta(days=days_ago)
        
        # 랜덤 직원
        employee = choice(employees)
        
        # 랜덤 리포트 타입과 카테고리
        report_type = choice(report_types)
        category = choice(report_categories)
        
        report = Report(
            user_id=employee.id,
            report_type=report_type,
            category=category,
            title=f"{category.capitalize()} {report_type.capitalize()} Report",
            content=f"This is a sample {report_type} report for {category} category.",
            created_at=report_date,
            status="submitted"
        )
        db.session.add(report)
    
    db.session.commit()
    print("✅ 50개의 예시 리포트 데이터 생성 완료")

def main():
    """메인 실행 함수"""
    print("🍽️ 레스토랑 관리 시스템 예시 데이터 생성 시작")
    print("=" * 50)
    
    with app.app_context():
        try:
            # 데이터베이스 연결 확인
            db.engine.execute("SELECT 1")
            print("✅ 데이터베이스 연결 확인")
            
            # 예시 데이터 생성
            create_sample_users()
            create_sample_orders()
            create_sample_schedules()
            create_sample_notices()
            create_sample_reports()
            
            print("=" * 50)
            print("🎉 모든 예시 데이터 생성 완료!")
            print("\n생성된 데이터:")
            print(f"- 사용자: {User.query.count()}명")
            print(f"- 주문: {Order.query.count()}개")
            print(f"- 스케줄: {Schedule.query.count()}개")
            print(f"- 공지사항: {Notice.query.count()}개")
            print(f"- 리포트: {Report.query.count()}개")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main() 