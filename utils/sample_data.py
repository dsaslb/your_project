import random
import logging
from datetime import datetime, timedelta
from typing import List

from extensions import db
from models import ActionLog, ApproveLog, Attendance, Branch, Feedback, User, Staff
from utils.logger import log_action

logger = logging.getLogger(__name__)


def create_sample_data():
    """샘플 데이터 생성"""
    try:
        # 기존 데이터 삭제
        db.session.query(Feedback).delete()
        db.session.query(Attendance).delete()
        db.session.query(ActionLog).delete()
        db.session.query(ApproveLog).delete()
        db.session.query(Staff).delete()
        db.session.query(User).delete()
        db.session.query(Branch).delete()

        # 지점 생성
        branches = [
            Branch(name="본사"),
            Branch(name="강남점"),
            Branch(name="홍대점"),
            Branch(name="부산점"),
            Branch(name="대구점"),
        ]
        for branch in branches:
            db.session.add(branch)
        db.session.commit()

        # 관리자 계정 생성
        admin = User(username="admin", email="admin@example.com", role="admin", status="approved", branch_id=1)
        admin.set_password("admin123")
        db.session.add(admin)

        # 매니저 계정 생성
        manager1 = User(username="manager1", email="manager1@example.com", role="manager", status="approved", branch_id=2)
        manager1.set_password("manager123")
        db.session.add(manager1)

        manager2 = User(username="manager2", email="manager2@example.com", role="manager", status="approved", branch_id=3)
        manager2.set_password("manager123")
        db.session.add(manager2)

        # 직원 계정 생성
        employees = [
            ("employee1", 2, "김철수", "주방장", "주방"),
            ("employee2", 2, "이영희", "서버", "홀"),
            ("employee3", 2, "박민수", "주방보조", "주방"),
            ("employee4", 3, "정수진", "매니저", "관리"),
            ("employee5", 3, "최동욱", "서버", "홀"),
            ("employee6", 3, "한미영", "캐셔", "홀"),
            ("employee7", 4, "송태호", "주방장", "주방"),
            ("employee8", 4, "윤지영", "서버", "홀"),
            ("employee9", 5, "임재현", "매니저", "관리"),
            ("employee10", 5, "강소영", "서버", "홀"),
        ]

        for username, branch_id, name, position, department in employees:
            user = User(
                username=username, 
                email=f"{username}@example.com", 
                role="employee", 
                status="approved", 
                branch_id=branch_id
            )
            user.set_password("employee123")
            db.session.add(user)
            db.session.flush()  # ID 생성
            
            # Staff 프로필 생성
            staff = Staff(
                name=name,
                position=position,
                department=department,
                email=f"{username}@example.com",
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                join_date=datetime.now().date() - timedelta(days=random.randint(30, 365)),
                salary=str(random.randint(2500000, 3500000)),
                restaurant_id=branch_id,
                user_id=user.id
            )
            db.session.add(staff)

        # 대기 중인 사용자
        pending_users = [
            ("pending1", 2, "임승우", "주방보조", "주방"),
            ("pending2", 3, "김미라", "서버", "홀"),
            ("pending3", 4, "박준호", "배송원", "배송"),
        ]

        for username, branch_id, name, position, department in pending_users:
            user = User(
                username=username, 
                email=f"{username}@example.com", 
                role="employee", 
                status="pending", 
                branch_id=branch_id
            )
            user.set_password("pending123")
            db.session.add(user)
            db.session.flush()  # ID 생성
            
            # Staff 프로필 생성
            staff = Staff(
                name=name,
                position=position,
                department=department,
                email=f"{username}@example.com",
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                join_date=datetime.now().date(),
                salary=str(random.randint(2500000, 3500000)),
                restaurant_id=branch_id,
                user_id=user.id
            )
            db.session.add(staff)

        # 거절된 사용자
        rejected_users = [
            ("rejected1", 2, "이철수", "주방보조", "주방"),
            ("rejected2", 3, "김영희", "서버", "홀"),
        ]

        for username, branch_id, name, position, department in rejected_users:
            user = User(
                username=username, 
                email=f"{username}@example.com", 
                role="employee", 
                status="rejected", 
                branch_id=branch_id
            )
            user.set_password("rejected123")
            db.session.add(user)
            db.session.flush()  # ID 생성
            
            # Staff 프로필 생성
            staff = Staff(
                name=name,
                position=position,
                department=department,
                email=f"{username}@example.com",
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                join_date=datetime.now().date(),
                salary=str(random.randint(2500000, 3500000)),
                restaurant_id=branch_id,
                user_id=user.id
            )
            db.session.add(staff)

        db.session.commit()

        # 출퇴근 기록 생성 (최근 30일)
        users = User.query.filter_by(status="approved").all()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        for user in users:
            current_date = start_date
            while current_date <= end_date:
                # 주말 제외
                if current_date.weekday() < 5:  # 월-금
                    # 출근 시간 (8:30-9:30 사이)
                    clock_in_hour = 8
                    clock_in_minute = random.randint(30, 90)
                    if clock_in_minute >= 60:
                        clock_in_hour += 1
                        clock_in_minute -= 60

                    clock_in = current_date.replace(
                        hour=clock_in_hour, minute=clock_in_minute, second=0, microsecond=0
                    )

                    # 퇴근 시간 (17:30-19:00 사이)
                    clock_out_hour = 17
                    clock_out_minute = random.randint(30, 60)
                    if clock_out_minute >= 60:
                        clock_out_hour += 1
                        clock_out_minute -= 60

                    clock_out = current_date.replace(
                        hour=clock_out_hour,
                        minute=clock_out_minute,
                        second=0,
                        microsecond=0,
                    )

                    attendance = Attendance(
                        user_id=user.id, clock_in=clock_in, clock_out=clock_out
                    )
                    db.session.add(attendance)

                current_date += timedelta(days=1)

        # 액션 로그 생성
        actions = ["login", "logout", "clockin", "clockout", "register"]
        for user in users:
            for _ in range(random.randint(5, 15)):
                action = random.choice(actions)
                log = ActionLog(
                    user_id=user.id, action=action, message=f"샘플 {action} 로그"
                )
                db.session.add(log)

        # 승인/거절 로그 생성
        approvers = [admin, manager1, manager2]
        pending_users = User.query.filter_by(status="pending").all()
        rejected_users = User.query.filter_by(status="rejected").all()

        for user in pending_users + rejected_users:
            approver = random.choice(approvers)
            action = "approved" if user.status == "approved" else "rejected"
            reason = "샘플 승인 사유" if action == "approved" else "샘플 거절 사유"

            log = ApproveLog(
                user_id=user.id, admin_id=approver.id, action=action, reason=reason
            )
            db.session.add(log)

        # 피드백 생성
        for user in users:
            for _ in range(random.randint(1, 3)):
                feedback = Feedback(
                    user_id=user.id,
                    satisfaction=random.randint(1, 5),
                    health=random.randint(1, 5),
                    comment=f"샘플 피드백 {random.randint(1, 100)}",
                )
                db.session.add(feedback)

        db.session.commit()
        logger.info("샘플 데이터 생성 완료!")

    except Exception as e:
        logger.error(f"샘플 데이터 생성 실패: {e}")
        db.session.rollback()


if __name__ == "__main__":
    from app import app

    with app.app_context():
        create_sample_data()
