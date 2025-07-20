"""
레스토랑 업종별 관리자 페이지
백엔드에서 업종 전체를 관리하는 관리자 페이지
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from models_main import Order, Staff, Branch, Menu, Inventory, Reservation, Brand
from extensions import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
restaurant_industry_admin = Blueprint('restaurant_industry_admin', __name__)


@restaurant_industry_admin.route('/admin/restaurant/industry')
@login_required
def restaurant_industry_admin_dashboard():
    """레스토랑 업종 관리자 대시보드"""
    try:
        # 관리자 권한 확인
        if current_user.role not in ['admin', 'super_admin']:
            return render_template('error.html', error="관리자 권한이 필요합니다.")

        # 업종 전체 통계
        industry_stats = get_industry_overview_stats()
        
        # 브랜드별 요약
        brand_summary = get_brand_summary()
        
        # 매장별 요약
        branch_summary = get_branch_summary()
        
        # 직원별 요약
        staff_summary = get_staff_summary()
        
        # 최근 활동
        recent_activities = get_recent_activities()
        
        return render_template(
            'admin/restaurant_industry_admin.html',
            user=current_user,
            industry_stats=industry_stats,
            brand_summary=brand_summary,
            branch_summary=branch_summary,
            staff_summary=staff_summary,
            recent_activities=recent_activities
        )

    except Exception as e:
        logger.error(f"업종 관리자 대시보드 오류: {str(e)}")
        return render_template('error.html', error="업종 관리자 대시보드 로딩 중 오류가 발생했습니다.")


@restaurant_industry_admin.route('/api/admin/restaurant/industry/stats')
@login_required
def get_industry_stats_api():
    """업종 통계 API"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        stats = get_industry_overview_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"업종 통계 API 오류: {str(e)}")
        return jsonify({'error': '통계 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/industry/brands')
@login_required
def get_brands_api():
    """브랜드 목록 API"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        brands = get_brand_summary()
        return jsonify(brands)
    except Exception as e:
        logger.error(f"브랜드 목록 API 오류: {str(e)}")
        return jsonify({'error': '브랜드 목록 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/industry/branches')
@login_required
def get_branches_api():
    """매장 목록 API"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        branches = get_branch_summary()
        return jsonify(branches)
    except Exception as e:
        logger.error(f"매장 목록 API 오류: {str(e)}")
        return jsonify({'error': '매장 목록 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/industry/staff')
@login_required
def get_staff_api():
    """직원 목록 API"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        staff = get_staff_summary()
        return jsonify(staff)
    except Exception as e:
        logger.error(f"직원 목록 API 오류: {str(e)}")
        return jsonify({'error': '직원 목록 로딩 실패'}), 500


# ==================== 헬퍼 함수들 ====================

def get_industry_overview_stats():
    """업종 전체 통계"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        this_month = today.replace(day=1)

        # 전체 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= today
        ).scalar() or 0

        yesterday_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.created_at >= yesterday, Order.created_at < today)
        ).scalar() or 0

        this_month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= this_month
        ).scalar() or 0

        # 전체 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            Order.created_at >= today
        ).scalar() or 0

        # 브랜드 수
        brand_count = db.session.query(func.count(Brand.id)).scalar() or 0

        # 매장 수
        branch_count = db.session.query(func.count(Branch.id)).scalar() or 0

        # 직원 수
        staff_count = db.session.query(func.count(Staff.id)).filter(
            Staff.is_active == True
        ).scalar() or 0

        return {
            'today_revenue': today_revenue,
            'yesterday_revenue': yesterday_revenue,
            'this_month_revenue': this_month_revenue,
            'revenue_change': ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0,
            'today_orders': today_orders,
            'brand_count': brand_count,
            'branch_count': branch_count,
            'staff_count': staff_count,
            'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0
        }

    except Exception as e:
        logger.error(f"업종 통계 조회 오류: {str(e)}")
        return {}


