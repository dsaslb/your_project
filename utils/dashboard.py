from datetime import date, datetime, timedelta

import pandas as pd

from models import Attendance, User


def get_dashboard_stats():
    """대시보드 통계 데이터를 반환하는 함수"""

    # --- 기본 통계 ---
    num_users = User.query.filter(
        User.deleted_at == None, User.status == "approved"
    ).count()
    num_attendance = Attendance.query.count()
    today = date.today()
    first = datetime(today.year, today.month, 1)
    last = (first + pd.offsets.MonthEnd()).to_pydatetime() + timedelta(days=1)

    # 월별 기록
    month_attendance = Attendance.query.filter(
        Attendance.clock_in >= first, Attendance.clock_in < last
    ).all()
    users = {u.id: u.username for u in User.query.filter(User.deleted_at == None)}

    # --- DataFrame 통계 ---
    data = []
    for a in month_attendance:
        data.append(
            {
                "user": users.get(a.user_id, "탈퇴"),
                "clock_in": a.clock_in,
                "clock_out": a.clock_out,
                "work_minutes": a.work_minutes,
                "status": a.status,
            }
        )
    df = pd.DataFrame(data)

    # --- 1. 월별 직원 근무시간 합계 ---
    if not df.empty:
        summary = (
            df.groupby("user")
            .agg(
                work_minutes_sum=("work_minutes", "sum"),
                late_count=("status", lambda x: (x == "지각").sum()),
                absent_count=("status", lambda x: (x == "결근").sum()),
            )
            .reset_index()
        )
        chart_labels = summary["user"].tolist()
        chart_data = summary["work_minutes_sum"].tolist()
    else:
        summary = pd.DataFrame()
        chart_labels = []
        chart_data = []

    # --- 2. 지각/결근 Top 3 랭킹 ---
    top_late = (
        summary.sort_values("late_count", ascending=False).head(3)
        if not summary.empty
        else pd.DataFrame()
    )
    top_absent = (
        summary.sort_values("absent_count", ascending=False).head(3)
        if not summary.empty
        else pd.DataFrame()
    )

    # --- 3. 최근 10개 출퇴근 이력 ---
    recent = (
        df.sort_values("clock_in", ascending=False).head(10)
        if not df.empty
        else pd.DataFrame()
    )

    # --- 4. 일자별 근무시간 트렌드(라인차트) ---
    if not df.empty:
        df["date"] = df["clock_in"].dt.date
        trend = df.groupby("date").work_minutes.sum().reset_index()
        trend_dates = trend["date"].astype(str).tolist()
        trend_data = trend["work_minutes"].tolist()
    else:
        trend_dates, trend_data = [], []

    # --- 5. 근무시간 분포(히스토그램/파이차트) ---
    if not df.empty:
        bins = [0, 240, 360, 480, 600, 1000]
        labels = ["4h 미만", "4~6h", "6~8h", "8~10h", "10h~"]
        df["work_range"] = pd.cut(df["work_minutes"], bins, right=False, labels=labels)
        range_count = df["work_range"].value_counts().reindex(labels, fill_value=0)
        dist_labels = range_count.index.tolist()
        dist_data = range_count.values.tolist()
    else:
        dist_labels, dist_data = [], []

    # --- 6. 자동 경고 (지각/결근 많은 직원) ---
    warn_users = (
        summary[(summary.late_count >= 2) | (summary.absent_count >= 1)][
            "user"
        ].tolist()
        if not summary.empty
        else []
    )

    return {
        "num_users": num_users,
        "num_attendance": num_attendance,
        "summary": summary.to_dict(orient="records"),
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "trend_dates": trend_dates,
        "trend_data": trend_data,
        "top_late": top_late.to_dict(orient="records") if not top_late.empty else [],
        "top_absent": (
            top_absent.to_dict(orient="records") if not top_absent.empty else []
        ),
        "recent": recent.to_dict(orient="records") if not recent.empty else [],
        "dist_labels": dist_labels,
        "dist_data": dist_data,
        "warn_users": warn_users,
    }


def get_warning_users():
    """경고 대상 사용자 목록을 반환"""
    stats = get_dashboard_stats()
    return stats["warn_users"]
