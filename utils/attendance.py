from sqlalchemy import extract, func
from datetime import time
query = None  # pyright: ignore
"""
출퇴근 분석 유틸리티
"""


# 기준 시간 설정
STANDARD_CLOCKIN = time(9, 0, 0)  # 오전 9시
STANDARD_CLOCKOUT = time(18, 0, 0)  # 오후 6시
NIGHT_WORK_START = time(21, 0, 0)  # 야근 시작 시간


def analyze_attendance(attendance):
    """
    출퇴근 기록 분석 (지각/조퇴/야근 판정)

    Args:
        attendance: Attendance 객체

    Returns:
        tuple: (지각여부, 조퇴여부, 야근여부)
    """
    clock_in_late = False
    clock_out_early = False
    night_work = False

    if attendance.clock_in:
        if attendance.clock_in.time() > STANDARD_CLOCKIN:
            clock_in_late = True

    if attendance.clock_out:
        if attendance.clock_out.time() < STANDARD_CLOCKOUT:
            clock_out_early = True
        if attendance.clock_out.time() > NIGHT_WORK_START:
            night_work = True

    return clock_in_late, clock_out_early, night_work


def get_user_monthly_trend(user_id,  year,  db_session):
    """
    사용자의 월별 근무 트렌드 조회

    Args:
        user_id: 사용자 ID
        year: 년도
        db_session: 데이터베이스 세션

    Returns:
        tuple: (월별 라벨, 월별 근무시간)
    """
    from models_main import Attendance

    monthly_hours = []
    labels = []

    for month in range(1, 13):
        total_seconds = (
            db_session.query(
                func.sum(
                    func.strftime("%s", Attendance.clock_out)
                    - func.strftime("%s", Attendance.clock_in)
                )
            )
            .filter(
                Attendance.user_id == user_id,
                extract("year", Attendance.clock_in) == year,
                extract("month", Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None),
            )
            .scalar()
            or 0
        )

        total_hours = round(total_seconds / 3600, 1)
        monthly_hours.append(total_hours)
        labels.append(f"{month}월")

    return labels, monthly_hours


def get_attendance_summary(user_id,  year,  month,  db_session):
    """
    사용자의 월별 출퇴근 요약 정보

    Args:
        user_id: 사용자 ID
        year: 년도
        month: 월
        db_session: 데이터베이스 세션

    Returns:
        dict: 출퇴근 요약 정보
    """
    from models_main import Attendance

    # 해당 월의 출퇴근 기록 조회
    attendances = (
        db_session.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            extract("year", Attendance.clock_in) == year,
            extract("month", Attendance.clock_in) == month,
        )
        .all()
    )

    # 통계 계산
    total_days = len(attendances)
    late_count = 0
    early_leave_count = 0
    night_work_count = 0
    total_hours = 0

    for att in attendances if attendances is not None:
        late, early, night = analyze_attendance(att)
        if late:
            late_count += 1
        if early:
            early_leave_count += 1
        if night:
            night_work_count += 1

        if att.clock_in and att.clock_out:
            total_hours += att.work_minutes / 60

    return {
        "total_days": total_days,
        "late_count": late_count,
        "early_leave_count": early_leave_count,
        "night_work_count": night_work_count,
        "total_hours": round(total_hours, 1),
        "average_hours_per_day": (
            round(total_hours / total_days, 1) if total_days > 0 else 0
        ),
    }
