"""
레스토랑 계층적 대시보드 라우트
업종 > 브랜드 > 매장 > 직원 계층 구조 지원
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from models_main import Order, Staff, Branch, Menu, Inventory, Reservation, Brand
from extensions import db
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
restaurant_hierarchical = Blueprint('restaurant_hierarchical', __name__)


# ==================== 메인 대시보드 ====================

@restaurant_hierarchical.route('/restaurant/hierarchical')
@login_required
def restaurant_hierarchical_main():
    """레스토랑 계층적 메인 대시보드"""
    try:
        # 업종 전체 통계
        industry_stats = get_restaurant_industry_stats()
        
        # 브랜드별 요약
        brand_summary = get_brand_summary()
        
        return render_template(
            'restaurant/hierarchical_main.html',
            user=current_user,
            industry_stats=industry_stats,
            brand_summary=brand_summary
        )

    except Exception as e:
        logger.error(f"계층적 메인 대시보드 오류: {str(e)}")
        return render_template('error.html', error="메인 대시보드 로딩 중 오류가 발생했습니다.")


# ==================== 업종별 페이지 ====================

@restaurant_hierarchical.route('/restaurant/industry/dashboard')
@login_required
def restaurant_industry_dashboard():
    """레스토랑 업종 전체 대시보드"""
    try:
        # 업종 전체 통계
        industry_stats = get_restaurant_industry_stats()
        
        # 브랜드별 요약
        brand_summary = get_brand_summary()
        
        # 업종 트렌드
        industry_trends = get_industry_trends()
        
        return render_template(
            'restaurant/industry_dashboard.html',
            user=current_user,
            industry_stats=industry_stats,
            brand_summary=brand_summary,
            industry_trends=industry_trends
        )

    except Exception as e:
        logger.error(f"업종 대시보드 오류: {str(e)}")
        return render_template('error.html', error="업종 대시보드 로딩 중 오류가 발생했습니다.")


# ==================== 브랜드별 페이지 ====================

@restaurant_hierarchical.route('/restaurant/brand/<int:brand_id>/dashboard')
@login_required
def restaurant_brand_dashboard(brand_id):
    """브랜드별 대시보드"""
    try:
        # 브랜드 정보 확인
        brand = db.session.query(Brand).filter_by(id=brand_id).first()
        if not brand:
            return render_template('error.html', error="브랜드를 찾을 수 없습니다.")

        # 브랜드별 통계
        brand_stats = get_brand_stats(brand_id)
        
        # 브랜드 소속 매장 목록
        brand_branches = get_brand_branches(brand_id)
        
        # 브랜드 트렌드
        brand_trends = get_brand_trends(brand_id)
        
        return render_template(
            'restaurant/brand_dashboard.html',
            user=current_user,
            brand=brand,
            brand_stats=brand_stats,
            brand_branches=brand_branches,
            brand_trends=brand_trends
        )

    except Exception as e:
        logger.error(f"브랜드 대시보드 오류: {str(e)}")
        return render_template('error.html', error="브랜드 대시보드 로딩 중 오류가 발생했습니다.")


@restaurant_hierarchical.route('/api/restaurant/brand/<int:brand_id>/stats')
@login_required
def get_brand_stats_api(brand_id):
    """브랜드 통계 API"""
    try:
        stats = get_brand_stats(brand_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"브랜드 통계 API 오류: {str(e)}")
        return jsonify({'error': '통계 로딩 실패'}), 500


# ==================== 매장별 페이지 ====================

@restaurant_hierarchical.route('/restaurant/branch/<int:branch_id>/dashboard')
@login_required
def restaurant_branch_dashboard(branch_id):
    """매장별 대시보드"""
    try:
        # 매장 정보 확인
        branch = db.session.query(Branch).filter_by(id=branch_id).first()
        if not branch:
            return render_template('error.html', error="매장을 찾을 수 없습니다.")

        # 사용자 권한 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        # 관리자가 아닌 경우 자신의 매장만 접근 가능
        if current_user.role not in ['admin', 'super_admin'] and user_branch != branch_id:
            return render_template('error.html', error="해당 매장에 대한 접근 권한이 없습니다.")

        # 매장별 통계
        branch_stats = get_branch_stats(branch_id)
        
        # 매장 직원 목록
        branch_staff = get_branch_staff(branch_id)
        
        # 매장 실시간 데이터
        branch_realtime = get_branch_realtime_data(branch_id)
        
        return render_template(
            'restaurant/branch_dashboard.html',
            user=current_user,
            branch=branch,
            branch_stats=branch_stats,
            branch_staff=branch_staff,
            branch_realtime=branch_realtime
        )

    except Exception as e:
        logger.error(f"매장 대시보드 오류: {str(e)}")
        return render_template('error.html', error="매장 대시보드 로딩 중 오류가 발생했습니다.")


@restaurant_hierarchical.route('/api/restaurant/branch/<int:branch_id>/stats')
@login_required
def get_branch_stats_api(branch_id):
    """매장 통계 API"""
    try:
        # 권한 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if current_user.role not in ['admin', 'super_admin'] and user_branch != branch_id:
            return jsonify({'error': '권한 없음'}), 403

        stats = get_branch_stats(branch_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"매장 통계 API 오류: {str(e)}")
        return jsonify({'error': '통계 로딩 실패'}), 500


# ==================== 직원별 페이지 ====================

@restaurant_hierarchical.route('/restaurant/staff/<int:staff_id>/dashboard')
@login_required
def restaurant_staff_dashboard(staff_id):
    """직원별 대시보드"""
    try:
        # 직원 정보 확인
        staff = db.session.query(Staff).filter_by(id=staff_id).first()
        if not staff:
            return render_template('error.html', error="직원을 찾을 수 없습니다.")

        # 권한 확인 (본인 또는 관리자만 접근)
        if current_user.role not in ['admin', 'super_admin']:
            if hasattr(current_user, 'staff') and current_user.staff.id != staff_id:
                return render_template('error.html', error="해당 직원 정보에 대한 접근 권한이 없습니다.")

        # 직원별 통계
        staff_stats = get_staff_stats(staff_id)
        
        # 직원 스케줄
        staff_schedule = get_staff_schedule(staff_id)
        
        # 직원 성과
        staff_performance = get_staff_performance(staff_id)
        
        return render_template(
            'restaurant/staff_dashboard.html',
            user=current_user,
            staff=staff,
            staff_stats=staff_stats,
            staff_schedule=staff_schedule,
            staff_performance=staff_performance
        )

    except Exception as e:
        logger.error(f"직원 대시보드 오류: {str(e)}")
        return render_template('error.html', error="직원 대시보드 로딩 중 오류가 발생했습니다.")


@restaurant_hierarchical.route('/api/restaurant/staff/<int:staff_id>/stats')
@login_required
def get_staff_stats_api(staff_id):
    """직원 통계 API"""
    try:
        # 권한 확인
        if current_user.role not in ['admin', 'super_admin']:
            if hasattr(current_user, 'staff') and current_user.staff.id != staff_id:
                return jsonify({'error': '권한 없음'}), 403

        stats = get_staff_stats(staff_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"직원 통계 API 오류: {str(e)}")
        return jsonify({'error': '통계 로딩 실패'}), 500


# ==================== 헬퍼 함수들 ====================

def get_restaurant_industry_stats():
    """레스토랑 업종 전체 통계"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # 전체 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= today
        ).scalar() or 0

        yesterday_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.created_at >= yesterday, Order.created_at < today)
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
            'revenue_change': ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0,
            'today_orders': today_orders,
            'brand_count': brand_count,
            'branch_count': branch_count,
            'staff_count': staff_count
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

            brand_summary.append({
                'id': brand.id,
                'name': brand.name,
                'today_revenue': today_revenue,
                'branch_count': branch_count
            })

        return brand_summary

    except Exception as e:
        logger.error(f"브랜드 요약 조회 오류: {str(e)}")
        return []


