#!/usr/bin/env python3
"""
테스트용 더미 데이터 생성 스크립트
관리자, 매장관리자, 직원 샘플 계정과 권한을 자동으로 생성합니다.
"""

import os
import sys
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

# Flask 앱 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Branch, Notification, Order, Schedule, User


def create_test_users():
    """테스트용 사용자 계정 생성"""
    print("🧪 테스트용 더미 데이터 생성 시작...")

    with app.app_context():
        # 기존 테스트 데이터 삭제 (선택사항)
        if input("기존 테스트 데이터를 삭제하시겠습니까? (y/N): ").lower() == "y":
            User.query.filter(User.username.like("test_%")).delete()
            db.session.commit()
            print("✅ 기존 테스트 데이터 삭제 완료")

        # 1. 최고관리자 계정 생성
        admin_user = User(
            username="test_admin",
            email="admin@test.com",
            password_hash=generate_password_hash("admin123!"),
            role="admin",
            grade="최고관리자",
            status="approved",
            created_at=datetime.now() - timedelta(days=30),
        )

        # 최고관리자 권한 설정 (모든 권한)
        admin_user.permissions = {
            "dashboard": {"view": True, "edit": True, "admin_only": True},
            "employee_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": True,
                "approve": True,
                "assign_roles": True,
            },
            "schedule_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": True,
                "approve": True,
            },
            "order_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": True,
                "approve": True,
            },
            "inventory_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": True,
            },
            "notification_management": {"view": True, "send": True, "delete": True},
            "system_management": {
                "view": True,
                "backup": True,
                "restore": True,
                "settings": True,
                "monitoring": True,
            },
            "reports": {"view": True, "export": True, "admin_only": True},
        }

        db.session.add(admin_user)
        print("✅ 최고관리자 계정 생성: test_admin / admin123!")

        # 2. 매장관리자 계정들 생성
        manager_users = []
        for i in range(1, 4):  # 3명의 매장관리자
            manager = User(
                username=f"test_manager{i}",
                email=f"manager{i}@test.com",
                password_hash=generate_password_hash("manager123!"),
                role="manager",
                grade="매장관리자",
                status="approved",
                created_at=datetime.now() - timedelta(days=20 + i),
            )

            # 매장관리자 권한 설정 (제한된 관리 권한)
            manager.permissions = {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {
                    "view": True,
                    "create": True,
                    "edit": True,
                    "delete": False,
                    "approve": True,
                    "assign_roles": False,
                },
                "schedule_management": {
                    "view": True,
                    "create": True,
                    "edit": True,
                    "delete": True,
                    "approve": True,
                },
                "order_management": {
                    "view": True,
                    "create": True,
                    "edit": True,
                    "delete": False,
                    "approve": True,
                },
                "inventory_management": {
                    "view": True,
                    "create": True,
                    "edit": True,
                    "delete": False,
                },
                "notification_management": {
                    "view": True,
                    "send": True,
                    "delete": False,
                },
                "system_management": {
                    "view": False,
                    "backup": False,
                    "restore": False,
                    "settings": False,
                    "monitoring": False,
                },
                "reports": {"view": True, "export": True, "admin_only": False},
            }

            manager_users.append(manager)
            db.session.add(manager)
            print(f"✅ 매장관리자 계정 생성: test_manager{i} / manager123!")

        # 3. 직원 계정들 생성
        employee_users = []
        for i in range(1, 11):  # 10명의 직원
            employee = User(
                username=f"test_employee{i}",
                email=f"employee{i}@test.com",
                password_hash=generate_password_hash("employee123!"),
                role="employee",
                grade="직원",
                status="approved",
                created_at=datetime.now() - timedelta(days=10 + i),
            )

            # 직원 권한 설정 (기본 업무 권한)
            employee.permissions = {
                "dashboard": {"view": True, "edit": False, "admin_only": False},
                "employee_management": {
                    "view": False,
                    "create": False,
                    "edit": False,
                    "delete": False,
                    "approve": False,
                    "assign_roles": False,
                },
                "schedule_management": {
                    "view": True,
                    "create": False,
                    "edit": False,
                    "delete": False,
                    "approve": False,
                },
                "order_management": {
                    "view": True,
                    "create": True,
                    "edit": False,
                    "delete": False,
                    "approve": False,
                },
                "inventory_management": {
                    "view": True,
                    "create": False,
                    "edit": False,
                    "delete": False,
                },
                "notification_management": {
                    "view": False,
                    "send": False,
                    "delete": False,
                },
                "system_management": {
                    "view": False,
                    "backup": False,
                    "restore": False,
                    "settings": False,
                    "monitoring": False,
                },
                "reports": {"view": False, "export": False, "admin_only": False},
            }

            employee_users.append(employee)
            db.session.add(employee)
            print(f"✅ 직원 계정 생성: test_employee{i} / employee123!")

        # 4. 특별 권한 직원 생성 (고급 권한)
        senior_employee = User(
            username="test_senior",
            email="senior@test.com",
            password_hash=generate_password_hash("senior123!"),
            role="employee",
            grade="주임",
            status="approved",
            created_at=datetime.now() - timedelta(days=15),
        )

        # 주임 권한 설정 (일부 관리 권한)
        senior_employee.permissions = {
            "dashboard": {"view": True, "edit": False, "admin_only": False},
            "employee_management": {
                "view": True,
                "create": False,
                "edit": False,
                "delete": False,
                "approve": False,
                "assign_roles": False,
            },
            "schedule_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": False,
                "approve": False,
            },
            "order_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": False,
                "approve": True,
            },
            "inventory_management": {
                "view": True,
                "create": True,
                "edit": True,
                "delete": False,
            },
            "notification_management": {"view": True, "send": False, "delete": False},
            "system_management": {
                "view": False,
                "backup": False,
                "restore": False,
                "settings": False,
                "monitoring": False,
            },
            "reports": {"view": True, "export": False, "admin_only": False},
        }

        db.session.add(senior_employee)
        print("✅ 주임 계정 생성: test_senior / senior123!")

        # 5. 승인 대기 중인 계정 생성
        pending_user = User(
            username="test_pending",
            email="pending@test.com",
            password_hash=generate_password_hash("pending123!"),
            role="employee",
            grade="직원",
            status="pending",
            created_at=datetime.now() - timedelta(days=5),
        )

        db.session.add(pending_user)
        print("✅ 승인 대기 계정 생성: test_pending / pending123!")

        # 데이터베이스에 저장
        try:
            db.session.commit()
            print("\n🎉 테스트 데이터 생성 완료!")

            # 생성된 계정 요약 출력
            print("\n📋 생성된 테스트 계정 목록:")
            print("=" * 50)
            print("최고관리자:")
            print("  - test_admin / admin123!")
            print("\n매장관리자:")
            for i in range(1, 4):
                print(f"  - test_manager{i} / manager123!")
            print("\n직원:")
            for i in range(1, 11):
                print(f"  - test_employee{i} / employee123!")
            print("  - test_senior / senior123!")
            print("\n승인 대기:")
            print("  - test_pending / pending123!")

            print("\n🔐 권한별 접근 테스트:")
            print("=" * 50)
            print("1. 최고관리자로 로그인하여 모든 메뉴 접근 가능")
            print("2. 매장관리자로 로그인하여 제한된 관리 메뉴 접근")
            print("3. 직원으로 로그인하여 기본 업무 메뉴만 접근")
            print("4. 권한 관리 페이지에서 권한 수정 테스트")

        except Exception as e:
            db.session.rollback()
            print(f"❌ 오류 발생: {e}")
            return False

    return True


