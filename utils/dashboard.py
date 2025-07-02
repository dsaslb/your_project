from datetime import date, datetime, timedelta
import logging
from typing import Dict, List, Optional

import pandas as pd

from sqlalchemy import and_, func

from extensions import db
from models import Attendance, User
from utils.logger import log_action

logger = logging.getLogger(__name__)


def get_dashboard_stats():
    """대시보드 통계 데이터를 반환하는 함수"""
    try:
        today = datetime.now().date()
        
        # 전체 사용자 수
        total_users = User.query.filter_by(status="approved").count()
        
        # 오늘 출근한 직원 수
        today_attendance = (
            db.session.query(Attendance)
            .filter(
                and_(
                    Attendance.date == today,
                    Attendance.status.in_(["present", "late"])
                )
            )
            .count()
        )
        
        # 이번 주 근무 통계
        week_start = today - timedelta(days=today.weekday())
        week_attendance = (
            db.session.query(Attendance)
            .filter(
                and_(
                    Attendance.date >= week_start,
                    Attendance.date <= today,
                    Attendance.status.in_(["present", "late"])
                )
            )
            .count()
        )
        
        # 이번 달 근무 통계
        month_start = today.replace(day=1)
        month_attendance = (
            db.session.query(Attendance)
            .filter(
                and_(
                    Attendance.date >= month_start,
                    Attendance.date <= today,
                    Attendance.status.in_(["present", "late"])
                )
            )
            .count()
        )
        
        stats = {
            "total_users": total_users,
            "today_attendance": today_attendance,
            "week_attendance": week_attendance,
            "month_attendance": month_attendance,
            "attendance_rate": round((today_attendance / total_users * 100), 1) if total_users > 0 else 0
        }
        
        logger.info(f"대시보드 통계 조회 완료: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"대시보드 통계 조회 실패: {e}")
        return {}


def get_warning_users():
    """경고 대상 사용자 목록을 반환"""
    stats = get_dashboard_stats()
    return stats["warn_users"]


def get_recent_activities(limit=10):
    """최근 활동 조회"""
    try:
        # 최근 근태 기록
        recent_attendances = (
            db.session.query(Attendance)
            .join(User)
            .filter(Attendance.date >= datetime.now().date() - timedelta(days=7))
            .order_by(Attendance.created_at.desc())
            .limit(limit)
            .all()
        )
        
        activities = []
        for attendance in recent_attendances:
            activities.append({
                "type": "attendance",
                "user": attendance.user.name or attendance.user.username,
                "action": f"{attendance.status} - {attendance.date}",
                "time": attendance.created_at
            })
        
        logger.info(f"최근 활동 조회 완료: {len(activities)}건")
        return activities
        
    except Exception as e:
        logger.error(f"최근 활동 조회 실패: {e}")
        return []


def get_attendance_chart_data(days=30):
    """근태 차트 데이터 조회"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 일별 출근 통계
        daily_stats = (
            db.session.query(
                Attendance.date,
                func.count(Attendance.id).label('count')
            )
            .filter(
                and_(
                    Attendance.date >= start_date,
                    Attendance.date <= end_date,
                    Attendance.status.in_(["present", "late"])
                )
            )
            .group_by(Attendance.date)
            .all()
        )
        
        chart_data = {
            "labels": [str(stat.date) for stat in daily_stats],
            "data": [stat.count for stat in daily_stats]
        }
        
        logger.info(f"근태 차트 데이터 조회 완료: {days}일")
        return chart_data
        
    except Exception as e:
        logger.error(f"근태 차트 데이터 조회 실패: {e}")
        return {"labels": [], "data": []}


def get_user_performance_stats():
    """사용자 성과 통계"""
    try:
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        # 이번 달 개인별 근무 통계
        user_stats = (
            db.session.query(
                User.id,
                User.name,
                User.username,
                func.count(Attendance.id).label('work_days'),
                func.avg(Attendance.overtime_hours).label('avg_overtime')
            )
            .outerjoin(Attendance, and_(
                Attendance.user_id == User.id,
                Attendance.date >= month_start,
                Attendance.date <= today,
                Attendance.status.in_(["present", "late"])
            ))
            .filter(User.status == "approved")
            .group_by(User.id, User.name, User.username)
            .all()
        )
        
        performance_data = []
        for stat in user_stats:
            performance_data.append({
                "user_id": stat.id,
                "name": stat.name or stat.username,
                "work_days": stat.work_days or 0,
                "avg_overtime": round(stat.avg_overtime or 0, 1)
            })
        
        logger.info(f"사용자 성과 통계 조회 완료: {len(performance_data)}명")
        return performance_data
        
    except Exception as e:
        logger.error(f"사용자 성과 통계 조회 실패: {e}")
        return []
