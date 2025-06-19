"""
급여 계산 유틸리티
"""

def calc_wage(user, work_time_hour, wage_table=None):
    """
    사용자별 급여 계산
    
    Args:
        user: User 객체
        work_time_hour: 근무 시간 (시간 단위)
        wage_table: 사용자별 시급 테이블 (dict {user_id: 시급})
    
    Returns:
        int: 계산된 급여 (원)
    """
    # 기본 시급
    wage_per_hour = 12000
    
    # 사용자별 급여 정책 적용
    if wage_table and user.id in wage_table:
        wage_per_hour = wage_table[user.id]
    
    # 월급제/시급제/주급제 분기 가능
    # 현재는 시급제로 계산
    return int(work_time_hour * wage_per_hour)

def calc_overtime_pay(work_time_hour, base_wage_per_hour=12000):
    """
    초과근무 수당 계산
    
    Args:
        work_time_hour: 근무 시간 (시간 단위)
        base_wage_per_hour: 기본 시급
    
    Returns:
        tuple: (기본급여, 초과수당, 총급여)
    """
    standard_hours = 8  # 기준 근무시간
    overtime_rate = 1.5  # 초과수당 배율
    
    if work_time_hour <= standard_hours:
        base_pay = work_time_hour * base_wage_per_hour
        overtime_pay = 0
    else:
        base_pay = standard_hours * base_wage_per_hour
        overtime_hours = work_time_hour - standard_hours
        overtime_pay = overtime_hours * base_wage_per_hour * overtime_rate
    
    total_pay = base_pay + overtime_pay
    return int(base_pay), int(overtime_pay), int(total_pay)

def format_work_time(total_minutes):
    """
    근무시간을 시간:분 형식으로 포맷팅
    
    Args:
        total_minutes: 총 근무시간 (분)
    
    Returns:
        str: "X시간 Y분" 형식
    """
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}시간 {minutes}분"

def get_monthly_stats(user_id, year, month, db_session):
    """
    사용자의 월별 근무 통계 조회
    
    Args:
        user_id: 사용자 ID
        year: 년도
        month: 월
        db_session: 데이터베이스 세션
    
    Returns:
        dict: 월별 통계 정보
    """
    from sqlalchemy import extract, func
    from models import Attendance
    
    # 해당 월의 출퇴근 기록 조회
    attendances = db_session.query(Attendance).filter(
        Attendance.user_id == user_id,
        extract('year', Attendance.clock_in) == year,
        extract('month', Attendance.clock_in) == month
    ).all()
    
    total_days = len(attendances)
    total_minutes = sum(att.work_minutes for att in attendances)
    total_hours = total_minutes / 60
    
    # 지각/조퇴/결근 통계
    late_count = sum(1 for att in attendances if "지각" in att.status)
    early_leave_count = sum(1 for att in attendances if "조퇴" in att.status)
    absent_count = sum(1 for att in attendances if att.status == "결근")
    
    return {
        'total_days': total_days,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'late_count': late_count,
        'early_leave_count': early_leave_count,
        'absent_count': absent_count,
        'work_time_formatted': format_work_time(total_minutes)
    } 