def create_test_data():
    """테스트용 업무 데이터 생성"""
    print("\n📊 테스트용 업무 데이터 생성...")

    with app.app_context():
        # 스케줄 데이터 생성
        for i in range(1, 8):  # 이번 주 스케줄
            date = datetime.now().date() + timedelta(days=i - 1)

            # 매장관리자 스케줄
            for j, manager in enumerate(User.query.filter_by(role="manager").all()[:2]):
                schedule = Schedule(
                    user_id=manager.id,
                    date=date,
                    start_time="09:00",
                    end_time="18:00",
                    type="work",
                    status="approved",
                    created_at=datetime.now() - timedelta(days=i),
                )
                db.session.add(schedule)

            # 직원 스케줄
            for j, employee in enumerate(
                User.query.filter_by(role="employee").all()[:5]
            ):
                if i % 2 == 0:  # 짝수일만 근무
                    schedule = Schedule(
                        user_id=employee.id,
                        date=date,
                        start_time="10:00" if j % 2 == 0 else "14:00",
                        end_time="19:00" if j % 2 == 0 else "22:00",
                        type="work",
                        status="approved",
                        created_at=datetime.now() - timedelta(days=i),
                    )
                    db.session.add(schedule)

        # 발주 데이터 생성
        for i in range(1, 6):
            order = Order(
                user_id=User.query.filter_by(role="employee").first().id,
                title=f"테스트 발주 {i}",
                description=f"테스트용 발주 상품 {i}",
                quantity=i * 10,
                status="pending" if i % 2 == 0 else "approved",
                created_at=datetime.now() - timedelta(days=i),
            )
            db.session.add(order)

        # 알림 데이터 생성
        for i in range(1, 4):
            notification = Notification(
                user_id=User.query.filter_by(role="admin").first().id,
                title=f"테스트 알림 {i}",
                message=f"테스트용 알림 메시지 {i}입니다.",
                type="info",
                is_read=False,
                created_at=datetime.now() - timedelta(hours=i),
            )
            db.session.add(notification)

        try:
            db.session.commit()
            print("✅ 테스트 업무 데이터 생성 완료!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 업무 데이터 생성 오류: {e}")


def main():
    """메인 실행 함수"""
    print("🚀 레스토랑 관리 시스템 - 테스트 데이터 생성기")
    print("=" * 60)

    # 사용자 계정 생성
    if create_test_users():
        # 업무 데이터 생성
        create_test_data()

        print("\n🎯 테스트 준비 완료!")
        print("이제 각 계정으로 로그인하여 권한별 메뉴 분기를 테스트할 수 있습니다.")
        print("\n💡 테스트 시나리오:")
        print("1. test_admin으로 로그인 → 최고관리자 메뉴 확인")
        print("2. test_manager1으로 로그인 → 매장관리자 메뉴 확인")
        print("3. test_employee1으로 로그인 → 직원 메뉴 확인")
        print("4. 권한 관리 페이지에서 권한 수정 테스트")
    else:
        print("❌ 테스트 데이터 생성에 실패했습니다.")


if __name__ == "__main__":
    main()