def get_brand_summary():
    """브랜드별 요약 정보"""
    try:
        brands = db.session.query(Brand).all()
        
        brand_summary = []
        for brand in brands:
            # 브랜드별 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).join(Branch).filter(
                and_(Branch.brand_id == brand.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            # 브랜드별 매장 수
            branch_count = db.session.query(func.count(Branch.id)).filter(
                Branch.brand_id == brand.id
            ).scalar() or 0

            # 브랜드별 직원 수
            staff_count = db.session.query(func.count(Staff.id)).join(Branch).filter(
                and_(Branch.brand_id == brand.id, Staff.is_active == True)
            ).scalar() or 0

            brand_summary.append({
                'id': brand.id,
                'name': brand.name,
                'today_revenue': today_revenue,
                'branch_count': branch_count,
                'staff_count': staff_count,
                'avg_revenue_per_branch': (today_revenue / branch_count) if branch_count > 0 else 0
            })

        return brand_summary

    except Exception as e:
        logger.error(f"브랜드 요약 조회 오류: {str(e)}")
        return []


def get_branch_summary():
    """매장별 요약 정보"""
    try:
        branches = db.session.query(Branch).all()
        
        branch_summary = []
        for branch in branches:
            # 매장별 오늘 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.branch_id == branch.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            # 매장별 직원 수
            staff_count = db.session.query(func.count(Staff.id)).filter(
                and_(Staff.branch_id == branch.id, Staff.is_active == True)
            ).scalar() or 0

            # 매장별 오늘 주문 수
            today_orders = db.session.query(func.count(Order.id)).filter(
                and_(Order.branch_id == branch.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            branch_summary.append({
                'id': branch.id,
                'name': branch.name,
                'brand_name': branch.brand.name if branch.brand else 'Unknown',
                'location': branch.location,
                'today_revenue': today_revenue,
                'staff_count': staff_count,
                'today_orders': today_orders,
                'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0
            })

        return branch_summary

    except Exception as e:
        logger.error(f"매장 요약 조회 오류: {str(e)}")
        return []


def get_staff_summary():
    """직원별 요약 정보"""
    try:
        staff_members = db.session.query(Staff).filter(Staff.is_active == True).all()
        
        staff_summary = []
        for staff in staff_members:
            # 직원별 오늘 처리 주문 수
            today_orders = db.session.query(func.count(Order.id)).filter(
                and_(Order.staff_id == staff.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            # 직원별 오늘 매출 기여도
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.staff_id == staff.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            staff_summary.append({
                'id': staff.id,
                'name': staff.user.username if staff.user else 'Unknown',
                'position': staff.position,
                'branch_name': staff.branch.name if staff.branch else 'Unknown',
                'brand_name': staff.branch.brand.name if staff.branch and staff.branch.brand else 'Unknown',
                'today_orders': today_orders,
                'today_revenue': today_revenue,
                'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0
            })

        return staff_summary

    except Exception as e:
        logger.error(f"직원 요약 조회 오류: {str(e)}")
        return []


def get_recent_activities():
    """최근 활동"""
    try:
        # 최근 주문
        recent_orders = db.session.query(Order).order_by(desc(Order.created_at)).limit(5).all()
        
        activities = []
        for order in recent_orders:
            activities.append({
                'type': 'order',
                'message': f"#{order.id:04d} 주문 접수 - {order.branch.name if order.branch else 'Unknown'}",
                'amount': order.total_amount,
                'time': get_time_ago(order.created_at)
            })

        # 최근 직원 활동 (샘플)
        activities.append({
            'type': 'staff',
            'message': "김서버가 강남점에서 근무 시작",
            'amount': 0,
            'time': '5분 전'
        })

        activities.append({
            'type': 'inventory',
            'message': "홍대점에서 토마토 소스 재고 부족 알림",
            'amount': 0,
            'time': '10분 전'
        })

        return activities

    except Exception as e:
        logger.error(f"최근 활동 조회 오류: {str(e)}")
        return []


def get_time_ago(datetime_obj):
    """시간 경과 계산"""
    try:
        now = datetime.utcnow()
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    except:
        return "시간 정보 없음"


# 블루프린트 등록
def init_app(app):
    app.register_blueprint(restaurant_industry_admin) 