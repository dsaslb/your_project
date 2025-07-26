"""
레스토랑 업종별 관리자 페이지
백엔드에서 업종 전체를 관리하는 관리자 페이지
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from models_main import Order, Staff, Branch, Brand
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


@restaurant_industry_admin.route('/api/admin/restaurant/industry/brands', methods=['POST'])
@login_required
def add_brand_api():
    if current_user.role not in ['admin', 'super_admin']:
        return jsonify({'error': '권한 없음'}), 403
    data = request.get_json()
    print("DEBUG POST DATA:", data) 
    name = data.get('name')
    description = data.get('description')
    manager = data.get('manager')
    # 필수값 체크
    if not name or not manager or not manager.get('name') or not manager.get('email'):
        return jsonify({'error': '필수값 누락'}), 400
    try:
        # 브랜드 생성
        new_brand = Brand(name=name, description=description)
        db.session.add(new_brand)
        db.session.commit()
        # (선택) 관리자 계정 생성 로직 추가 가능
        return jsonify({'success': True, 'brand_id': new_brand.id})
    except Exception as e:
        logger.error(f"브랜드 추가 오류: {str(e)}")
        db.session.rollback()
        return jsonify({'error': '브랜드 저장 실패', 'detail': str(e)}), 500


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


# 브랜드별 API 엔드포인트들
@restaurant_industry_admin.route('/api/admin/restaurant/brand/<int:brand_id>/stats')
@login_required
def api_brand_stats(brand_id):
    """특정 브랜드의 통계 데이터"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드별 매장 수
        total_branches = db.session.query(func.count(Branch.id)).filter(Branch.brand_id == brand_id).scalar() or 0
        active_branches = db.session.query(func.count(Branch.id)).filter(
            and_(Branch.brand_id == brand_id, Branch.is_active == True)
        ).scalar() or 0
        
        # 브랜드별 직원 수
        total_staff = db.session.query(func.count(Staff.id)).join(Branch).filter(Branch.brand_id == brand_id).scalar() or 0
        active_staff = db.session.query(func.count(Staff.id)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Staff.is_active == True)
        ).scalar() or 0
        
        # 브랜드별 오늘 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= datetime.utcnow().date())
        ).scalar() or 0
        
        # 브랜드별 월 매출
        this_month = datetime.utcnow().replace(day=1)
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).join(Branch).filter(
            and_(Branch.brand_id == brand_id, Order.created_at >= this_month)
        ).scalar() or 0
        
        stats = {
            'brand_name': brand.name,
            'total_branches': total_branches,
            'total_staff': total_staff,
            'today_revenue': today_revenue,
            'monthly_revenue': monthly_revenue,
            'active_branches': active_branches,
            'inactive_branches': total_branches - active_branches,
            'active_staff': active_staff,
            'inactive_staff': total_staff - active_staff
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"브랜드 통계 API 오류: {str(e)}")
        return jsonify({'error': '브랜드 통계 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/brand/<int:brand_id>/branches')
@login_required
def api_brand_branches(brand_id):
    """특정 브랜드의 매장 목록"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        branches = db.session.query(Branch).filter(Branch.brand_id == brand_id).all()
        branches_data = []
        
        for branch in branches:
            # 매장별 직원 수
            staff_count = db.session.query(func.count(Staff.id)).filter(Staff.branch_id == branch.id).scalar() or 0
            
            # 매장별 오늘 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.branch_id == branch.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            # 매장별 오늘 주문 수
            today_orders = db.session.query(func.count(Order.id)).filter(
                and_(Order.branch_id == branch.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            branch_data = {
                'id': branch.id,
                'name': branch.name,
                'location': branch.location,
                'status': 'active' if branch.is_active else 'inactive',
                'staff_count': staff_count,
                'today_revenue': today_revenue,
                'today_orders': today_orders,
                'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0,
                'manager_name': branch.manager_name or '미지정',
                'phone': branch.phone or '미등록'
            }
            branches_data.append(branch_data)
        
        return jsonify(branches_data)
    except Exception as e:
        logger.error(f"브랜드 매장 목록 API 오류: {str(e)}")
        return jsonify({'error': '매장 목록 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/brand/<int:brand_id>/staff')
@login_required
def api_brand_staff(brand_id):
    """특정 브랜드의 직원 목록"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        staff = db.session.query(Staff).join(Branch).filter(Branch.brand_id == brand_id).all()
        staff_data = []
        
        for employee in staff:
            # 직원별 오늘 주문 수
            today_orders = db.session.query(func.count(Order.id)).filter(
                and_(Order.staff_id == employee.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            # 직원별 오늘 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.staff_id == employee.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            staff_data.append({
                'id': employee.id,
                'name': employee.name,
                'position': employee.position,
                'branch_name': employee.branch.name,
                'brand_name': employee.branch.brand.name,
                'today_orders': today_orders,
                'today_revenue': today_revenue,
                'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0,
                'status': 'active' if employee.is_active else 'inactive',
                'phone': employee.phone or '미등록',
                'email': employee.email or '미등록'
            })
        
        return jsonify(staff_data)
    except Exception as e:
        logger.error(f"브랜드 직원 목록 API 오류: {str(e)}")
        return jsonify({'error': '직원 목록 로딩 실패'}), 500


# 매장별 API 엔드포인트들
@restaurant_industry_admin.route('/api/admin/restaurant/branch/<int:branch_id>/stats')
@login_required
def api_branch_stats(branch_id):
    """특정 매장의 통계 데이터"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        branch = Branch.query.get_or_404(branch_id)
        
        # 매장별 직원 수
        total_staff = db.session.query(func.count(Staff.id)).filter(Staff.branch_id == branch_id).scalar() or 0
        active_staff = db.session.query(func.count(Staff.id)).filter(
            and_(Staff.branch_id == branch_id, Staff.is_active == True)
        ).scalar() or 0
        
        # 매장별 오늘 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= datetime.utcnow().date())
        ).scalar() or 0
        
        # 매장별 오늘 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= datetime.utcnow().date())
        ).scalar() or 0
        
        # 매장별 월 매출
        this_month = datetime.utcnow().replace(day=1)
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.branch_id == branch_id, Order.created_at >= this_month)
        ).scalar() or 0
        
        stats = {
            'branch_name': branch.name,
            'brand_name': branch.brand.name,
            'location': branch.location,
            'total_staff': total_staff,
            'today_revenue': today_revenue,
            'today_orders': today_orders,
            'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0,
            'monthly_revenue': monthly_revenue,
            'active_staff': active_staff,
            'inactive_staff': total_staff - active_staff,
            'manager_name': branch.manager_name or '미지정',
            'phone': branch.phone or '미등록',
            'address': branch.address or '미등록'
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"매장 통계 API 오류: {str(e)}")
        return jsonify({'error': '매장 통계 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/branch/<int:branch_id>/staff')
@login_required
def api_branch_staff(branch_id):
    """특정 매장의 직원 목록"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        staff = db.session.query(Staff).filter(Staff.branch_id == branch_id).all()
        staff_data = []
        
        for employee in staff:
            # 직원별 오늘 주문 수
            today_orders = db.session.query(func.count(Order.id)).filter(
                and_(Order.staff_id == employee.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            # 직원별 오늘 매출
            today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                and_(Order.staff_id == employee.id, Order.created_at >= datetime.utcnow().date())
            ).scalar() or 0
            
            staff_data.append({
                'id': employee.id,
                'name': employee.name,
                'position': employee.position,
                'status': 'active' if employee.is_active else 'inactive',
                'today_orders': today_orders,
                'today_revenue': today_revenue,
                'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0,
                'phone': employee.phone or '미등록',
                'email': employee.email or '미등록',
                'hire_date': employee.hire_date.isoformat() if employee.hire_date else None,
                'performance_rating': getattr(employee, 'performance_rating', 4.0)
            })
        
        return jsonify(staff_data)
    except Exception as e:
        logger.error(f"매장 직원 목록 API 오류: {str(e)}")
        return jsonify({'error': '직원 목록 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/branch/<int:branch_id>/orders')
@login_required
def api_branch_orders(branch_id):
    """특정 매장의 주문 목록 (예시 데이터)"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        # 실제로는 Order 모델에서 데이터를 가져와야 함
        # 여기서는 예시 데이터를 반환
        orders_data = [
            {
                'id': 1,
                'order_number': 'ORD001',
                'customer_name': '김철수',
                'items': ['아메리카노', '카페라떼'],
                'total_amount': 8500,
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat(),
                'staff_name': '이영희'
            },
            {
                'id': 2,
                'order_number': 'ORD002',
                'customer_name': '박영희',
                'items': ['카푸치노'],
                'total_amount': 4500,
                'status': 'preparing',
                'created_at': datetime.utcnow().isoformat(),
                'staff_name': '김민수'
            }
        ]
        
        return jsonify(orders_data)
    except Exception as e:
        logger.error(f"매장 주문 목록 API 오류: {str(e)}")
        return jsonify({'error': '주문 목록 로딩 실패'}), 500


# 직원별 API 엔드포인트들
@restaurant_industry_admin.route('/api/admin/restaurant/staff/<int:staff_id>/profile')
@login_required
def api_staff_profile(staff_id):
    """특정 직원의 프로필 정보"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        staff = Staff.query.get_or_404(staff_id)
        
        profile_data = {
            'id': staff.id,
            'name': staff.name,
            'position': staff.position,
            'branch_name': staff.branch.name,
            'brand_name': staff.branch.brand.name,
            'phone': staff.phone or '미등록',
            'email': staff.email or '미등록',
            'hire_date': staff.hire_date.isoformat() if staff.hire_date else None,
            'performance_rating': getattr(staff, 'performance_rating', 4.0),
            'status': 'active' if staff.is_active else 'inactive'
        }
        
        return jsonify(profile_data)
    except Exception as e:
        logger.error(f"직원 프로필 API 오류: {str(e)}")
        return jsonify({'error': '직원 프로필 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/staff/<int:staff_id>/stats')
@login_required
def api_staff_stats(staff_id):
    """특정 직원의 통계 데이터"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        staff = Staff.query.get_or_404(staff_id)
        
        # 직원별 오늘 주문 수
        today_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= datetime.utcnow().date())
        ).scalar() or 0
        
        # 직원별 오늘 매출
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= datetime.utcnow().date())
        ).scalar() or 0
        
        # 직원별 월 주문 수
        this_month = datetime.utcnow().replace(day=1)
        monthly_orders = db.session.query(func.count(Order.id)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= this_month)
        ).scalar() or 0
        
        # 직원별 월 매출
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            and_(Order.staff_id == staff_id, Order.created_at >= this_month)
        ).scalar() or 0
        
        stats = {
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'monthly_orders': monthly_orders,
            'monthly_revenue': monthly_revenue,
            'avg_order_value': (today_revenue / today_orders) if today_orders > 0 else 0,
            'customer_satisfaction': 92.5,  # 예시 데이터
            'attendance_rate': 95.0,  # 예시 데이터
            'target_achievement': 85.0  # 예시 데이터
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"직원 통계 API 오류: {str(e)}")
        return jsonify({'error': '직원 통계 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/staff/<int:staff_id>/orders')
@login_required
def api_staff_orders(staff_id):
    """특정 직원의 주문 내역 (예시 데이터)"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        # 실제로는 Order 모델에서 데이터를 가져와야 함
        orders_data = [
            {
                'id': 1,
                'order_number': 'ORD001',
                'customer_name': '김철수',
                'items': ['아메리카노', '카페라떼'],
                'total_amount': 8500,
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat(),
                'tip_amount': 500
            },
            {
                'id': 2,
                'order_number': 'ORD002',
                'customer_name': '박영희',
                'items': ['카푸치노'],
                'total_amount': 4500,
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat(),
                'tip_amount': 300
            }
        ]
        
        return jsonify(orders_data)
    except Exception as e:
        logger.error(f"직원 주문 내역 API 오류: {str(e)}")
        return jsonify({'error': '주문 내역 로딩 실패'}), 500


@restaurant_industry_admin.route('/api/admin/restaurant/staff/<int:staff_id>/tasks')
@login_required
def api_staff_tasks(staff_id):
    """특정 직원의 업무 목록 (예시 데이터)"""
    try:
        if current_user.role not in ['admin', 'super_admin']:
            return jsonify({'error': '권한 없음'}), 403

        tasks_data = [
            {
                'id': 1,
                'title': '매장 청소',
                'description': '매장 내부 청소 및 정리',
                'status': 'completed',
                'priority': 'medium',
                'due_date': datetime.utcnow().isoformat(),
                'assigned_by': '매니저'
            },
            {
                'id': 2,
                'title': '재고 확인',
                'description': '커피 원두 재고 확인',
                'status': 'in_progress',
                'priority': 'high',
                'due_date': datetime.utcnow().isoformat(),
                'assigned_by': '매니저'
            }
        ]
        
        return jsonify(tasks_data)
    except Exception as e:
        logger.error(f"직원 업무 목록 API 오류: {str(e)}")
        return jsonify({'error': '업무 목록 로딩 실패'}), 500


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