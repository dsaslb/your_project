#!/usr/bin/env python3
"""
근태 관리 시스템 스케줄러
정기적인 리포트 생성 및 이메일 발송을 담당합니다.
"""

import logging
import os
import sys
from datetime import date, datetime, timedelta

from sqlalchemy import and_, extract

# Flask 앱 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db as db_instance
from models import Attendance, User, db

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scheduler.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def send_weekly_report():
    """주간 근태 리포트 발송"""
    try:
        logger.info("주간 근태 리포트 발송 시작")

        with app.app_context():
            # 관리자 목록 조회
            admins = User.query.filter_by(role="admin").all()

            if not admins:
                logger.warning("발송할 관리자가 없습니다.")
                return

            # 주간 데이터 생성
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

            records = Attendance.query.filter(
                and_(Attendance.clock_in >= start_date, Attendance.clock_in <= end_date)
            ).all()

            # 통계 계산
            stats = {
                "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                "total_records": len(records),
                "total_hours": 0,
                "late_count": 0,
                "early_leave_count": 0,
                "absent_count": 0,
            }

            for record in records:
                if record.clock_in and record.clock_out:
                    work_seconds = (record.clock_out - record.clock_in).total_seconds()
                    work_hours = work_seconds / 3600
                    stats["total_hours"] += work_hours

                    if (
                        record.clock_in.time()
                        > datetime.strptime("09:00", "%H:%M").time()
                    ):
                        stats["late_count"] += 1
                    if (
                        record.clock_out.time()
                        < datetime.strptime("18:00", "%H:%M").time()
                    ):
                        stats["early_leave_count"] += 1
                else:
                    stats["absent_count"] += 1

            # 이메일 본문 생성
            email_body = f"""
주간 근태 리포트

기간: {stats['period']}
총 기록: {stats['total_records']}건
총 근무시간: {round(stats['total_hours'], 2)}시간
지각: {stats['late_count']}건
조퇴: {stats['early_leave_count']}건
결근: {stats['absent_count']}건

감사합니다.
"""

            # 이메일 발송 (테스트용)
            success_count = 0
            for admin in admins:
                if admin.email:
                    # 실제 환경에서는 SMTP 설정 필요
                    print(f"이메일 발송 테스트: {admin.email}")
                    print(f"제목: 주간 근태 리포트")
                    print(f"내용: {email_body}")
                    success_count += 1

            logger.info(f"주간 리포트 발송 완료: {success_count}/{len(admins)}명")

    except Exception as e:
        logger.error(f"주간 리포트 발송 중 오류: {str(e)}")


def send_monthly_report():
    """월간 근태 리포트 발송"""
    try:
        logger.info("월간 근태 리포트 발송 시작")

        with app.app_context():
            # 관리자 목록 조회
            admins = User.query.filter_by(role="admin").all()

            if not admins:
                logger.warning("발송할 관리자가 없습니다.")
                return

            # 월간 데이터 생성
            start_date = date.today().replace(day=1)
            end_date = date.today()

            records = Attendance.query.filter(
                and_(Attendance.clock_in >= start_date, Attendance.clock_in <= end_date)
            ).all()

            # 통계 계산
            stats = {
                "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
                "total_records": len(records),
                "total_hours": 0,
                "late_count": 0,
                "early_leave_count": 0,
                "absent_count": 0,
            }

            for record in records:
                if record.clock_in and record.clock_out:
                    work_seconds = (record.clock_out - record.clock_in).total_seconds()
                    work_hours = work_seconds / 3600
                    stats["total_hours"] += work_hours

                    if (
                        record.clock_in.time()
                        > datetime.strptime("09:00", "%H:%M").time()
                    ):
                        stats["late_count"] += 1
                    if (
                        record.clock_out.time()
                        < datetime.strptime("18:00", "%H:%M").time()
                    ):
                        stats["early_leave_count"] += 1
                else:
                    stats["absent_count"] += 1

            # 이메일 본문 생성
            email_body = f"""
월간 근태 리포트

기간: {stats['period']}
총 기록: {stats['total_records']}건
총 근무시간: {round(stats['total_hours'], 2)}시간
지각: {stats['late_count']}건
조퇴: {stats['early_leave_count']}건
결근: {stats['absent_count']}건

감사합니다.
"""

            # 이메일 발송 (테스트용)
            success_count = 0
            for admin in admins:
                if admin.email:
                    # 실제 환경에서는 SMTP 설정 필요
                    print(f"이메일 발송 테스트: {admin.email}")
                    print(f"제목: 월간 근태 리포트")
                    print(f"내용: {email_body}")
                    success_count += 1

            logger.info(f"월간 리포트 발송 완료: {success_count}/{len(admins)}명")

    except Exception as e:
        logger.error(f"월간 리포트 발송 중 오류: {str(e)}")


