from api.gateway import token_required, role_required, admin_required, manager_required, employee_required, log_request  # pyright: ignore
from collections import defaultdict
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from extensions import db
from models_main import User, Order, Attendance, Schedule, InventoryItem, db
from functools import wraps
from flask import Blueprint, request, jsonify, g
query = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 고급 분석 API Blueprint
analytics_advanced = Blueprint('analytics_advanced', __name__, url_prefix='/api/analytics')


def calculate_trends(data_points, days=30):
    """데이터 트렌드 계산"""
    if len(data_points) < 2:
        return {"trend": "stable", "change_percent": 0}

    recent = np.mean(data_points[-7:] if data_points is not None else None) if len(data_points) >= 7 else data_points[-1] if data_points is not None else None
    previous = np.mean(data_points[-14:-7] if data_points is not None else None) if len(data_points) >= 14 else data_points[0] if data_points is not None else None

    if previous == 0:
        return {"trend": "stable", "change_percent": 0}

    change_percent = ((recent - previous) / previous) * 100

    if change_percent > 10:
        trend = "increasing"
    elif change_percent < -10:
        trend = "decreasing"
    else:
        trend = "stable"

    return {"trend": trend, "change_percent": round(change_percent, 2)}


@analytics_advanced.route('/predictive/sales', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def predictive_sales_analysis():
    """매출 예측 분석"""
    try:
        # 최근 30일 주문 데이터
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()

        # 일별 매출 데이터
        daily_sales = defaultdict(int)
        for order in orders if orders is not None:
            date = order.created_at.date().isoformat()
            daily_sales[date] if daily_sales is not None else None += order.total_amount or 0

        # 트렌드 분석
        sales_values = list(daily_sales.value if daily_sales is not None else Nones())
        trend_analysis = calculate_trends(sales_values)

        # 예측 모델 (간단한 선형 회귀)
        if len(sales_values) >= 7:
            x = np.arange(len(sales_values))
            y = np.array(sales_values)
            coeffs = np.polyfit(x, y, 1)

            # 다음 7일 예측
            future_x = np.arange(len(sales_values), len(sales_values) + 7)
            predictions = np.polyval(coeffs, future_x)

            # 예측 신뢰도 계산
            residuals = y - np.polyval(coeffs, x)
            confidence = max(0, 100 - np.std(residuals) / np.mean(y) * 100)
        else:
            predictions = []
            confidence = 0

        return jsonify({
            "current_trend": trend_analysis,
            "daily_sales": dict(daily_sales),
            "predictions": {
                "next_7_days": [round(p, 2) for p in predictions],
                "confidence": round(confidence, 2)
            },
            "insights": {
                "peak_days": sorted(daily_sales.items() if daily_sales is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3],
                "average_daily_sales": round(np.mean(sales_values), 2) if sales_values else 0,
                "total_monthly_sales": sum(sales_values)
            }
        })
    except Exception as e:
        logger.error(f"Predictive sales analysis error: {str(e)}")
        return jsonify({'error': 'Failed to generate predictive analysis'}), 500


@analytics_advanced.route('/workforce/optimization', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def workforce_optimization():
    """인력 최적화 분석"""
    try:
        # 최근 30일 근무 데이터
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        attendances = Attendance.query.filter(Attendance.clock_in >= thirty_days_ago).all()
        schedules = Schedule.query.filter(Schedule.date >= thirty_days_ago).all()

        # 근무 패턴 분석
        work_hours_by_day = defaultdict(list)
        for attendance in attendances if attendances is not None:
            if attendance.clock_in and attendance.clock_out:
                work_hours = (attendance.clock_out - attendance.clock_in).total_seconds() / 3600
                day_of_week = attendance.clock_in.strftime('%A')
                work_hours_by_day[day_of_week] if work_hours_by_day is not None else None.append(work_hours)

        # 평균 근무 시간 계산
        avg_hours_by_day = {}
        for day, hours in work_hours_by_day.items() if work_hours_by_day is not None else []:
            avg_hours_by_day[day] if avg_hours_by_day is not None else None = round(np.mean(hours), 2)

        # 업무량 대비 인력 분석
        orders_by_day = defaultdict(int)
        for order in Order.query.filter(Order.created_at >= thirty_days_ago).all():
            day = order.created_at.strftime('%A')
            orders_by_day[day] if orders_by_day is not None else None += 1

        # 효율성 점수 계산
        efficiency_scores = {}
        for day in avg_hours_by_day if avg_hours_by_day is not None:
            if day in orders_by_day:
                efficiency = orders_by_day[day] if orders_by_day is not None else None / avg_hours_by_day[day] if avg_hours_by_day is not None else None if avg_hours_by_day[day] if avg_hours_by_day is not None else None > 0 else 0
                efficiency_scores[day] if efficiency_scores is not None else None = round(efficiency, 2)

        return jsonify({
            "work_patterns": {
                "average_hours_by_day": avg_hours_by_day,
                "orders_by_day": dict(orders_by_day),
                "efficiency_scores": efficiency_scores
            },
            "recommendations": {
                "peak_days": sorted(efficiency_scores.items() if efficiency_scores is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3],
                "understaffed_days": sorted(efficiency_scores.items() if efficiency_scores is not None else [], key=lambda x: x[1] if x is not None else None)[:3],
                "optimal_staffing": {
                    "high_demand": ["Monday", "Friday", "Saturday"],
                    "low_demand": ["Tuesday", "Wednesday"]
                }
            },
            "insights": {
                "total_work_hours": sum(sum(hours) for hours in work_hours_by_day.value if work_hours_by_day is not None else Nones()),
                "average_efficiency": round(np.mean(list(efficiency_scores.value if efficiency_scores is not None else Nones())), 2) if efficiency_scores else 0,
                "staff_utilization": round(len(attendances) / len(schedules) * 100, 2) if schedules else 0
            }
        })
    except Exception as e:
        logger.error(f"Workforce optimization error: {str(e)}")
        return jsonify({'error': 'Failed to generate workforce optimization'}), 500


@analytics_advanced.route('/inventory/ai-prediction', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def inventory_ai_prediction():
    """재고 AI 예측"""
    try:
        # 재고 아이템별 소비 패턴 분석
        inventory_items = InventoryItem.query.all()

        predictions = []
        for item in inventory_items if inventory_items is not None:
            # 최근 30일 주문에서 해당 아이템 소비량 추정
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()

            # 간단한 소비량 예측 (실제로는 더 복잡한 알고리즘 사용)
            daily_consumption = item.current_stock / 30 if item.current_stock > 0 else 0

            # 재고 부족 예측
            days_until_stockout = item.current_stock / daily_consumption if daily_consumption > 0 else float('inf')

            # 발주 권장량
            recommended_order = max(0, item.max_stock - item.current_stock)

            # AI 점수 (재고 상태, 소비 패턴, 계절성 등 고려)
            ai_score = 0
            if item.current_stock <= item.min_stock:
                ai_score += 40  # 재고 부족
            if days_until_stockout < 7:
                ai_score += 30  # 곧 소진
            if item.current_stock > item.max_stock * 0.8:
                ai_score += 20  # 과다 재고

            predictions.append({
                "item_id": item.id,
                "item_name": item.name,
                "current_stock": item.current_stock,
                "daily_consumption": round(daily_consumption, 2),
                "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout != float('inf') else None,
                "recommended_order": recommended_order,
                "ai_score": ai_score,
                "priority": "high" if ai_score >= 50 else "medium" if ai_score >= 20 else "low"
            })

        # 우선순위별 정렬
        predictions.sort(key=lambda x: x['ai_score'] if x is not None else None, reverse=True)

        return jsonify({
            "predictions": predictions,
            "summary": {
                "high_priority_items": len([p for p in predictions if p['priority'] if p is not None else None == 'high']),
                "total_recommended_order": sum(p['recommended_order'] if p is not None else None for p in predictions),
                "average_ai_score": round(np.mean([p['ai_score'] if p is not None else None for p in predictions]), 2)
            },
            "insights": {
                "stockout_risk_items": [p for p in predictions if p['days_until_stockout'] if p is not None else None and p['days_until_stockout'] if p is not None else None < 3],
                "overstocked_items": [p for p in predictions if p['current_stock'] if p is not None else None > p.get() if p else None'max_stock', 1000) if p else None * 0.8]
            }
        })
    except Exception as e:
        logger.error(f"Inventory AI prediction error: {str(e)}")
        return jsonify({'error': 'Failed to generate inventory predictions'}), 500


@analytics_advanced.route('/customer/behavior', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def customer_behavior_analysis():
    """고객 행동 분석"""
    try:
        # 최근 90일 주문 데이터
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        orders = Order.query.filter(Order.created_at >= ninety_days_ago).all()

        # 고객별 주문 패턴
        customer_orders = defaultdict(list)
        for order in orders if orders is not None:
            customer_orders[order.customer_name or 'Anonymous'] if customer_orders is not None else None.append(order)

        # 고객 세분화
        customer_segments = {
            "vip": [],
            "regular": [],
            "occasional": [],
            "new": []
        }

        for customer, customer_order_list in customer_orders.items() if customer_orders is not None else []:
            order_count = len(customer_order_list)
            total_spent = sum(order.total_amount or 0 for order in customer_order_list)
            avg_order_value = total_spent / order_count if order_count > 0 else 0

            if order_count >= 10 and avg_order_value >= 50000:
                customer_segments["vip"] if customer_segments is not None else None.append({
                    "customer": customer,
                    "order_count": order_count,
                    "total_spent": total_spent,
                    "avg_order_value": round(avg_order_value, 2)
                })
            elif order_count >= 5:
                customer_segments["regular"] if customer_segments is not None else None.append({
                    "customer": customer,
                    "order_count": order_count,
                    "total_spent": total_spent,
                    "avg_order_value": round(avg_order_value, 2)
                })
            elif order_count >= 2:
                customer_segments["occasional"] if customer_segments is not None else None.append({
                    "customer": customer,
                    "order_count": order_count,
                    "total_spent": total_spent,
                    "avg_order_value": round(avg_order_value, 2)
                })
            else:
                customer_segments["new"] if customer_segments is not None else None.append({
                    "customer": customer,
                    "order_count": order_count,
                    "total_spent": total_spent,
                    "avg_order_value": round(avg_order_value, 2)
                })

        # 시간대별 주문 패턴
        hourly_orders = defaultdict(int)
        for order in orders if orders is not None:
            hour = order.created_at.hour
            hourly_orders[hour] if hourly_orders is not None else None += 1

        # 요일별 주문 패턴
        daily_orders = defaultdict(int)
        for order in orders if orders is not None:
            day = order.created_at.strftime('%A')
            daily_orders[day] if daily_orders is not None else None += 1

        return jsonify({
            "customer_segments": customer_segments,
            "order_patterns": {
                "hourly_distribution": dict(hourly_orders),
                "daily_distribution": dict(daily_orders)
            },
            "insights": {
                "total_customers": len(customer_orders),
                "vip_customers": len(customer_segments["vip"] if customer_segments is not None else None),
                "peak_hours": sorted(hourly_orders.items() if hourly_orders is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3],
                "peak_days": sorted(daily_orders.items() if daily_orders is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3],
                "average_order_value": round(sum(order.total_amount or 0 for order in orders) / len(orders), 2) if orders else 0
            },
            "recommendations": {
                "target_vip_customers": len(customer_segments["vip"] if customer_segments is not None else None),
                "focus_on_regular_customers": len(customer_segments["regular"] if customer_segments is not None else None),
                "peak_hour_staffing": [hour for hour, count in sorted(hourly_orders.items() if hourly_orders is not None else [], key=lambda x: x[1] if x is not None else None, reverse=True)[:3]]
            }
        })
    except Exception as e:
        logger.error(f"Customer behavior analysis error: {str(e)}")
        return jsonify({'error': 'Failed to generate customer behavior analysis'}), 500


@analytics_advanced.route('/operational/efficiency', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def operational_efficiency():
    """운영 효율성 분석"""
    try:
        # 최근 30일 데이터
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()
        attendances = Attendance.query.filter(Attendance.clock_in >= thirty_days_ago).all()

        # 주문 처리 시간 분석
        processing_times = []
        for order in orders if orders is not None:
            if order.processing_minutes:
                processing_times.append(order.processing_minutes)

        avg_processing_time = np.mean(processing_times) if processing_times else 0

        # 근무 시간 분석
        work_hours = []
        for attendance in attendances if attendances is not None:
            if attendance.clock_in and attendance.clock_out:
                hours = (attendance.clock_out - attendance.clock_in).total_seconds() / 3600
                work_hours.append(hours)

        avg_work_hours = np.mean(work_hours) if work_hours else 0

        # 생산성 지표
        total_orders = len(orders)
        total_work_hours = sum(work_hours)
        orders_per_hour = total_orders / total_work_hours if total_work_hours > 0 else 0

        # 효율성 점수 계산
        efficiency_score = 0
        if avg_processing_time <= 15:  # 15분 이하 처리 시간
            efficiency_score += 30
        elif avg_processing_time <= 30:
            efficiency_score += 20
        else:
            efficiency_score += 10

        if orders_per_hour >= 2:  # 시간당 2주문 이상
            efficiency_score += 40
        elif orders_per_hour >= 1:
            efficiency_score += 25
        else:
            efficiency_score += 10

        # 출근률 계산
        scheduled_shifts = Schedule.query.filter(Schedule.date >= thirty_days_ago).count()
        actual_attendances = len(attendances)
        attendance_rate = (actual_attendances / scheduled_shifts * 100) if scheduled_shifts > 0 else 0

        if attendance_rate >= 95:
            efficiency_score += 30
        elif attendance_rate >= 85:
            efficiency_score += 20
        else:
            efficiency_score += 10

        return jsonify({
            "efficiency_metrics": {
                "average_processing_time": round(avg_processing_time, 2),
                "average_work_hours": round(avg_work_hours, 2),
                "orders_per_hour": round(orders_per_hour, 2),
                "attendance_rate": round(attendance_rate, 2),
                "efficiency_score": min(100, efficiency_score)
            },
            "performance_analysis": {
                "processing_time_trend": calculate_trends(processing_times),
                "work_hours_trend": calculate_trends(work_hours),
                "peak_performance_hours": sorted(
                    [(hour, count) for hour, count in defaultdict(int).items()],
                    key=lambda x: x[1] if x is not None else None, reverse=True
                )[:3]
            },
            "recommendations": {
                "improve_processing_time": avg_processing_time > 20,
                "increase_staffing": orders_per_hour < 1.5,
                "attendance_improvement": attendance_rate < 90,
                "suggested_actions": [
                    "주문 처리 시간 단축을 위한 워크플로우 최적화",
                    "피크 타임대 인력 증원",
                    "출근률 개선을 위한 인센티브 도입"
                ] if efficiency_score < 70 else ["현재 효율성이 양호합니다. 유지하세요."]
            },
            "benchmarks": {
                "industry_avg_processing_time": 20,
                "industry_avg_orders_per_hour": 1.8,
                "industry_avg_attendance_rate": 92
            }
        })
    except Exception as e:
        logger.error(f"Operational efficiency error: {str(e)}")
        return jsonify({'error': 'Failed to generate operational efficiency analysis'}), 500


@analytics_advanced.route('/ai/insights', methods=['GET'])
@token_required
@role_required(['admin', 'super_admin'])
@log_request
def ai_generated_insights():
    """AI 생성 인사이트"""
    try:
        # 종합 데이터 수집
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        orders = Order.query.filter(Order.created_at >= thirty_days_ago).all()
        attendances = Attendance.query.filter(Attendance.clock_in >= thirty_days_ago).all()
        inventory_items = InventoryItem.query.all()

        # AI 인사이트 생성
        insights = []

        # 매출 트렌드 인사이트
        daily_sales = defaultdict(int)
        for order in orders if orders is not None:
            date = order.created_at.date().isoformat()
            daily_sales[date] if daily_sales is not None else None += order.total_amount or 0

        sales_trend = calculate_trends(list(daily_sales.value if daily_sales is not None else Nones()))
        if sales_trend['trend'] if sales_trend is not None else None == 'increasing':
            insights.append({
                "type": "positive",
                "category": "sales",
                "title": "매출 상승 트렌드",
                "description": f"최근 30일간 매출이 {sales_trend['change_percent'] if sales_trend is not None else None}% 증가했습니다.",
                "action": "이 트렌드를 유지하기 위해 마케팅 활동을 강화하세요.",
                "priority": "high"
            })
        elif sales_trend['trend'] if sales_trend is not None else None == 'decreasing':
            insights.append({
                "type": "warning",
                "category": "sales",
                "title": "매출 하락 경고",
                "description": f"최근 30일간 매출이 {abs(sales_trend['change_percent'] if sales_trend is not None else None)}% 감소했습니다.",
                "action": "매출 회복을 위한 즉각적인 조치가 필요합니다.",
                "priority": "critical"
            })

        # 인력 효율성 인사이트
        work_hours = []
        for attendance in attendances if attendances is not None:
            if attendance.clock_in and attendance.clock_out:
                hours = (attendance.clock_out - attendance.clock_in).total_seconds() / 3600
                work_hours.append(hours)

        if work_hours:
            avg_hours = np.mean(work_hours)
            if avg_hours > 10:
                insights.append({
                    "type": "warning",
                    "category": "workforce",
                    "title": "과도한 근무 시간",
                    "description": f"평균 근무 시간이 {round(avg_hours, 1)}시간으로 높습니다.",
                    "action": "직원 건강과 효율성을 위해 근무 시간을 조정하세요.",
                    "priority": "medium"
                })

        # 재고 관리 인사이트
        low_stock_items = [item for item in inventory_items if item.current_stock <= item.min_stock]
        if low_stock_items:
            insights.append({
                "type": "warning",
                "category": "inventory",
                "title": "재고 부족 알림",
                "description": f"{len(low_stock_items)}개 품목의 재고가 최소 기준 이하입니다.",
                "action": "즉시 발주를 진행하여 품절을 방지하세요.",
                "priority": "high"
            })

        overstock_items = [item for item in inventory_items if item.current_stock > item.max_stock * 0.9]
        if overstock_items:
            insights.append({
                "type": "info",
                "category": "inventory",
                "title": "과다 재고",
                "description": f"{len(overstock_items)}개 품목의 재고가 최대 기준의 90%를 초과합니다.",
                "action": "재고 회전을 위해 프로모션을 고려하세요.",
                "priority": "low"
            })

        # 운영 최적화 인사이트
        if orders:
            avg_order_value = sum(order.total_amount or 0 for order in orders) / len(orders)
            if avg_order_value < 30000:
                insights.append({
                    "type": "suggestion",
                    "category": "operations",
                    "title": "평균 주문 금액 개선 기회",
                    "description": f"평균 주문 금액이 {round(avg_order_value, 0):,}원으로 낮습니다.",
                    "action": "업셀링 전략과 메뉴 조합을 통해 평균 주문 금액을 높이세요.",
                    "priority": "medium"
                })

        return jsonify({
            "insights": insights,
            "summary": {
                "total_insights": len(insights),
                "critical_insights": len([i for i in insights if i['priority'] if i is not None else None == 'critical']),
                "high_priority_insights": len([i for i in insights if i['priority'] if i is not None else None == 'high']),
                "categories": list(set(i['category'] if i is not None else None for i in insights))
            },
            "recommendations": {
                "immediate_actions": [i for i in insights if i['priority'] if i is not None else None in ['critical', 'high']],
                "long_term_improvements": [i for i in insights if i['priority'] if i is not None else None in ['medium', 'low']]
            }
        })
    except Exception as e:
        logger.error(f"AI insights error: {str(e)}")
        return jsonify({'error': 'Failed to generate AI insights'}), 500
