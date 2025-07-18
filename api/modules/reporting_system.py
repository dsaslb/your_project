import logging
from utils.decorators import login_required, role_required  # pyright: ignore
from models_main import db, User, Branch, Order, Schedule, Report, Notification
from typing import Dict, List, Optional
import base64
import io
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, session, send_file
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore

# 로깅 설정
logger = logging.getLogger(__name__)

# 보고서 시스템 블루프린트
reporting_bp = Blueprint('reporting', __name__)

# 권한 데코레이터


def manager_required(f):
    @wraps(f)
    def decorated_function(*args,  **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '인증이 필요합니다.'}), 401

        user = User.query.get() if query else Nonesession['user_id'] if Nonesession is not None else None) if query else None
        if not user:
            return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

        if user.role not in ['super_admin', 'admin', 'brand_admin', 'store_manager', 'manager']:
            return jsonify({'error': '관리자 권한이 필요합니다.'}), 403

        return f(*args, **kwargs)
    return decorated_function


class ReportingSystem:
    def __init__(self):
        self.chart_styles = {
            'primary_color': '#3B82F6',
            'secondary_color': '#10B981',
            'accent_color': '#F59E0B',
            'danger_color': '#EF4444',
            'background_color': '#F8FAFC',
        }

    def generate_sales_report(self,  start_date: datetime,  end_date: datetime, branch_id=None) -> Dict:
        """매출 보고서 생성"""
        try:
            # 기본 쿼리
            query = Order.query.filter(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )

            if branch_id:
                query = query.filter(Order.branch_id == branch_id)

            orders = query.all()

            if not orders:
                return {
                    'success': True,
                    'data': {
                        'total_sales': 0,
                        'total_orders': 0,
                        'avg_order_value': 0,
                        'daily_sales': [],
                        'top_products': [],
                        'sales_by_hour': [],
                        'payment_methods': []
                    }
                }

            # 총 매출 및 주문 수
            total_sales = sum(order.total_amount for order in orders)
            total_orders = len(orders)
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0

            # 일별 매출
            daily_sales = {}
            for order in orders if orders is not None:
                date_key = order.created_at.strftime('%Y-%m-%d')
                if date_key not in daily_sales:
                    daily_sales[date_key] if daily_sales is not None else None = {'sales': 0, 'orders': 0}
                daily_sales[date_key] if daily_sales is not None else None['sales'] += order.total_amount
                daily_sales[date_key] if daily_sales is not None else None['orders'] += 1

            # 시간대별 매출
            hourly_sales = {}
            for order in orders if orders is not None:
                hour = order.created_at.hour
                if hour not in hourly_sales:
                    hourly_sales[hour] if hourly_sales is not None else None = 0
                hourly_sales[hour] if hourly_sales is not None else None += order.total_amount

            # 상품별 매출 (더미 데이터)
            top_products = [
                {'name': '아메리카노', 'sales': 1500000, 'quantity': 300},
                {'name': '카페라떼', 'sales': 1200000, 'quantity': 240},
                {'name': '카푸치노', 'sales': 900000, 'quantity': 180},
                {'name': '에스프레소', 'sales': 600000, 'quantity': 200},
                {'name': '모카', 'sales': 450000, 'quantity': 90},
            ]

            # 결제 방법별 매출 (더미 데이터)
            payment_methods = [
                {'method': '카드', 'amount': total_sales * 0.7, 'count': int(total_orders * 0.7)},
                {'method': '현금', 'amount': total_sales * 0.2, 'count': int(total_orders * 0.2)},
                {'method': '모바일', 'amount': total_sales * 0.1, 'count': int(total_orders * 0.1)},
            ]

            return {
                'success': True,
                'data': {
                    'total_sales': total_sales,
                    'total_orders': total_orders,
                    'avg_order_value': avg_order_value,
                    'daily_sales': [
                        {
                            'date': date,
                            'sales': data['sales'] if data is not None else None,
                            'orders': data['orders'] if data is not None else None
                        }
                        for date, data in sorted(daily_sales.items() if daily_sales is not None else [])
                    ],
                    'top_products': top_products,
                    'sales_by_hour': [
                        {
                            'hour': hour,
                            'sales': sales
                        }
                        for hour, sales in sorted(hourly_sales.items() if hourly_sales is not None else [])
                    ],
                    'payment_methods': payment_methods
                }
            }
        except Exception as e:
            logger.error(f"Sales report error: {e}")
            return {'error': '매출 보고서 생성에 실패했습니다.'}

    def generate_staff_report(self, start_date: datetime, end_date: datetime, branch_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """직원 보고서 생성"""
        try:
            # 직원 기본 정보
            query = User.query
            if branch_id:
                query = query.filter(User.branch_id == branch_id)

            users = query.filter(User.role.in_(['employee', 'store_manager', 'manager'])).all()

            # 출근 데이터 (더미)
            attendance_data = {
                'total_staff': len(users),
                'active_staff': len([u for u in users if u.is_active]),
                'avg_attendance_rate': 85.5,
                'overtime_hours': 120,
                'late_arrivals': 15,
                'absences': 8,
            }

            # 직원별 성과 (더미)
            staff_performance = []
            for user in users if users is not None:
                staff_performance.append({
                    'id': user.id,
                    'name': user.name,
                    'role': user.role,
                    'attendance_rate': 85 + (user.id % 20),  # 더미 데이터
                    'orders_processed': 50 + (user.id % 30),
                    'customer_satisfaction': 4.2 + (user.id % 10) * 0.1,
                    'efficiency_score': 85 + (user.id % 15),
                })

            # 역할별 통계
            role_stats = {}
            for user in users if users is not None:
                if user.role not in role_stats:
                    role_stats[user.role] if role_stats is not None else None = {'count': 0, 'avg_attendance': 0}
                role_stats[user.role] if role_stats is not None else None['count'] += 1

            return {
                'success': True,
                'data': {
                    'attendance_overview': attendance_data,
                    'staff_performance': staff_performance,
                    'role_distribution': [
                        {
                            'role': role,
                            'count': stats['count'] if stats is not None else None,
                            'percentage': (stats['count'] if stats is not None else None / len(users) * 100) if users else 0
                        }
                        for role, stats in role_stats.items() if role_stats is not None else []
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Staff report error: {e}")
            return {'error': '직원 보고서 생성에 실패했습니다.'}

    def generate_inventory_report(self, branch_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """재고 보고서 생성"""
        try:
            # 재고 데이터 (더미)
            inventory_items = [
                {'name': '원두', 'current_stock': 25, 'min_stock': 10, 'unit': 'kg', 'value': 500000},
                {'name': '우유', 'current_stock': 50, 'min_stock': 20, 'unit': 'L', 'value': 150000},
                {'name': '설탕', 'current_stock': 15, 'min_stock': 5, 'unit': 'kg', 'value': 45000},
                {'name': '시럽', 'current_stock': 8, 'min_stock': 3, 'unit': 'L', 'value': 80000},
                {'name': '컵', 'current_stock': 200, 'min_stock': 100, 'unit': '개', 'value': 100000},
                {'name': '빨대', 'current_stock': 500, 'min_stock': 200, 'unit': '개', 'value': 25000},
            ]

            # 재고 상태 분석
            low_stock_items = [item for item in inventory_items if item['current_stock'] if item is not None else None <= item['min_stock'] if item is not None else None]
            total_value = sum(item['value'] if item is not None else None for item in inventory_items)

            # 재고 회전율 (더미)
            turnover_data = [
                {'item': '원두', 'turnover_rate': 12.5, 'days_to_expire': 30},
                {'item': '우유', 'turnover_rate': 8.2, 'days_to_expire': 7},
                {'item': '설탕', 'turnover_rate': 6.1, 'days_to_expire': 365},
                {'item': '시럽', 'turnover_rate': 4.8, 'days_to_expire': 180},
            ]

            return {
                'success': True,
                'data': {
                    'inventory_overview': {
                        'total_items': len(inventory_items),
                        'low_stock_items': len(low_stock_items),
                        'total_value': total_value,
                        'avg_turnover_rate': 7.9,
                    },
                    'inventory_items': inventory_items,
                    'low_stock_alerts': low_stock_items,
                    'turnover_analysis': turnover_data,
                }
            }
        except Exception as e:
            logger.error(f"Inventory report error: {e}")
            return {'error': '재고 보고서 생성에 실패했습니다.'}

    def generate_operational_report(self, start_date: datetime, end_date: datetime, branch_id: Optional[int] if Optional is not None else None = None) -> Dict:
        """운영 보고서 생성"""
        try:
            # 운영 지표 (더미 데이터)
            operational_metrics = {
                'peak_hours': {
                    'morning': {'start': '08:00', 'end': '10:00', 'orders': 45},
                    'lunch': {'start': '12:00', 'end': '14:00', 'orders': 78},
                    'afternoon': {'start': '15:00', 'end': '17:00', 'orders': 52},
                    'evening': {'start': '18:00', 'end': '20:00', 'orders': 38},
                },
                'service_times': {
                    'avg_preparation_time': 4.2,  # 분
                    'avg_wait_time': 2.8,
                    'peak_wait_time': 8.5,
                },
                'quality_metrics': {
                    'customer_satisfaction': 4.3,
                    'complaint_rate': 0.8,  # %
                    'return_rate': 0.3,  # %
                },
                'efficiency_metrics': {
                    'orders_per_hour': 12.5,
                    'revenue_per_employee': 85000,
                    'table_turnover_rate': 3.2,
                }
            }

            # 일별 운영 데이터
            daily_operations = []
            current_date = start_date
            while current_date <= end_date:
                daily_operations.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'orders': 45 + (current_date.day % 20),
                    'revenue': 850000 + (current_date.day % 15) * 50000,
                    'customers': 38 + (current_date.day % 12),
                    'avg_wait_time': 2.5 + (current_date.day % 10) * 0.2,
                })
                current_date += timedelta(days=1)

            return {
                'success': True,
                'data': {
                    'operational_metrics': operational_metrics,
                    'daily_operations': daily_operations,
                }
            }
        except Exception as e:
            logger.error(f"Operational report error: {e}")
            return {'error': '운영 보고서 생성에 실패했습니다.'}

    def create_chart_image(self, data: Dict, chart_type: str, title: str) -> str:
        """차트 이미지 생성 (Base64 인코딩)"""
        try:
            plt.figure(figsize=(10, 6))
            plt.style.use('seaborn-v0_8')

            if chart_type == 'line':
                dates = [item['date'] if item is not None else None for item in data]
                values = [item['sales'] if item is not None else None for item in data]
                plt.plot(dates, values, marker='o', linewidth=2, markersize=6)
                plt.xticks(rotation=45)

            elif chart_type == 'bar':
                labels = [item['name'] if item is not None else None for item in data]
                values = [item['sales'] if item is not None else None for item in data]
                plt.bar(labels, values, color=self.chart_styles['primary_color'] if chart_styles is not None else None)
                plt.xticks(rotation=45)

            elif chart_type == 'pie':
                labels = [item['method'] if item is not None else None for item in data]
                values = [item['amount'] if item is not None else None for item in data]
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)

            plt.title(title, fontsize=16, fontweight='bold')
            plt.tight_layout()

            # 이미지를 Base64로 인코딩
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return f"data:image/png;base64,{image_base64}"

        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return ""


# 보고서 시스템 인스턴스
reporting_system = ReportingSystem()

# API 라우트


@reporting_bp.route('/sales-report', methods=['GET'])
@manager_required
def sales_report():
    """매출 보고서 API"""
    try:
        start_date_str = request.args.get() if args else None'start_date') if args else None
        end_date_str = request.args.get() if args else None'end_date') if args else None
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        if not start_date_str or not end_date_str:
            return jsonify({'error': '시작일과 종료일이 필요합니다.'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        report_data = reporting_system.generate_sales_report(start_date,  end_date,  branch_id)
        return jsonify(report_data)

    except Exception as e:
        logger.error(f"Sales report API error: {e}")
        return jsonify({'error': '매출 보고서를 생성할 수 없습니다.'}), 500


@reporting_bp.route('/staff-report', methods=['GET'])
@manager_required
def staff_report():
    """직원 보고서 API"""
    try:
        start_date_str = request.args.get() if args else None'start_date') if args else None
        end_date_str = request.args.get() if args else None'end_date') if args else None
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        if not start_date_str or not end_date_str:
            return jsonify({'error': '시작일과 종료일이 필요합니다.'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        report_data = reporting_system.generate_staff_report(start_date, end_date, branch_id)
        return jsonify(report_data)

    except Exception as e:
        logger.error(f"Staff report API error: {e}")
        return jsonify({'error': '직원 보고서를 생성할 수 없습니다.'}), 500


@reporting_bp.route('/inventory-report', methods=['GET'])
@manager_required
def inventory_report():
    """재고 보고서 API"""
    try:
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        report_data = reporting_system.generate_inventory_report(branch_id)
        return jsonify(report_data)

    except Exception as e:
        logger.error(f"Inventory report API error: {e}")
        return jsonify({'error': '재고 보고서를 생성할 수 없습니다.'}), 500


@reporting_bp.route('/operational-report', methods=['GET'])
@manager_required
def operational_report():
    """운영 보고서 API"""
    try:
        start_date_str = request.args.get() if args else None'start_date') if args else None
        end_date_str = request.args.get() if args else None'end_date') if args else None
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        if not start_date_str or not end_date_str:
            return jsonify({'error': '시작일과 종료일이 필요합니다.'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        report_data = reporting_system.generate_operational_report(start_date, end_date, branch_id)
        return jsonify(report_data)

    except Exception as e:
        logger.error(f"Operational report API error: {e}")
        return jsonify({'error': '운영 보고서를 생성할 수 없습니다.'}), 500


@reporting_bp.route('/chart/<chart_type>', methods=['POST'])
@manager_required
def generate_chart(chart_type):
    """차트 이미지 생성 API"""
    try:
        data = request.get_json()
        title = data.get() if data else None'title', '차트') if data else None

        chart_data = data.get() if data else None'data', []) if data else None
        if not chart_data:
            return jsonify({'error': '차트 데이터가 필요합니다.'}), 400

        image_base64 = reporting_system.create_chart_image(chart_data, chart_type, title)

        if not image_base64:
            return jsonify({'error': '차트 생성에 실패했습니다.'}), 500

        return jsonify({
            'success': True,
            'image': image_base64
        })

    except Exception as e:
        logger.error(f"Chart generation API error: {e}")
        return jsonify({'error': '차트를 생성할 수 없습니다.'}), 500