def check_attendance_alerts():
    """출근 알림 체크"""
    try:
        logger.info("출근 알림 체크 시작")

        with app.app_context():
            today = date.today()
            current_time = datetime.now().time()

            # 아직 출근하지 않은 직원 체크
            users = User.query.filter(
                and_(User.role == "employee", User.deleted_at == None)
            ).all()

            for user in users:
                # 오늘 출근 기록 확인
                today_attendance = Attendance.query.filter(
                    and_(
                        Attendance.user_id == user.id,
                        extract("date", Attendance.clock_in) == today,
                    )
                ).first()

                # 출근하지 않았고, 출근 시간이 지났으면 알림
                if (
                    not today_attendance
                    and current_time > datetime.strptime("09:30", "%H:%M").time()
                ):
                    logger.info(f"출근 알림: {user.name or user.username}")
                    # 실제 알림 발송 로직 추가 가능

            logger.info("출근 알림 체크 완료")

    except Exception as e:
        logger.error(f"출근 알림 체크 중 오류: {str(e)}")


def check_leave_alerts():
    """퇴근 알림 체크"""
    try:
        logger.info("퇴근 알림 체크 시작")

        with app.app_context():
            today = date.today()
            current_time = datetime.now().time()

            # 아직 퇴근하지 않은 직원 체크
            attendances = Attendance.query.filter(
                and_(
                    extract("date", Attendance.clock_in) == today,
                    Attendance.clock_out == None,
                )
            ).all()

            for attendance in attendances:
                # 퇴근 시간이 지났으면 알림
                if current_time > datetime.strptime("18:30", "%H:%M").time():
                    user = attendance.user
                    logger.info(f"퇴근 알림: {user.name or user.username}")
                    # 실제 알림 발송 로직 추가 가능

            logger.info("퇴근 알림 체크 완료")

    except Exception as e:
        logger.error(f"퇴근 알림 체크 중 오류: {str(e)}")


def manual_weekly_report():
    """수동 주간 리포트 발송"""
    print("주간 리포트를 수동으로 발송합니다...")
    send_weekly_report()


def manual_monthly_report():
    """수동 월간 리포트 발송"""
    print("월간 리포트를 수동으로 발송합니다...")
    send_monthly_report()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="근태 관리 시스템 스케줄러")
    parser.add_argument("--weekly", action="store_true", help="주간 리포트 발송")
    parser.add_argument("--monthly", action="store_true", help="월간 리포트 발송")
    parser.add_argument(
        "--attendance-alert", action="store_true", help="출근 알림 체크"
    )
    parser.add_argument("--leave-alert", action="store_true", help="퇴근 알림 체크")

    args = parser.parse_args()

    if args.weekly:
        manual_weekly_report()
    elif args.monthly:
        manual_monthly_report()
    elif args.attendance_alert:
        check_attendance_alerts()
    elif args.leave_alert:
        check_leave_alerts()
    else:
        print("사용법:")
        print("  python scheduler_runner.py --weekly     # 주간 리포트 발송")
        print("  python scheduler_runner.py --monthly    # 월간 리포트 발송")
        print("  python scheduler_runner.py --attendance-alert  # 출근 알림 체크")
        print("  python scheduler_runner.py --leave-alert       # 퇴근 알림 체크")
