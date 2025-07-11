from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func

from models import User, Attendance, Order, InventoryItem, Branch, db
from utils.cache_manager import cache_manager, cached

logger = logging.getLogger(__name__)

@cached("dashboard_stats", ttl=300)  # 5분 캐시
def get_dashboard_stats(branch_id: Optional[int] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
    """대시보드 통계 데이터 조회 (캐싱 적용)"""
    try:
        today = datetime.now().date()
        
        # 기본 필터 조건
        base_filter = []
        if branch_id:
            base_filter.append(User.branch_id == branch_id)
        if user_id:
            base_filter.append(User.id == user_id)
        
        # 오늘 출근한 직원 수
        today_attendance = (
            db.session.query(Attendance)
            .join(User)
            .filter(
                and_(
                    func.date(Attendance.clock_in) == today,
                    *base_filter
                )
            )
            .count()
        )
        
        # 이번 주 근무 통계
        week_start = today - timedelta(days=today.weekday())
        week_attendance = (
            db.session.query(Attendance)
            .join(User)
            .filter(
                and_(
                    func.date(Attendance.clock_in) >= week_start,
                    func.date(Attendance.clock_in) <= today,
                    *base_filter
                )
            )
            .count()
        )
        
        # 이번 달 근무 통계
        month_start = today.replace(day=1)
        month_attendance = (
            db.session.query(Attendance)
            .join(User)
            .filter(
                and_(
                    func.date(Attendance.clock_in) >= month_start,
                    func.date(Attendance.clock_in) <= today,
                    *base_filter
                )
            )
            .count()
        )
        
        # 오늘 주문 수
        today_orders = (
            db.session.query(Order)
            .filter(
                and_(
                    func.date(Order.created_at) == today,
                    *base_filter
                )
            )
            .count()
        )
        
        # 재고 부족 상품 수
        low_stock_items = (
            db.session.query(InventoryItem)
            .filter(InventoryItem.current_stock <= InventoryItem.min_stock)
            .count()
        )
        
        # 총 직원 수
        total_employees = (
            db.session.query(User)
            .filter(
                and_(
                    User.status == "approved",
                    *base_filter
                )
            )
            .count()
        )
        
        return {
            "today_attendance": today_attendance,
            "week_attendance": week_attendance,
            "month_attendance": month_attendance,
            "today_orders": today_orders,
            "low_stock_items": low_stock_items,
            "total_employees": total_employees,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"대시보드 통계 조회 오류: {str(e)}")
        return {
            "error": "통계 데이터를 불러올 수 없습니다.",
            "last_updated": datetime.now().isoformat()
        }

@cached("recent_activities", ttl=180)  # 3분 캐시
def get_recent_activities(limit: int = 10, branch_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """최근 활동 조회 (캐싱 적용)"""
    try:
        activities = []
        
        # 최근 출퇴근 기록
        query = db.session.query(Attendance).join(User)
        query = query.filter(func.date(Attendance.clock_in) >= datetime.now().date() - timedelta(days=7))
        if branch_id:
            query = query.filter(User.branch_id == branch_id)
        
        recent_attendances = query.order_by(Attendance.created_at.desc()).limit(limit).all()
        
        for attendance in recent_attendances:
            user = getattr(attendance, 'user', None)
            user_name = user.name if user and getattr(user, 'name', None) else (user.username if user else "")
            activities.append({
                "type": "attendance",
                "user": user_name,
                "action": f"{attendance.status} - {attendance.clock_in.date()}",
                "time": attendance.created_at,
                "icon": "clock"
            })
        
        # 최근 주문 기록
        query = db.session.query(Order)
        query = query.filter(Order.created_at >= datetime.now() - timedelta(days=7))
        if branch_id:
            query = query.filter(Order.store_id == branch_id)
        
        recent_orders = query.order_by(Order.created_at.desc()).limit(limit).all()
        
        for order in recent_orders:
            activities.append({
                "type": "order",
                "user": order.item or "발주",
                "action": f"발주 #{order.id} - {order.status}",
                "time": order.created_at,
                "icon": "shopping-cart"
            })
        
        # 시간순 정렬
        activities.sort(key=lambda x: x["time"], reverse=True)
        return activities[:limit]
        
    except Exception as e:
        logger.error(f"최근 활동 조회 오류: {str(e)}")
        return []

@cached("attendance_chart", ttl=600)  # 10분 캐시
def get_attendance_chart_data(days: int = 30, branch_id: Optional[int] = None) -> Dict[str, Any]:
    """출근 차트 데이터 조회 (캐싱 적용)"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 일별 출근 통계
        query = db.session.query(
            func.date(Attendance.clock_in).label('date'),
            func.count(Attendance.id).label('count')
        ).join(User)
        query = query.filter(func.date(Attendance.clock_in) >= start_date)
        query = query.filter(func.date(Attendance.clock_in) <= end_date)
        if branch_id:
            query = query.filter(User.branch_id == branch_id)
        
        daily_stats = query.group_by(func.date(Attendance.clock_in)).all()
        
        chart_data = {
            "labels": [str(stat.date) for stat in daily_stats],
            "data": [stat.count for stat in daily_stats]
        }
        
        return chart_data
        
    except Exception as e:
        logger.error(f"출근 차트 데이터 조회 오류: {str(e)}")
        return {"labels": [], "data": []}

@cached("user_stats", ttl=1800)  # 30분 캐시
def get_user_statistics(branch_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """사용자 통계 조회 (캐싱 적용)"""
    try:
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        # 이번 달 개인별 근무 통계
        query = db.session.query(
            User.id,
            User.name,
            User.username,
            func.count(Attendance.id).label('work_days'),
            func.avg(func.extract('hour', Attendance.clock_out - Attendance.clock_in)).label('avg_hours')
        ).outerjoin(Attendance, and_(
            Attendance.user_id == User.id,
            func.date(Attendance.clock_in) >= month_start,
            func.date(Attendance.clock_in) <= today
        ))
        query = query.filter(User.status == "approved")
        if branch_id:
            query = query.filter(User.branch_id == branch_id)
        
        user_stats = query.group_by(User.id, User.name, User.username).all()
        
        return [
            {
                "id": stat.id,
                "name": stat.name or stat.username,
                "work_days": stat.work_days or 0,
                "avg_hours": round(stat.avg_hours or 0, 1)
            }
            for stat in user_stats
        ]
        
    except Exception as e:
        logger.error(f"사용자 통계 조회 오류: {str(e)}")
        return []

def clear_dashboard_cache(branch_id: Optional[int] = None):
    """대시보드 캐시 무효화"""
    try:
        patterns = ["dashboard_stats", "recent_activities", "attendance_chart", "user_stats"]
        for pattern in patterns:
            cache_manager.invalidate_pattern(pattern)
        
        logger.info("대시보드 캐시가 무효화되었습니다.")
    except Exception as e:
        logger.error(f"캐시 무효화 오류: {str(e)}")

@cached("branch_list", ttl=3600)  # 1시간 캐시
def get_branch_list() -> List[Dict[str, Any]]:
    """지점 목록 조회 (캐싱 적용)"""
    try:
        branches = (
            db.session.query(Branch)
            .filter(Branch.status == "active")
            .all()
        )
        
        return [
            {
                "id": branch.id,
                "name": branch.name,
                "address": branch.address,
                "phone": branch.phone
            }
            for branch in branches
        ]
        
    except Exception as e:
        logger.error(f"지점 목록 조회 오류: {str(e)}")
        return []

def get_real_time_stats(branch_id: Optional[int] = None) -> Dict[str, Any]:
    """실시간 통계 (캐시 없음)"""
    try:
        now = datetime.now()
        today = now.date()
        
        # 현재 근무 중인 직원 수
        query = db.session.query(Attendance).join(User)
        query = query.filter(func.date(Attendance.clock_in) == today)
        query = query.filter(Attendance.clock_out.is_(None))
        if branch_id:
            query = query.filter(User.branch_id == branch_id)
        current_working = query.count()
        
        # 오늘 처리된 주문 수
        query = db.session.query(Order)
        query = query.filter(func.date(Order.created_at) == today)
        query = query.filter(Order.status.in_(["completed", "delivered"]))
        if branch_id:
            query = query.filter(Order.store_id == branch_id)
        today_processed_orders = query.count()
        
        return {
            "current_working": current_working,
            "today_processed_orders": today_processed_orders,
            "last_updated": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"실시간 통계 조회 오류: {str(e)}")
        return {
            "error": "실시간 데이터를 불러올 수 없습니다.",
            "last_updated": datetime.now().isoformat()
        }
