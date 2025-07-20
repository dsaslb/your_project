"""
레스토랑 특화 분석 API
레스토랑 업종에 특화된 고급 분석 기능 제공
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc, extract
from models_main import Order, Menu, Customer, Branch, Staff, Inventory
from extensions import db
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
restaurant_analytics = Blueprint('restaurant_analytics', __name__)


@restaurant_analytics.route('/api/restaurant/sales-analysis')
@login_required
def sales_analysis():
    """매출 분석 API"""
    try:
        period = request.args.get('period', 'week')
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        analysis_data = get_sales_analysis(period, user_branch or branch_id)
        return jsonify(analysis_data)

    except Exception as e:
        logger.error(f"매출 분석 오류: {str(e)}")
        return jsonify({'error': '분석 실패'}), 500


@restaurant_analytics.route('/api/restaurant/menu-performance')
@login_required
def menu_performance():
    """메뉴 성과 분석 API"""
    try:
        period = request.args.get('period', 'month')
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        performance_data = get_menu_performance(period, user_branch or branch_id)
        return jsonify(performance_data)

    except Exception as e:
        logger.error(f"메뉴 성과 분석 오류: {str(e)}")
        return jsonify({'error': '분석 실패'}), 500


@restaurant_analytics.route('/api/restaurant/customer-behavior')
@login_required
def customer_behavior():
    """고객 행동 분석 API"""
    try:
        period = request.args.get('period', 'month')
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        behavior_data = get_customer_behavior(period, user_branch or branch_id)
        return jsonify(behavior_data)

    except Exception as e:
        logger.error(f"고객 행동 분석 오류: {str(e)}")
        return jsonify({'error': '분석 실패'}), 500


@restaurant_analytics.route('/api/restaurant/operational-insights')
@login_required
def operational_insights():
    """운영 인사이트 API"""
    try:
        branch_id = request.args.get('branch_id')
        
        # 사용자 권한 확인
        if not current_user.is_authenticated:
            return jsonify({'error': '인증 필요'}), 401

        # 사용자 소속 매장 확인
        user_branch = None
        if hasattr(current_user, 'staff') and current_user.staff:
            user_branch = current_user.staff.branch_id
        
        if branch_id and user_branch and int(branch_id) != user_branch:
            return jsonify({'error': '권한 없음'}), 403

        insights_data = get_operational_insights(user_branch or branch_id)
        return jsonify(insights_data)

    except Exception as e:
        logger.error(f"운영 인사이트 오류: {str(e)}")
        return jsonify({'error': '분석 실패'}), 500


def get_sales_analysis(period: str, branch_id: int = None) -> Dict[str, Any]:
    """매출 분석 데이터 조회"""
    try:
        # 기간 설정
        end_date = datetime.utcnow().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)

        # 기본 필터
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 일별 매출 데이터
        daily_sales = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(func.date(Order.created_at)).order_by('date').all()

        # 시간대별 매출 분석
        hourly_sales = db.session.query(
            extract('hour', Order.created_at).label('hour'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(extract('hour', Order.created_at)).order_by('hour').all()

        # 요일별 매출 분석
        weekday_sales = db.session.query(
            extract('dow', Order.created_at).label('weekday'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(extract('dow', Order.created_at)).order_by('weekday').all()

        # 통계 계산
        total_revenue = sum(day.revenue for day in daily_sales)
        total_orders = sum(day.order_count for day in daily_sales)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # 성장률 계산 (이전 기간 대비)
        prev_start = start_date - (end_date - start_date)
        prev_sales = db.session.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.created_at >= prev_start,
                Order.created_at < start_date,
                *base_filter
            )
        ).scalar() or 0

        growth_rate = ((total_revenue - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0

        return {
            'period': period,
            'summary': {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'avg_order_value': round(avg_order_value, 2),
                'growth_rate': round(growth_rate, 2)
            },
            'daily_sales': [
                {
                    'date': day.date.strftime('%Y-%m-%d'),
                    'revenue': day.revenue,
                    'order_count': day.order_count,
                    'avg_order_value': round(day.avg_order_value, 2)
                }
                for day in daily_sales
            ],
            'hourly_sales': [
                {
                    'hour': int(hr.hour),
                    'revenue': hr.revenue,
                    'order_count': hr.order_count
                }
                for hr in hourly_sales
            ],
            'weekday_sales': [
                {
                    'weekday': int(wd.weekday),
                    'weekday_name': get_weekday_name(int(wd.weekday)),
                    'revenue': wd.revenue,
                    'order_count': wd.order_count
                }
                for wd in weekday_sales
            ]
        }

    except Exception as e:
        logger.error(f"매출 분석 데이터 조회 오류: {str(e)}")
        return {
            'period': period,
            'summary': {'total_revenue': 0, 'total_orders': 0, 'avg_order_value': 0, 'growth_rate': 0},
            'daily_sales': [],
            'hourly_sales': [],
            'weekday_sales': []
        }


def get_menu_performance(period: str, branch_id: int = None) -> Dict[str, Any]:
    """메뉴 성과 분석 데이터 조회"""
    try:
        # 기간 설정
        end_date = datetime.utcnow().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)

        # 기본 필터
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 메뉴별 성과 분석
        menu_performance = db.session.query(
            Menu.name,
            Menu.category,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_revenue'),
            func.avg(Order.total_amount).label('avg_revenue'),
            func.sum(Order.total_amount).label('revenue_share')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(Menu.name, Menu.category).order_by(desc('total_revenue')).all()

        # 총 매출 계산
        total_revenue = sum(menu.total_revenue for menu in menu_performance)

        # 카테고리별 분석
        category_performance = {}
        for menu in menu_performance:
            category = menu.category or '기타'
            if category not in category_performance:
                category_performance[category] = {
                    'order_count': 0,
                    'total_revenue': 0,
                    'menu_count': 0
                }
            category_performance[category]['order_count'] += menu.order_count
            category_performance[category]['total_revenue'] += menu.total_revenue
            category_performance[category]['menu_count'] += 1

        # 수익성 분석 (마진 정보가 있다면)
        profitability_analysis = analyze_menu_profitability(menu_performance)

        return {
            'period': period,
            'total_revenue': total_revenue,
            'menu_performance': [
                {
                    'name': menu.name,
                    'category': menu.category,
                    'order_count': menu.order_count,
                    'total_revenue': menu.total_revenue,
                    'avg_revenue': round(menu.avg_revenue, 2),
                    'revenue_share': round((menu.total_revenue / total_revenue * 100), 2) if total_revenue > 0 else 0
                }
                for menu in menu_performance
            ],
            'category_performance': [
                {
                    'category': category,
                    'order_count': data['order_count'],
                    'total_revenue': data['total_revenue'],
                    'menu_count': data['menu_count'],
                    'revenue_share': round((data['total_revenue'] / total_revenue * 100), 2) if total_revenue > 0 else 0
                }
                for category, data in category_performance.items()
            ],
            'profitability_analysis': profitability_analysis
        }

    except Exception as e:
        logger.error(f"메뉴 성과 분석 데이터 조회 오류: {str(e)}")
        return {
            'period': period,
            'total_revenue': 0,
            'menu_performance': [],
            'category_performance': [],
            'profitability_analysis': {}
        }


def get_customer_behavior(period: str, branch_id: int = None) -> Dict[str, Any]:
    """고객 행동 분석 데이터 조회"""
    try:
        # 기간 설정
        end_date = datetime.utcnow().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)

        # 기본 필터
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 고객별 주문 패턴 분석
        customer_patterns = db.session.query(
            Order.customer_id,
            func.count(Order.id).label('visit_count'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('avg_order_value'),
            func.min(Order.created_at).label('first_visit'),
            func.max(Order.created_at).label('last_visit')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                Order.customer_id.isnot(None),
                *base_filter
            )
        ).group_by(Order.customer_id).all()

        # RFM 분석
        rfm_analysis = analyze_rfm(customer_patterns, end_date)

        # 고객 세그먼트 분석
        customer_segments = segment_customers(customer_patterns)

        # 방문 빈도 분석
        visit_frequency = analyze_visit_frequency(customer_patterns)

        # 평균 주문 금액 분포
        order_value_distribution = analyze_order_value_distribution(customer_patterns)

        return {
            'period': period,
            'total_customers': len(customer_patterns),
            'rfm_analysis': rfm_analysis,
            'customer_segments': customer_segments,
            'visit_frequency': visit_frequency,
            'order_value_distribution': order_value_distribution,
            'customer_patterns': [
                {
                    'customer_id': pattern.customer_id,
                    'visit_count': pattern.visit_count,
                    'total_spent': pattern.total_spent,
                    'avg_order_value': round(pattern.avg_order_value, 2),
                    'first_visit': pattern.first_visit.strftime('%Y-%m-%d') if pattern.first_visit else None,
                    'last_visit': pattern.last_visit.strftime('%Y-%m-%d') if pattern.last_visit else None
                }
                for pattern in customer_patterns
            ]
        }

    except Exception as e:
        logger.error(f"고객 행동 분석 데이터 조회 오류: {str(e)}")
        return {
            'period': period,
            'total_customers': 0,
            'rfm_analysis': {},
            'customer_segments': {},
            'visit_frequency': {},
            'order_value_distribution': {},
            'customer_patterns': []
        }


def get_operational_insights(branch_id: int = None) -> Dict[str, Any]:
    """운영 인사이트 데이터 조회"""
    try:
        # 최근 30일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        # 기본 필터
        base_filter = []
        if branch_id:
            base_filter.append(Order.branch_id == branch_id)

        # 피크 시간대 분석
        peak_hours = analyze_peak_hours(start_date, end_date, base_filter)

        # 재고 최적화 인사이트
        inventory_insights = analyze_inventory_optimization(branch_id)

        # 직원 효율성 분석
        staff_efficiency = analyze_staff_efficiency(branch_id, start_date, end_date)

        # 수익성 개선 기회
        profitability_opportunities = analyze_profitability_opportunities(start_date, end_date, base_filter)

        # 고객 만족도 트렌드
        satisfaction_trends = analyze_satisfaction_trends(start_date, end_date, base_filter)

        return {
            'peak_hours': peak_hours,
            'inventory_insights': inventory_insights,
            'staff_efficiency': staff_efficiency,
            'profitability_opportunities': profitability_opportunities,
            'satisfaction_trends': satisfaction_trends,
            'recommendations': generate_recommendations(
                peak_hours, inventory_insights, staff_efficiency, 
                profitability_opportunities, satisfaction_trends
            )
        }

    except Exception as e:
        logger.error(f"운영 인사이트 데이터 조회 오류: {str(e)}")
        return {
            'peak_hours': {},
            'inventory_insights': {},
            'staff_efficiency': {},
            'profitability_opportunities': {},
            'satisfaction_trends': {},
            'recommendations': []
        }


def get_weekday_name(weekday: int) -> str:
    """요일 번호를 요일명으로 변환"""
    weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    return weekdays[weekday] if 0 <= weekday < 7 else '알 수 없음'


def analyze_menu_profitability(menu_performance: List) -> Dict[str, Any]:
    """메뉴 수익성 분석"""
    try:
        # 샘플 수익성 데이터 (실제로는 메뉴별 원가 정보가 필요)
        profitability_data = {
            'high_profit_menus': [],
            'low_profit_menus': [],
            'profit_margins': {}
        }

        for menu in menu_performance:
            # 샘플 마진 계산 (실제로는 원가 데이터 사용)
            estimated_cost = menu.total_revenue * 0.6  # 60% 원가 가정
            profit_margin = ((menu.total_revenue - estimated_cost) / menu.total_revenue * 100)
            
            profitability_data['profit_margins'][menu.name] = round(profit_margin, 2)
            
            if profit_margin > 50:
                profitability_data['high_profit_menus'].append(menu.name)
            elif profit_margin < 30:
                profitability_data['low_profit_menus'].append(menu.name)

        return profitability_data

    except Exception as e:
        logger.error(f"메뉴 수익성 분석 오류: {str(e)}")
        return {'high_profit_menus': [], 'low_profit_menus': [], 'profit_margins': {}}


def analyze_rfm(customer_patterns: List, end_date: datetime.date) -> Dict[str, Any]:
    """RFM 분석 (Recency, Frequency, Monetary)"""
    try:
        rfm_data = {
            'recency': {'high': 0, 'medium': 0, 'low': 0},
            'frequency': {'high': 0, 'medium': 0, 'low': 0},
            'monetary': {'high': 0, 'medium': 0, 'low': 0},
            'rfm_scores': []
        }

        for pattern in customer_patterns:
            # Recency 계산
            days_since_last_visit = (end_date - pattern.last_visit.date()).days
            
            # RFM 점수 계산
            r_score = 5 if days_since_last_visit <= 7 else (4 if days_since_last_visit <= 30 else 3)
            f_score = 5 if pattern.visit_count >= 10 else (4 if pattern.visit_count >= 5 else 3)
            m_score = 5 if pattern.total_spent >= 100000 else (4 if pattern.total_spent >= 50000 else 3)
            
            rfm_score = r_score + f_score + m_score
            
            rfm_data['rfm_scores'].append({
                'customer_id': pattern.customer_id,
                'r_score': r_score,
                'f_score': f_score,
                'm_score': m_score,
                'rfm_score': rfm_score
            })

        return rfm_data

    except Exception as e:
        logger.error(f"RFM 분석 오류: {str(e)}")
        return {'recency': {}, 'frequency': {}, 'monetary': {}, 'rfm_scores': []}


def segment_customers(customer_patterns: List) -> Dict[str, Any]:
    """고객 세그먼트 분석"""
    try:
        segments = {
            'vip_customers': [],
            'regular_customers': [],
            'occasional_customers': [],
            'at_risk_customers': []
        }

        for pattern in customer_patterns:
            if pattern.total_spent >= 100000 and pattern.visit_count >= 10:
                segments['vip_customers'].append(pattern.customer_id)
            elif pattern.total_spent >= 50000 and pattern.visit_count >= 5:
                segments['regular_customers'].append(pattern.customer_id)
            elif pattern.total_spent >= 20000:
                segments['occasional_customers'].append(pattern.customer_id)
            else:
                segments['at_risk_customers'].append(pattern.customer_id)

        return segments

    except Exception as e:
        logger.error(f"고객 세그먼트 분석 오류: {str(e)}")
        return {'vip_customers': [], 'regular_customers': [], 'occasional_customers': [], 'at_risk_customers': []}


def analyze_visit_frequency(customer_patterns: List) -> Dict[str, Any]:
    """방문 빈도 분석"""
    try:
        visit_counts = [pattern.visit_count for pattern in customer_patterns]
        
        return {
            'avg_visits': round(sum(visit_counts) / len(visit_counts), 2) if visit_counts else 0,
            'max_visits': max(visit_counts) if visit_counts else 0,
            'min_visits': min(visit_counts) if visit_counts else 0,
            'visit_distribution': {
                '1-2회': len([v for v in visit_counts if 1 <= v <= 2]),
                '3-5회': len([v for v in visit_counts if 3 <= v <= 5]),
                '6-10회': len([v for v in visit_counts if 6 <= v <= 10]),
                '10회 이상': len([v for v in visit_counts if v > 10])
            }
        }

    except Exception as e:
        logger.error(f"방문 빈도 분석 오류: {str(e)}")
        return {'avg_visits': 0, 'max_visits': 0, 'min_visits': 0, 'visit_distribution': {}}


def analyze_order_value_distribution(customer_patterns: List) -> Dict[str, Any]:
    """평균 주문 금액 분포 분석"""
    try:
        avg_values = [pattern.avg_order_value for pattern in customer_patterns]
        
        return {
            'avg_order_value': round(sum(avg_values) / len(avg_values), 2) if avg_values else 0,
            'max_order_value': max(avg_values) if avg_values else 0,
            'min_order_value': min(avg_values) if avg_values else 0,
            'value_distribution': {
                '1만원 미만': len([v for v in avg_values if v < 10000]),
                '1-2만원': len([v for v in avg_values if 10000 <= v < 20000]),
                '2-3만원': len([v for v in avg_values if 20000 <= v < 30000]),
                '3만원 이상': len([v for v in avg_values if v >= 30000])
            }
        }

    except Exception as e:
        logger.error(f"주문 금액 분포 분석 오류: {str(e)}")
        return {'avg_order_value': 0, 'max_order_value': 0, 'min_order_value': 0, 'value_distribution': {}}


def analyze_peak_hours(start_date: datetime.date, end_date: datetime.date, base_filter: List) -> Dict[str, Any]:
    """피크 시간대 분석"""
    try:
        hourly_data = db.session.query(
            extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(extract('hour', Order.created_at)).order_by('hour').all()

        peak_hours = []
        for hour_data in hourly_data:
            if hour_data.order_count > 10:  # 피크 시간 기준
                peak_hours.append({
                    'hour': int(hour_data.hour),
                    'order_count': hour_data.order_count,
                    'revenue': hour_data.revenue
                })

        return {
            'peak_hours': peak_hours,
            'busiest_hour': max(peak_hours, key=lambda x: x['order_count']) if peak_hours else None
        }

    except Exception as e:
        logger.error(f"피크 시간대 분석 오류: {str(e)}")
        return {'peak_hours': [], 'busiest_hour': None}


def analyze_inventory_optimization(branch_id: int = None) -> Dict[str, Any]:
    """재고 최적화 분석"""
    try:
        # 재고 부족 아이템
        low_stock_items = db.session.query(Inventory).filter(
            and_(
                Inventory.quantity <= Inventory.min_quantity,
                *(Inventory.branch_id == branch_id if branch_id else [])
            )
        ).all()

        # 재고 과잉 아이템
        overstock_items = db.session.query(Inventory).filter(
            and_(
                Inventory.quantity > Inventory.max_quantity * 1.5,
                *(Inventory.branch_id == branch_id if branch_id else [])
            )
        ).all()

        return {
            'low_stock_count': len(low_stock_items),
            'overstock_count': len(overstock_items),
            'low_stock_items': [item.item_name for item in low_stock_items],
            'overstock_items': [item.item_name for item in overstock_items]
        }

    except Exception as e:
        logger.error(f"재고 최적화 분석 오류: {str(e)}")
        return {'low_stock_count': 0, 'overstock_count': 0, 'low_stock_items': [], 'overstock_items': []}


def analyze_staff_efficiency(branch_id: int = None, start_date: datetime.date = None, end_date: datetime.date = None) -> Dict[str, Any]:
    """직원 효율성 분석"""
    try:
        # 직원별 주문 처리량
        staff_performance = db.session.query(
            Staff.id,
            Staff.position,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *(Staff.branch_id == branch_id if branch_id else [])
            )
        ).group_by(Staff.id, Staff.position).all()

        return {
            'total_staff': len(staff_performance),
            'avg_orders_per_staff': round(sum(s.order_count for s in staff_performance) / len(staff_performance), 2) if staff_performance else 0,
            'top_performers': [
                {
                    'staff_id': s.id,
                    'position': s.position,
                    'order_count': s.order_count,
                    'total_revenue': s.total_revenue
                }
                for s in sorted(staff_performance, key=lambda x: x.order_count, reverse=True)[:5]
            ]
        }

    except Exception as e:
        logger.error(f"직원 효율성 분석 오류: {str(e)}")
        return {'total_staff': 0, 'avg_orders_per_staff': 0, 'top_performers': []}


def analyze_profitability_opportunities(start_date: datetime.date, end_date: datetime.date, base_filter: List) -> Dict[str, Any]:
    """수익성 개선 기회 분석"""
    try:
        # 저수익 메뉴 식별
        low_profit_menus = db.session.query(
            Menu.name,
            func.count(Order.id).label('order_count'),
            func.avg(Order.total_amount).label('avg_price')
        ).join(Order).filter(
            and_(
                Order.created_at >= start_date,
                Order.created_at <= end_date,
                *base_filter
            )
        ).group_by(Menu.name).having(func.avg(Order.total_amount) < 15000).all()

        return {
            'low_profit_menu_count': len(low_profit_menus),
            'low_profit_menus': [
                {
                    'name': menu.name,
                    'order_count': menu.order_count,
                    'avg_price': round(menu.avg_price, 2)
                }
                for menu in low_profit_menus
            ]
        }

    except Exception as e:
        logger.error(f"수익성 개선 기회 분석 오류: {str(e)}")
        return {'low_profit_menu_count': 0, 'low_profit_menus': []}


def analyze_satisfaction_trends(start_date: datetime.date, end_date: datetime.date, base_filter: List) -> Dict[str, Any]:
    """고객 만족도 트렌드 분석"""
    try:
        # 샘플 만족도 데이터 (실제로는 리뷰/평점 데이터 사용)
        satisfaction_data = {
            'overall_satisfaction': 4.2,
            'trend': 'stable',
            'key_factors': ['음식 품질', '서비스 속도', '직원 친절도'],
            'improvement_areas': ['대기 시간', '메뉴 다양성']
        }

        return satisfaction_data

    except Exception as e:
        logger.error(f"고객 만족도 트렌드 분석 오류: {str(e)}")
        return {'overall_satisfaction': 0, 'trend': 'unknown', 'key_factors': [], 'improvement_areas': []}


def generate_recommendations(peak_hours: Dict, inventory_insights: Dict, staff_efficiency: Dict, 
                           profitability_opportunities: Dict, satisfaction_trends: Dict) -> List[str]:
    """AI 기반 추천사항 생성"""
    recommendations = []

    # 피크 시간대 기반 추천
    if peak_hours.get('busiest_hour'):
        recommendations.append(f"피크 시간대({peak_hours['busiest_hour']['hour']}시)에 직원 배치를 늘려 고객 대기 시간을 단축하세요.")

    # 재고 관리 추천
    if inventory_insights.get('low_stock_count', 0) > 0:
        recommendations.append(f"재고 부족 아이템 {inventory_insights['low_stock_count']}개에 대해 즉시 발주를 진행하세요.")

    # 직원 효율성 추천
    if staff_efficiency.get('avg_orders_per_staff', 0) < 20:
        recommendations.append("직원 교육을 통해 주문 처리 효율성을 향상시키세요.")

    # 수익성 개선 추천
    if profitability_opportunities.get('low_profit_menu_count', 0) > 0:
        recommendations.append("저수익 메뉴의 가격 정책을 재검토하거나 메뉴를 개선하세요.")

    # 고객 만족도 추천
    if satisfaction_trends.get('overall_satisfaction', 0) < 4.0:
        recommendations.append("고객 만족도 향상을 위해 서비스 품질 개선에 집중하세요.")

    return recommendations


# 블루프린트 등록
def init_app(app):
    app.register_blueprint(restaurant_analytics) 