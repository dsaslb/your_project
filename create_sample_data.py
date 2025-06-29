# -*- coding: utf-8 -*-

from datetime import date, datetime, time

from werkzeug.security import generate_password_hash

from app import app, db
from models import Branch, CleaningPlan, Order, Schedule, User


def create_sample_data():
    """예시 데이터 생성"""

    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()

        # 이미 데이터가 있는지 확인
        if User.query.filter_by(username="admin").first():
            print("이미 예시 데이터가 존재합니다.")
            return

        print("예시 데이터를 생성합니다...")

        # 1. 지점 생성
        branch = Branch(
            name="본점", address="서울시 강남구 테헤란로 123", phone="02-1234-5678"
        )
        db.session.add(branch)
        db.session.commit()

        # 2. 사용자 생성
        users = [
            User(
                username="admin",
                password=generate_password_hash("admin123"),
                role="admin",
                status="approved",
                name="관리자",
                phone="010-1234-5678",
                email="admin@restaurant.com",
                branch_id=branch.id,
            ),
            User(
                username="매니저",
                password=generate_password_hash("manager123"),
                role="manager",
                status="approved",
                name="김매니저",
                phone="010-2345-6789",
                email="manager@restaurant.com",
                branch_id=branch.id,
            ),
            User(
                username="김직원",
                password=generate_password_hash("employee123"),
                role="employee",
                status="approved",
                name="김직원",
                phone="010-3456-7890",
                email="employee1@restaurant.com",
                branch_id=branch.id,
            ),
            User(
                username="박스태프",
                password=generate_password_hash("staff123"),
                role="employee",
                status="approved",
                name="박스태프",
                phone="010-4567-8901",
                email="employee2@restaurant.com",
                branch_id=branch.id,
            ),
            User(
                username="이청소",
                password=generate_password_hash("clean123"),
                role="employee",
                status="approved",
                name="이청소",
                phone="010-5678-9012",
                email="cleaner@restaurant.com",
                branch_id=branch.id,
            ),
        ]

        for user in users:
            db.session.add(user)
        db.session.commit()

        print("✅ 예시 데이터 생성 완료!")
        print("\n📋 생성된 데이터:")
        print(f"- 사용자: {len(users)}명 (admin, 매니저, 김직원, 박스태프, 이청소)")
        print("\n🔑 로그인 정보:")
        print("- admin / admin123")
        print("- 매니저 / manager123")
        print("- 김직원 / employee123")
        print("- 박스태프 / staff123")
        print("- 이청소 / clean123")

        # 발주 예시 데이터
        orders = [
            Order(
                item="닭고기 10kg",
                quantity=1,
                order_date=date(2025, 6, 25),
                ordered_by=2,
            ),
            Order(
                item="종이컵", quantity=2, order_date=date(2025, 6, 25), ordered_by=3
            ),
            Order(
                item="채소 세트", quantity=3, order_date=date(2025, 6, 26), ordered_by=4
            ),
            Order(
                item="조미료", quantity=5, order_date=date(2025, 6, 26), ordered_by=2
            ),
        ]

        # 청소 계획 예시 데이터
        cleanings = [
            CleaningPlan(
                date=date(2025, 6, 25), plan="주방 소독", team="주방", manager_id=3
            ),
            CleaningPlan(
                date=date(2025, 6, 25), plan="홀 바닥청소", team="홀", manager_id=4
            ),
            CleaningPlan(
                date=date(2025, 6, 26), plan="화장실 청소", team="화장실", manager_id=3
            ),
            CleaningPlan(
                date=date(2025, 6, 26), plan="주방 정리정돈", team="주방", manager_id=4
            ),
        ]

        # 스케줄 예시 데이터 (기존에 추가)
        schedules = [
            Schedule(
                user_id=3,
                date=date(2025, 6, 25),
                start_time=time(9, 0),
                end_time=time(18, 0),
                category="근무",
                memo="오픈",
            ),
            Schedule(
                user_id=4,
                date=date(2025, 6, 25),
                start_time=time(14, 0),
                end_time=time(22, 0),
                category="근무",
                memo="마감",
            ),
            Schedule(
                user_id=3,
                date=date(2025, 6, 26),
                start_time=time(10, 0),
                end_time=time(19, 0),
                category="근무",
                memo="중간",
            ),
            Schedule(
                user_id=4,
                date=date(2025, 6, 26),
                start_time=time(15, 0),
                end_time=time(23, 0),
                category="근무",
                memo="마감",
            ),
            Schedule(
                user_id=3,
                date=date(2025, 6, 27),
                start_time=time(8, 0),
                end_time=time(17, 0),
                category="청소",
                memo="주방청소",
            ),
            Schedule(
                user_id=4,
                date=date(2025, 6, 27),
                start_time=time(16, 0),
                end_time=time(24, 0),
                category="근무",
                memo="마감",
            ),
        ]


if __name__ == "__main__":
    create_sample_data()
