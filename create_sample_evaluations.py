#!/usr/bin/env python3
"""
근태 평가 샘플 데이터 생성 스크립트
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from datetime import date, datetime, timedelta

from app import app, db
from models import Attendance, AttendanceReport, User


def create_sample_evaluations():
    """샘플 근태 평가 데이터 생성"""
    with app.app_context():
        # 사용자 조회
        users = User.query.filter_by(status="approved").all()
        if not users:
            print("사용자가 없습니다. 먼저 사용자를 생성해주세요.")
            return

        # 관리자 조회
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            print("관리자가 없습니다. 먼저 관리자를 생성해주세요.")
            return

        print(f"총 {len(users)}명의 사용자에 대해 샘플 평가 데이터를 생성합니다...")

        # 각 사용자별로 과거 3개월간의 평가 데이터 생성
        for user in users:
            if user.role == "admin":
                continue  # 관리자는 제외

            print(f"  - {user.username} ({user.name or '이름없음'})")

            # 과거 3개월간 월별 평가 생성
            for i in range(3):
                # 평가 기간 설정 (이번 달부터 역순)
                end_date = date.today().replace(day=1) - timedelta(days=i * 30)
                start_date = end_date.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(
                    days=1
                )

                # 랜덤 통계 생성
                total_days = random.randint(20, 25)  # 월 20-25일 근무
                late_count = random.randint(0, 3)  # 지각 0-3회
                early_leave_count = random.randint(0, 2)  # 조퇴 0-2회
                overtime_count = random.randint(0, 5)  # 야근 0-5회
                normal_count = total_days - late_count - early_leave_count

                # 점수 계산
                score = 100
                score -= late_count * 5
                score -= early_leave_count * 3
                overtime_bonus = min(overtime_count * 2, 10)
                score += overtime_bonus
                normal_bonus = min(normal_count * 1, 20)
                score += normal_bonus
                score = max(0, min(100, score))

                # 등급 부여
                if score >= 90:
                    grade = "A+"
                elif score >= 80:
                    grade = "A"
                elif score >= 70:
                    grade = "B+"
                elif score >= 60:
                    grade = "B"
                elif score >= 50:
                    grade = "C+"
                elif score >= 40:
                    grade = "C"
                else:
                    grade = "D"

                # 평가 코멘트 생성
                comments = [
                    "전반적으로 양호한 근태를 보여줍니다.",
                    "시간 준수에 더욱 신경 써주세요.",
                    "야근이 많아 고생이 많습니다. 건강에 유의하세요.",
                    "정시 출근률이 높아 칭찬합니다.",
                    "조퇴가 잦은 편입니다. 사전 보고를 부탁드립니다.",
                    "근무 태도가 매우 좋습니다.",
                    "개선의 여지가 있습니다.",
                    "안정적인 근태를 유지하고 있습니다.",
                    "지각이 있어 아쉽습니다. 개선 부탁드립니다.",
                    "전체적으로 만족스러운 근태입니다.",
                ]

                comment = random.choice(comments)

                # 기존 평가가 있는지 확인
                existing = AttendanceReport.query.filter_by(
                    user_id=user.id,
                    period_from=start_date.strftime("%Y-%m-%d"),
                    period_to=end_date.strftime("%Y-%m-%d"),
                ).first()

                if not existing:
                    # 새 평가 생성
                    evaluation = AttendanceReport(
                        user_id=user.id,
                        period_from=start_date.strftime("%Y-%m-%d"),
                        period_to=end_date.strftime("%Y-%m-%d"),
                        total=total_days,
                        late=late_count,
                        early=early_leave_count,
                        ot=overtime_count,
                        ontime=normal_count,
                        score=score,
                        grade=grade,
                        comment=comment,
                        created_at=datetime.now() - timedelta(days=i * 30),
                    )
                    db.session.add(evaluation)
                    print(
                        f"    {start_date.strftime('%Y-%m')}: {score}점 ({grade}) - {comment[:20]}..."
                    )

        # 데이터베이스에 저장
        db.session.commit()
        print(f"\n✅ 샘플 근태 평가 데이터 생성 완료!")
        print(f"   - 총 {len(users)-1}명의 사용자")
        print(f"   - 각 사용자별 3개월간 평가 데이터")
        print(f"   - 관리자: {admin.username}")


if __name__ == "__main__":
    create_sample_evaluations()