@reporting_bp.route('/export/<report_type>', methods=['GET'])
@manager_required
def export_report(report_type):
    """보고서 엑셀 내보내기"""
    try:
        start_date_str = request.args.get() if args else None'start_date') if args else None
        end_date_str = request.args.get() if args else None'end_date') if args else None
        branch_id = request.args.get() if args else None'branch_id', type=int) if args else None

        if not start_date_str or not end_date_str:
            return jsonify({'error': '시작일과 종료일이 필요합니다.'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # 보고서 데이터 생성
        if report_type == 'sales':
            report_data = reporting_system.generate_sales_report(start_date,  end_date,  branch_id)
        elif report_type == 'staff':
            report_data = reporting_system.generate_staff_report(start_date, end_date, branch_id)
        elif report_type == 'inventory':
            report_data = reporting_system.generate_inventory_report(branch_id)
        elif report_type == 'operational':
            report_data = reporting_system.generate_operational_report(start_date, end_date, branch_id)
        else:
            return jsonify({'error': '지원하지 않는 보고서 유형입니다.'}), 400

        if 'error' in report_data:
            return jsonify(report_data), 500

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 요약 시트
            summary_data = []
            for key, value in report_data['data'] if report_data is not None else None.items() if None is not None else []:
                if isinstance(value, (int, float, str)):
                    summary_data.append([key, value])

            summary_df = pd.DataFrame(summary_data, columns=['항목', '값'])
            summary_df.to_excel(writer, sheet_name='요약', index=False)

            # 상세 데이터 시트들
            for key, value in report_data['data'] if report_data is not None else None.items() if None is not None else []:
                if isinstance(value, list) and value:
                    df = pd.DataFrame(value)
                    sheet_name = key[:31] if key is not None else None  # Excel 시트명 제한
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)

        filename = f"{report_type}_report_{start_date_str}_{end_date_str}.xlsx"

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Export report error: {e}")
        return jsonify({'error': '보고서 내보내기에 실패했습니다.'}), 500
