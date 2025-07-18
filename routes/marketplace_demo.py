import random
from datetime import datetime, timedelta
import json
from flask import Blueprint, render_template, jsonify, request
form = None  # pyright: ignore

marketplace_demo_bp = Blueprint('marketplace_demo', __name__)


@marketplace_demo_bp.route('/marketplace/demo/<module_id>')
def demo_module(module_id):
    """모듈 데모 페이지"""
    try:
        # 플러그인 정보 로드
        with open('marketplace/plugins.json', 'r', encoding='utf-8') as f:
            plugins = json.load(f)

        plugin = next((p for p in plugins if (p is not None and p.get('id') == module_id)), None)
        if not plugin:
            return render_template('errors/404.html'), 404

        return render_template('marketplace/demo.html', plugin=plugin)

    except Exception as e:
        return render_template('errors/500.html'), 500


@marketplace_demo_bp.route('/api/marketplace/demo/<module_id>/data')
def get_demo_data(module_id):
    """데모 데이터 API"""
    try:
        if module_id == 'attendance_management':
            return get_attendance_demo_data()
        elif module_id == 'restaurant_analytics':
            return get_analytics_demo_data()
        elif module_id == 'inventory_management':
            return get_inventory_demo_data()
        elif module_id == 'customer_loyalty':
            return get_loyalty_demo_data()
        elif module_id == 'employee_scheduling':
            return get_scheduling_demo_data()
        else:
            return jsonify({'error': '지원하지 않는 모듈입니다.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_attendance_demo_data():
    """출퇴근 관리 데모 데이터"""
    today = datetime.now().strftime('%Y-%m-%d')

    # 실시간 데이터 시뮬레이션
    current_time = datetime.now()
    demo_data = {
        "employees": [
            {
                "id": "emp_001",
                "name": "김철수",
                "position": "매니저",
                "store_id": "store_001",
                "brand_id": "brand_001",
                "avatar": "/static/images/avatars/employee1.png"
            },
            {
                "id": "emp_002",
                "name": "이영희",
                "position": "직원",
                "store_id": "store_001",
                "brand_id": "brand_001",
                "avatar": "/static/images/avatars/employee2.png"
            },
            {
                "id": "emp_003",
                "name": "박민수",
                "position": "직원",
                "store_id": "store_001",
                "brand_id": "brand_001",
                "avatar": "/static/images/avatars/employee3.png"
            }
        ],
        "attendance_records": [
            {
                "id": "att_001",
                "employee_id": "emp_001",
                "employee_name": "김철수",
                "date": today,
                "check_in_time": "08:45:00",
                "check_out_time": current_time.strftime('%H:%M:%S') if current_time.hour >= 18 else None,
                "work_hours": 9.5 if current_time.hour >= 18 else None,
                "is_late": False,
                "overtime_hours": 0.5 if current_time.hour >= 18 else 0,
                "status": "checked_out" if current_time.hour >= 18 else "checked_in"
            },
            {
                "id": "att_002",
                "employee_id": "emp_002",
                "employee_name": "이영희",
                "date": today,
                "check_in_time": "09:15:00",
                "check_out_time": current_time.strftime('%H:%M:%S') if current_time.hour >= 18 else None,
                "work_hours": 8.75 if current_time.hour >= 18 else None,
                "is_late": True,
                "overtime_hours": 0,
                "status": "checked_out" if current_time.hour >= 18 else "checked_in"
            },
            {
                "id": "att_003",
                "employee_id": "emp_003",
                "employee_name": "박민수",
                "date": today,
                "check_in_time": "08:30:00",
                "check_out_time": current_time.strftime('%H:%M:%S') if current_time.hour >= 18 else None,
                "work_hours": 9.75 if current_time.hour >= 18 else None,
                "is_late": False,
                "overtime_hours": 0.75 if current_time.hour >= 18 else 0,
                "status": "checked_out" if current_time.hour >= 18 else "checked_in"
            }
        ],
        "statistics": {
            "total_employees": 3,
            "present_today": 3,
            "late_count": 1,
            "average_work_hours": 9.0 if current_time.hour >= 18 else None,
            "total_overtime": 1.25 if current_time.hour >= 18 else 0,
            "on_time_rate": 66.7
        },
        "recent_activities": [
            {
                "id": "act_001",
                "employee_name": "김철수",
                "action": "출근",
                "time": "08:45:00",
                "status": "정시"
            },
            {
                "id": "act_002",
                "employee_name": "이영희",
                "action": "출근",
                "time": "09:15:00",
                "status": "지각"
            },
            {
                "id": "act_003",
                "employee_name": "박민수",
                "action": "출근",
                "time": "08:30:00",
                "status": "정시"
            }
        ]
    }

    return jsonify(demo_data)


def get_analytics_demo_data():
    """레스토랑 분석 데모 데이터"""
    demo_data = {
        "sales_data": [
            {
                "date": "2024-01-15",
                "total_sales": 2500000,
                "order_count": 150,
                "average_order": 16667
            },
            {
                "date": "2024-01-14",
                "total_sales": 2300000,
                "order_count": 140,
                "average_order": 16429
            }
        ],
        "menu_performance": [
            {
                "menu_name": "스테이크",
                "sales_count": 45,
                "revenue": 675000,
                "rating": 4.8,
                "profit_margin": 65
            },
            {
                "menu_name": "파스타",
                "sales_count": 38,
                "revenue": 456000,
                "rating": 4.6,
                "profit_margin": 70
            }
        ],
        "customer_insights": {
            "total_customers": 150,
            "new_customers": 25,
            "returning_customers": 125,
            "average_rating": 4.7
        }
    }

    return jsonify(demo_data)


def get_inventory_demo_data():
    """재고 관리 데모 데이터"""
    demo_data = {
        "inventory_items": [
            {
                "id": "item_001",
                "name": "토마토",
                "current_stock": 50,
                "min_stock": 20,
                "unit_price": 2000,
                "category": "채소",
                "supplier": "농협"
            },
            {
                "id": "item_002",
                "name": "양파",
                "current_stock": 30,
                "min_stock": 15,
                "unit_price": 1500,
                "category": "채소",
                "supplier": "농협"
            }
        ],
        "orders": [
            {
                "id": "order_001",
                "item_id": "item_001",
                "item_name": "토마토",
                "quantity": 100,
                "status": "pending",
                "order_date": "2024-01-15"
            }
        ],
        "alerts": [
            {
                "id": "alert_001",
                "type": "low_stock",
                "item_name": "양파",
                "current_stock": 30,
                "min_stock": 15,
                "message": "양파 재고가 부족합니다."
            }
        ]
    }

    return jsonify(demo_data)


def get_loyalty_demo_data():
    """고객 충성도 데모 데이터"""
    demo_data = {
        "customers": [
            {
                "id": "cust_001",
                "name": "김고객",
                "points": 1500,
                "vip_level": "silver",
                "total_purchases": 250000,
                "visit_count": 15
            },
            {
                "id": "cust_002",
                "name": "이고객",
                "points": 3200,
                "vip_level": "gold",
                "total_purchases": 450000,
                "visit_count": 28
            }
        ],
        "coupons": [
            {
                "id": "coupon_001",
                "name": "10% 할인",
                "discount": 10,
                "valid_until": "2024-02-15",
                "usage_count": 45
            },
            {
                "id": "coupon_002",
                "name": "무료 음료",
                "discount": 100,
                "valid_until": "2024-01-30",
                "usage_count": 23
            }
        ],
        "vip_programs": [
            {
                "level": "bronze",
                "min_points": 0,
                "benefits": ["기본 포인트 적립"]
            },
            {
                "level": "silver",
                "min_points": 1000,
                "benefits": ["기본 포인트 적립", "5% 추가 할인"]
            },
            {
                "level": "gold",
                "min_points": 3000,
                "benefits": ["기본 포인트 적립", "10% 추가 할인", "무료 배송"]
            }
        ]
    }

    return jsonify(demo_data)


def get_scheduling_demo_data():
    """직원 스케줄링 데모 데이터"""
    today = datetime.now()
    demo_data = {
        "schedules": [
            {
                "id": "schedule_001",
                "employee_id": "emp_001",
                "employee_name": "김철수",
                "date": today.strftime('%Y-%m-%d'),
                "start_time": "09:00",
                "end_time": "18:00",
                "shift_type": "day",
                "status": "confirmed"
            },
            {
                "id": "schedule_002",
                "employee_id": "emp_002",
                "employee_name": "이영희",
                "date": today.strftime('%Y-%m-%d'),
                "start_time": "10:00",
                "end_time": "19:00",
                "shift_type": "day",
                "status": "confirmed"
            }
        ],
        "shifts": [
            {
                "id": "shift_001",
                "name": "주간",
                "start_time": "09:00",
                "end_time": "18:00",
                "color": "#4CAF50"
            },
            {
                "id": "shift_002",
                "name": "야간",
                "start_time": "18:00",
                "end_time": "03:00",
                "color": "#2196F3"
            }
        ],
        "payroll_summary": {
            "total_hours": 18,
            "overtime_hours": 0,
            "total_pay": 180000,
            "overtime_pay": 0
        }
    }

    return jsonify(demo_data)


@marketplace_demo_bp.route('/api/marketplace/demo/<module_id>/interact', methods=['POST'])
def interact_with_demo(module_id):
    """데모 상호작용 API"""
    try:
        data = request.get_json()
        action = data.get('action') if data else None

        if module_id == 'attendance_management':
            return handle_attendance_interaction(action,  data)
        elif module_id == 'inventory_management':
            return handle_inventory_interaction(action,  data)
        else:
            return jsonify({'error': '지원하지 않는 상호작용입니다.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def handle_attendance_interaction(action,  data):
    """출퇴근 관리 상호작용 처리"""
    if action == 'check_in':
        employee_id = data.get('employee_id') if data else None
        current_time = datetime.now()

        # 지각 여부 확인
        is_late = current_time.time() > datetime.strptime('09:00', '%H:%M').time()

        result = {
            'success': True,
            'message': '출근이 기록되었습니다.',
            'data': {
                'employee_id': employee_id,
                'check_in_time': current_time.strftime('%H:%M:%S'),
                'is_late': is_late,
                'status': 'checked_in'
            }
        }

        return jsonify(result)

    elif action == 'check_out':
        employee_id = data.get('employee_id') if data else None
        current_time = datetime.now()

        result = {
            'success': True,
            'message': '퇴근이 기록되었습니다.',
            'data': {
                'employee_id': employee_id,
                'check_out_time': current_time.strftime('%H:%M:%S'),
                'work_hours': 9.0,
                'status': 'checked_out'
            }
        }

        return jsonify(result)

    return jsonify({'error': '지원하지 않는 액션입니다.'}), 400


def handle_inventory_interaction(action,  data):
    """재고 관리 상호작용 처리"""
    if action == 'add_item':
        item_name = data.get('name') if data else None
        quantity = data.get('quantity', 1) if data else None

        result = {
            'success': True,
            'message': f'{item_name}이(가) 재고에 추가되었습니다.',
            'data': {
                'id': f'item_{random.randint(1000, 9999)}',
                'name': item_name,
                'current_stock': quantity,
                'min_stock': 10,
                'unit_price': 1000
            }
        }

        return jsonify(result)

    return jsonify({'error': '지원하지 않는 액션입니다.'}), 400
