#!/usr/bin/env python3
"""
사유 템플릿 기능 테스트 스크립트
"""

from datetime import date, datetime, timedelta

from app import app, db
from models import Attendance, Notification, ReasonTemplate, User


def test_reason_templates():
    """사유 템플릿 기능 테스트"""
    print("=== 사유 템플릿 기능 테스트 시작 ===")

    with app.app_context():
        # 1. 기존 템플릿 확인
        print("\n1. 기존 사유 템플릿 확인:")
        templates = ReasonTemplate.query.all()
        if templates:
            for t in templates:
                print(f"  - {t.text} (팀: {t.team or '전체'})")
        else:
            print("  등록된 템플릿이 없습니다.")

        # 2. 샘플 템플릿 추가
        print("\n2. 샘플 템플릿 추가:")
        sample_templates = [
            "월요일 컨디션 저하",
            "금요일 야근",
            "수요일 중간점검",
            "개인사정",
            "교통사고",
            "병원진료",
        ]

        for text in sample_templates:
            if not ReasonTemplate.query.filter_by(text=text).first():
                template = ReasonTemplate(text=text, created_by=1)  # 관리자 ID
                db.session.add(template)
                print(f"  - {text} 추가됨")
            else:
                print(f"  - {text} 이미 존재")

        db.session.commit()

        # 3. 팀별 템플릿 추가
        print("\n3. 팀별 템플릿 추가:")
        team_templates = [
            ("주방", "조리 준비"),
            ("주방", "재료 정리"),
            ("홀", "고객 응대"),
            ("홀", "테이블 정리"),
        ]

        for team, text in team_templates:
            if not ReasonTemplate.query.filter_by(text=text, team=team).first():
                template = ReasonTemplate(text=text, team=team, created_by=1)
                db.session.add(template)
                print(f"  - {team}: {text} 추가됨")
            else:
                print(f"  - {team}: {text} 이미 존재")

        db.session.commit()

        # 4. 템플릿 조회 테스트
        print("\n4. 템플릿 조회 테스트:")

        # 전체 템플릿
        all_templates = ReasonTemplate.query.filter_by(is_active=True).all()
        print(f"  전체 템플릿 수: {len(all_templates)}")

        # 팀별 템플릿
        kitchen_templates = ReasonTemplate.query.filter_by(
            team="주방", is_active=True
        ).all()
        print(f"  주방 템플릿 수: {len(kitchen_templates)}")

        hall_templates = ReasonTemplate.query.filter_by(team="홀", is_active=True).all()
        print(f"  홀 템플릿 수: {len(hall_templates)}")

        # 5. 근태 사유 업데이트 테스트
        print("\n5. 근태 사유 업데이트 테스트:")

        # 기존 근태 기록 확인
        attendances = (
            Attendance.query.filter(Attendance.reason.isnot(None)).limit(5).all()
        )
        if attendances:
            print(f"  기존 사유가 있는 근태 기록: {len(attendances)}개")
            for att in attendances:
                print(f"    - {att.clock_in.date()}: {att.reason}")
        else:
            print("  기존 사유가 있는 근태 기록이 없습니다.")

        # 6. 알림 기능 테스트
        print("\n6. 알림 기능 테스트:")

        # 지각 관련 알림 확인
        late_notifications = Notification.query.filter(
            Notification.content.like("%지각%"), Notification.category == "근무"
        ).all()

        print(f"  지각 관련 알림 수: {len(late_notifications)}")
        for noti in late_notifications[:3]:  # 최근 3개만
            print(f"    - {noti.created_at.strftime('%Y-%m-%d')}: {noti.content}")

        # 7. AI 추천 기능 테스트
        print("\n7. AI 추천 기능 테스트:")

        from app import ai_recommend_reason

        test_dates = [
            date.today(),
            date.today() - timedelta(days=1),
            date.today() - timedelta(days=2),
        ]

        for test_date in test_dates:
            recommendation = ai_recommend_reason(None, test_date)
            if recommendation:
                print(f"  {test_date.strftime('%Y-%m-%d')}: {recommendation}")
            else:
                print(f"  {test_date.strftime('%Y-%m-%d')}: 추천 없음")

        print("\n=== 사유 템플릿 기능 테스트 완료 ===")


def test_mobile_api():
    """모바일 API 테스트"""
    print("\n=== 모바일 API 테스트 시작 ===")

    with app.app_context():
        # 1. 템플릿 API 테스트
        print("\n1. 템플릿 API 테스트:")

        # 전체 템플릿
        all_templates = ReasonTemplate.query.filter_by(is_active=True).all()
        template_texts = [t.text for t in all_templates]
        print(f"  전체 템플릿: {template_texts}")

        # 팀별 템플릿
        kitchen_templates = ReasonTemplate.query.filter_by(
            team="주방", is_active=True
        ).all()
        kitchen_texts = [t.text for t in kitchen_templates]
        print(f"  주방 템플릿: {kitchen_texts}")

        # 2. 근태 사유 업데이트 API 테스트
        print("\n2. 근태 사유 업데이트 API 테스트:")

        # 테스트용 근태 기록 찾기
        test_attendance = Attendance.query.first()
        if test_attendance:
            print(
                f"  테스트 근태 기록: ID {test_attendance.id}, 사용자 {test_attendance.user_id}"
            )
            print(f"  현재 사유: {test_attendance.reason or '없음'}")
        else:
            print("  테스트할 근태 기록이 없습니다.")

        print("\n=== 모바일 API 테스트 완료 ===")


if __name__ == "__main__":
    test_reason_templates()
    test_mobile_api()