def get_industry_trends():
    """업종 트렌드"""
    try:
        # 최근 7일 매출 트렌드
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)

        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(Order.created_at >= start_date, Order.created_at <= end_date)
        ).group_by(func.date(Order.created_at)).order_by('date').all()

        return {
            'daily_revenue': [
                {
                    'date': day.date.strftime('%m/%d'),
                    'revenue': day.revenue
                }
                for day in daily_revenue
            ]
        }

    except Exception as e:
        logger.error(f"업종 트렌드 조회 오류: {str(e)}")
        return {'daily_revenue': []}


def get_brand_stats(brand_id):
    """브랜드별 통계"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # 브랜드별 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= today)
        ).scalar() or 0

        yesterday_revenue = db.session.query(func.sum(Order.total_amount)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= yesterday, Order.created_at < today)
        ).scalar() or 0

        # 브랜드별 주문 수
        today_orders = db.session.query(func.count(Order.id)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= today)
        ).scalar() or 0

        # 브랜드별 매장 수
        branch_count = db.session.query(func.count(Branch.id)).filter(
            Branch.brand_id == brand_id
        ).scalar() or 0

        return {
            'today_revenue': today_revenue,
            'yesterday_revenue': yesterday_revenue,
            'revenue_change': ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0,
            'today_orders': today_orders,
            'branch_count': branch_count
        }

    except Exception as e:
        logger.error(f"브랜드 통계 조회 오류: {str(e)}")
        return {}


def get_brand_branches(brand_id):
    """브랜드 소속 매장 목록"""
    try:
        branches = db.session.query(Branch).filter(Branch.brand_id == brand_id).all()
        
        branch_list = []
        for branch in branches:
            # 매장별 오늘 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.branch_id == branch.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0

            branch_list.append({
                'id': branch.id,
                'name': branch.name,
                'location': branch.location,
                'today_revenue': today_revenue
            })

        return branch_list

    except Exception as e:
        logger.error(f"브랜드 매장 목록 조회 오류: {str(e)}")
        return []


def get_brand_trends(brand_id):
    """브랜드 트렌드"""
    try:
        # 최근 7일 브랜드별 매출 트렌드
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)

        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= start_date, Order.created_at <= end_date)
        ).group_by(func.date(Order.created_at)).order_by('date').all()

        return {
            'daily_revenue': [
                {
                    'date': day.date.strftime('%m/%d'),
                    'revenue': day.revenue
                }
                for day in daily_revenue
            ]
        }

    except Exception as e:
        logger.error(f"브랜드 트렌드 조회 오류: {str(e)}")
        return {'daily_revenue': []}


def get_branch_stats(branch_id):
    """매장별 통계"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # 매장별 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= today)
        ).scalar() or 0

        yesterday_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= yesterday, Order.created_at < today)
        ).scalar() or 0

        # 매장별 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= today)
        ).scalar() or 0

        # 매장별 직원 수
        staff_count = db.session.query(func.count(Staff.id)).filter(
            and_(Staff.branch_id == branch_id, Staff.is_active == True)
        ).scalar() or 0

        return {
            'today_revenue': today_revenue,
            'yesterday_revenue': yesterday_revenue,
            'revenue_change': ((today_revenue - yesterday_revenue) / yesterday_revenue * 100) if yesterday_revenue > 0 else 0,
            'today_orders': today_orders,
            'staff_count': staff_count
        }

    except Exception as e:
        logger.error(f"매장 통계 조회 오류: {str(e)}")
        return {}


