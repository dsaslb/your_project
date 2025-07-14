"""
모듈 간 데이터 연동 테스트용 샘플 데이터
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List

class IntegrationTestData:
    """모듈 간 데이터 연동 테스트용 샘플 데이터"""
    
    @staticmethod
    def get_sample_data() -> Dict:
        """전체 샘플 데이터 구조"""
        return {
            "users": IntegrationTestData.get_users_data(),
            "branches": IntegrationTestData.get_branches_data(),
            "attendance": IntegrationTestData.get_attendance_data(),
            "orders": IntegrationTestData.get_orders_data(),
            "inventory": IntegrationTestData.get_inventory_data(),
            "payroll": IntegrationTestData.get_payroll_data(),
            "notifications": IntegrationTestData.get_notifications_data(),
            "analytics": IntegrationTestData.get_analytics_data()
        }
    
    @staticmethod
    def get_users_data() -> List[Dict]:
        """직원 데이터"""
        return [
            {
                "id": 1,
                "username": "kim_manager",
                "name": "김매니저",
                "role": "store_admin",
                "position": "매니저",
                "branch_id": 1,
                "brand_id": 1,
                "status": "approved",
                "created_at": "2024-01-01T09:00:00"
            },
            {
                "id": 2,
                "username": "lee_staff",
                "name": "이직원",
                "role": "employee",
                "position": "직원",
                "branch_id": 1,
                "brand_id": 1,
                "status": "approved",
                "created_at": "2024-01-01T09:00:00"
            },
            {
                "id": 3,
                "username": "park_staff",
                "name": "박직원",
                "role": "employee",
                "position": "직원",
                "branch_id": 1,
                "brand_id": 1,
                "status": "approved",
                "created_at": "2024-01-01T09:00:00"
            }
        ]
    
    @staticmethod
    def get_branches_data() -> List[Dict]:
        """매장 데이터"""
        return [
            {
                "id": 1,
                "name": "강남점",
                "brand_id": 1,
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "status": "active",
                "created_at": "2024-01-01T09:00:00"
            }
        ]
    
    @staticmethod
    def get_attendance_data() -> List[Dict]:
        """출퇴근 데이터"""
        today = datetime.now().strftime('%Y-%m-%d')
        return [
            {
                "id": 1,
                "user_id": 1,
                "date": today,
                "clock_in": f"{today}T08:45:00",
                "clock_out": f"{today}T18:15:00",
                "is_late": False,
                "work_hours": 9.5,
                "overtime_hours": 0.5,
                "status": "completed"
            },
            {
                "id": 2,
                "user_id": 2,
                "date": today,
                "clock_in": f"{today}T09:15:00",
                "clock_out": f"{today}T18:00:00",
                "is_late": True,
                "work_hours": 8.75,
                "overtime_hours": 0,
                "status": "completed"
            },
            {
                "id": 3,
                "user_id": 3,
                "date": today,
                "clock_in": f"{today}T08:30:00",
                "clock_out": None,
                "is_late": False,
                "work_hours": None,
                "overtime_hours": 0,
                "status": "checked_in"
            }
        ]
    
    @staticmethod
    def get_orders_data() -> List[Dict]:
        """주문/발주 데이터"""
        return [
            {
                "id": 1,
                "customer_name": "홍길동",
                "order_items": json.dumps([
                    {"name": "스테이크", "quantity": 2, "price": 25000},
                    {"name": "파스타", "quantity": 1, "price": 15000}
                ]),
                "total_amount": 65000,
                "status": "completed",
                "employee_id": 1,
                "store_id": 1,
                "created_at": "2024-01-15T12:00:00",
                "completed_at": "2024-01-15T12:25:00",
                "processing_minutes": 25
            },
            {
                "id": 2,
                "customer_name": "김철수",
                "order_items": json.dumps([
                    {"name": "피자", "quantity": 1, "price": 20000}
                ]),
                "total_amount": 20000,
                "status": "processing",
                "employee_id": 2,
                "store_id": 1,
                "created_at": "2024-01-15T12:30:00",
                "completed_at": None,
                "processing_minutes": None
            }
        ]
    
    @staticmethod
    def get_inventory_data() -> List[Dict]:
        """재고 데이터"""
        return [
            {
                "id": 1,
                "name": "토마토",
                "category": "채소",
                "current_stock": 50,
                "min_stock": 20,
                "max_stock": 100,
                "unit": "개",
                "unit_price": 2000,
                "supplier": "농협",
                "branch_id": 1,
                "status": "active"
            },
            {
                "id": 2,
                "name": "양파",
                "category": "채소",
                "current_stock": 15,
                "min_stock": 20,
                "max_stock": 80,
                "unit": "개",
                "unit_price": 1500,
                "supplier": "농협",
                "branch_id": 1,
                "status": "active"
            },
            {
                "id": 3,
                "name": "소고기",
                "category": "육류",
                "current_stock": 5,
                "min_stock": 10,
                "max_stock": 50,
                "unit": "kg",
                "unit_price": 50000,
                "supplier": "축협",
                "branch_id": 1,
                "status": "active"
            }
        ]
    
    @staticmethod
    def get_payroll_data() -> List[Dict]:
        """급여 데이터"""
        return [
            {
                "id": 1,
                "user_id": 1,
                "year": 2024,
                "month": 1,
                "base_salary": 3000000,
                "allowance": 200000,
                "deduction": 100000,
                "net_salary": 3100000,
                "created_at": "2024-01-15T09:00:00"
            },
            {
                "id": 2,
                "user_id": 2,
                "year": 2024,
                "month": 1,
                "base_salary": 2500000,
                "allowance": 150000,
                "deduction": 80000,
                "net_salary": 2570000,
                "created_at": "2024-01-15T09:00:00"
            }
        ]
    
    @staticmethod
    def get_notifications_data() -> List[Dict]:
        """알림 데이터"""
        return [
            {
                "id": 1,
                "user_id": 1,
                "content": "양파 재고가 부족합니다. 발주가 필요합니다.",
                "category": "재고",
                "priority": "긴급",
                "is_read": False,
                "created_at": "2024-01-15T10:00:00"
            },
            {
                "id": 2,
                "user_id": 2,
                "content": "오늘 지각하셨습니다. 다음에는 정시에 출근해주세요.",
                "category": "출퇴근",
                "priority": "일반",
                "is_read": False,
                "created_at": "2024-01-15T09:30:00"
            }
        ]
    
    @staticmethod
    def get_analytics_data() -> Dict:
        """분석 데이터"""
        return {
            "sales_analytics": {
                "total_sales_today": 85000,
                "order_count_today": 2,
                "average_order_value": 42500,
                "top_selling_items": [
                    {"name": "스테이크", "quantity": 2, "revenue": 50000},
                    {"name": "파스타", "quantity": 1, "revenue": 15000}
                ]
            },
            "attendance_analytics": {
                "total_employees": 3,
                "present_today": 3,
                "late_count": 1,
                "on_time_rate": 66.7,
                "average_work_hours": 9.125
            },
            "inventory_analytics": {
                "total_items": 3,
                "low_stock_items": 2,
                "out_of_stock_items": 0,
                "total_inventory_value": 125000
            },
            "performance_analytics": {
                "average_order_processing_time": 25,
                "customer_satisfaction_score": 4.5,
                "employee_productivity_score": 8.2
            }
        }
    
    @staticmethod
    def get_integration_test_scenarios() -> List[Dict]:
        """통합 테스트 시나리오"""
        return [
            {
                "scenario": "출퇴근 → 급여 연동",
                "description": "출퇴근 데이터를 기반으로 급여 계산",
                "test_data": {
                    "attendance_records": IntegrationTestData.get_attendance_data(),
                    "expected_payroll": {
                        "user_id": 1,
                        "work_hours": 9.5,
                        "overtime_hours": 0.5,
                        "calculated_salary": 3100000
                    }
                }
            },
            {
                "scenario": "재고 → 주문 연동",
                "description": "재고 부족 시 자동 발주 알림",
                "test_data": {
                    "inventory_items": IntegrationTestData.get_inventory_data(),
                    "expected_alerts": [
                        {
                            "type": "low_stock",
                            "item": "양파",
                            "current_stock": 15,
                            "min_stock": 20
                        }
                    ]
                }
            },
            {
                "scenario": "주문 → 직원 성과 연동",
                "description": "주문 처리 시간을 직원 성과에 반영",
                "test_data": {
                    "orders": IntegrationTestData.get_orders_data(),
                    "expected_performance": {
                        "employee_id": 1,
                        "orders_processed": 1,
                        "average_processing_time": 25,
                        "performance_score": 8.5
                    }
                }
            },
            {
                "scenario": "실시간 알림 통합",
                "description": "여러 모듈의 이벤트를 통합 알림으로 처리",
                "test_data": {
                    "events": [
                        {"type": "attendance", "event": "late_check_in", "user_id": 2},
                        {"type": "inventory", "event": "low_stock", "item_id": 2},
                        {"type": "order", "event": "processing_delay", "order_id": 2}
                    ],
                    "expected_notifications": [
                        {"user_id": 2, "content": "지각 알림"},
                        {"user_id": 1, "content": "재고 부족 알림"},
                        {"user_id": 1, "content": "주문 지연 알림"}
                    ]
                }
            }
        ]

# 테스트 실행 함수
def run_integration_tests():
    """통합 테스트 실행"""
    print("=== 모듈 간 데이터 연동 테스트 ===")
    
    # 샘플 데이터 로드
    sample_data = IntegrationTestData.get_sample_data()
    print(f"✅ 샘플 데이터 로드 완료: {len(sample_data)}개 모듈")
    
    # 테스트 시나리오 실행
    scenarios = IntegrationTestData.get_integration_test_scenarios()
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 시나리오 {i}: {scenario['scenario']}")
        print(f"   설명: {scenario['description']}")
        print(f"   ✅ 테스트 데이터 준비 완료")
    
    print(f"\n🎯 총 {len(scenarios)}개 통합 테스트 시나리오 준비 완료")
    return sample_data, scenarios

if __name__ == "__main__":
    run_integration_tests() 