def get_branch_staff(branch_id):
    """매장 직원 목록"""
    try:
        staff_members = db.session.query(Staff).filter(
            and_(Staff.branch_id == branch_id, Staff.is_active == True)
        ).all()
        
        staff_list = []
        for staff in staff_members:
            staff_list.append({
                'id': staff.id,
                'name': staff.user.username if staff.user else 'Unknown',
                'position': staff.position,
                'status': '근무중' if staff.is_active else '휴식'
            })

        return staff_list

    except Exception as e:
        logger.error(f"매장 직원 목록 조회 오류: {str(e)}")
        return []


def get_branch_realtime_data(branch_id):
    """매장 실시간 데이터"""
    try:
        # 최근 주문 (30분)
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        
        recent_orders = db.session.query(Order).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= thirty_minutes_ago)
        ).order_by(desc(Order.created_at)).limit(5).all()

        # 재고 부족 아이템
        low_stock_items = db.session.query(Inventory).filter(
            and_(Inventory.branch_id == branch_id, Inventory.quantity <= Inventory.min_quantity)
        ).limit(5).all()

        return {
            'recent_orders': [
                {
                    'id': order.id,
                    'order_number': f"#{order.id:04d}",
                    'total_amount': order.total_amount,
                    'status': order.status,
                    'time_ago': get_time_ago(order.created_at)
                }
                for order in recent_orders
            ],
            'low_stock_items': [
                {
                    'id': inv.id,
                    'item_name': inv.item_name,
                    'quantity': inv.quantity,
                    'min_quantity': inv.min_quantity
                }
                for inv in low_stock_items
            ]
        }

    except Exception as e:
        logger.error(f"매장 실시간 데이터 조회 오류: {str(e)}")
        return {'recent_orders': [], 'low_stock_items': []}


def get_staff_stats(staff_id):
    """직원별 통계"""
    try:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        # 직원별 처리 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= today)
        ).scalar() or 0

        yesterday_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= yesterday, Order.created_at < today)
        ).scalar() or 0

        # 직원별 매출 기여도
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= today)
        ).scalar() or 0

        return {
            'today_orders': today_orders,
            'yesterday_orders': yesterday_orders,
            'order_change': ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0,
            'today_revenue': today_revenue
        }

    except Exception as e:
        logger.error(f"직원 통계 조회 오류: {str(e)}")
        return {}


def get_staff_schedule(staff_id):
    """직원 스케줄"""
    try:
        # 실제 구현에서는 Schedule 모델 사용
        # 여기서는 샘플 데이터 반환
        return {
            'today': [
                {'time': '09:00-17:00', 'type': '근무'},
                {'time': '12:00-13:00', 'type': '휴식'}
            ],
            'tomorrow': [
                {'time': '17:00-01:00', 'type': '근무'},
                {'time': '20:00-21:00', 'type': '휴식'}
            ]
        }

    except Exception as e:
        logger.error(f"직원 스케줄 조회 오류: {str(e)}")
        return {}


def get_staff_performance(staff_id):
    """직원 성과"""
    try:
        # 최근 30일 성과
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        # 처리 주문 수
        total_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= start_date)
        ).scalar() or 0

        # 평균 주문 처리 시간 (샘플)
        avg_processing_time = 15.5

        # 고객 만족도 (샘플)
        customer_satisfaction = 4.2

        return {
            'total_orders': total_orders,
            'avg_processing_time': avg_processing_time,
            'customer_satisfaction': customer_satisfaction
        }

    except Exception as e:
        logger.error(f"직원 성과 조회 오류: {str(e)}")
        return {}


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
    app.register_blueprint(restaurant_hierarchical) 