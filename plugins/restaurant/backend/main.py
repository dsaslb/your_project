"""
외식업 플러그인 메인 모듈
플러그인 시스템과 연동되는 외식업 관리 기능
"""

from flask import request, jsonify
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class RestaurantPlugin:
    """외식업 플러그인 클래스"""
    
    def __init__(self):
        self.name = "restaurant"
        self.version = "1.0.0"
        self.routes = []
        self._setup_routes()
    
    def _setup_routes(self):
        """라우트 설정"""
        self.routes = [
            {
                "path": "/staff",
                "methods": ["GET", "POST"],
                "handler": "handle_staff",
                "permissions": ["staff_management"]
            },
            {
                "path": "/staff/<int:staff_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_staff_detail",
                "permissions": ["staff_management"]
            },
            {
                "path": "/inventory",
                "methods": ["GET", "POST"],
                "handler": "handle_inventory",
                "permissions": ["inventory_management"]
            },
            {
                "path": "/inventory/<int:item_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_inventory_detail",
                "permissions": ["inventory_management"]
            },
            {
                "path": "/orders",
                "methods": ["GET", "POST"],
                "handler": "handle_orders",
                "permissions": ["order_management"]
            },
            {
                "path": "/orders/<int:order_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_order_detail",
                "permissions": ["order_management"]
            },
            {
                "path": "/schedule",
                "methods": ["GET", "POST"],
                "handler": "handle_schedule",
                "permissions": ["schedule_management"]
            },
            {
                "path": "/schedule/<int:schedule_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_schedule_detail",
                "permissions": ["schedule_management"]
            },
            {
                "path": "/attendance",
                "methods": ["GET", "POST"],
                "handler": "handle_attendance",
                "permissions": ["attendance_management"]
            },
            {
                "path": "/attendance/<int:attendance_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_attendance_detail",
                "permissions": ["attendance_management"]
            },
            {
                "path": "/qsc",
                "methods": ["GET", "POST"],
                "handler": "handle_qsc",
                "permissions": ["qsc_management"]
            },
            {
                "path": "/qsc/<int:qsc_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_qsc_detail",
                "permissions": ["qsc_management"]
            },
            {
                "path": "/analytics",
                "methods": ["GET"],
                "handler": "handle_analytics",
                "permissions": ["analytics"]
            },
            {
                "path": "/iot",
                "methods": ["GET", "POST"],
                "handler": "handle_iot",
                "permissions": ["iot_management"]
            },
            {
                "path": "/iot/<int:device_id>",
                "methods": ["GET", "PUT", "DELETE"],
                "handler": "handle_iot_detail",
                "permissions": ["iot_management"]
            }
        ]
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """라우트 정보 반환"""
        return self.routes
    
    def cleanup(self):
        """플러그인 정리"""
        logger.info("외식업 플러그인 정리 완료")
    
    # API 핸들러들
    def handle_staff(self):
        """직원 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "직원 목록 조회",
                "data": [
                    {"id": 1, "name": "김철수", "position": "매니저", "status": "active"},
                    {"id": 2, "name": "이영희", "position": "직원", "status": "active"},
                    {"id": 3, "name": "박민수", "position": "직원", "status": "inactive"}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "직원 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_staff_detail(self, staff_id):
        """직원 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"직원 {staff_id} 상세 정보",
                "data": {
                    "id": staff_id,
                    "name": "김철수",
                    "position": "매니저",
                    "status": "active",
                    "contact": "010-1234-5678",
                    "email": "kim@restaurant.com"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"직원 {staff_id} 정보 수정 완료",
                "data": {"id": staff_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"직원 {staff_id} 삭제 완료"
            }), 200
    
    def handle_inventory(self):
        """재고 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "재고 목록 조회",
                "data": [
                    {"id": 1, "name": "쌀", "quantity": 100, "unit": "kg", "status": "sufficient"},
                    {"id": 2, "name": "고기", "quantity": 50, "unit": "kg", "status": "warning"},
                    {"id": 3, "name": "채소", "quantity": 20, "unit": "kg", "status": "critical"}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "재고 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_inventory_detail(self, item_id):
        """재고 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"재고 {item_id} 상세 정보",
                "data": {
                    "id": item_id,
                    "name": "쌀",
                    "quantity": 100,
                    "unit": "kg",
                    "status": "sufficient",
                    "min_quantity": 20,
                    "max_quantity": 200,
                    "supplier": "농협"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"재고 {item_id} 정보 수정 완료",
                "data": {"id": item_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"재고 {item_id} 삭제 완료"
            }), 200
    
    def handle_orders(self):
        """주문 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "주문 목록 조회",
                "data": [
                    {"id": 1, "customer": "홍길동", "items": ["김치찌개", "밥"], "status": "pending"},
                    {"id": 2, "customer": "김철수", "items": ["된장찌개"], "status": "completed"},
                    {"id": 3, "customer": "이영희", "items": ["비빔밥"], "status": "cooking"}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "주문 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_order_detail(self, order_id):
        """주문 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"주문 {order_id} 상세 정보",
                "data": {
                    "id": order_id,
                    "customer": "홍길동",
                    "items": ["김치찌개", "밥"],
                    "status": "pending",
                    "total_price": 15000,
                    "order_time": "2024-07-10T14:30:00"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"주문 {order_id} 정보 수정 완료",
                "data": {"id": order_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"주문 {order_id} 삭제 완료"
            }), 200
    
    def handle_schedule(self):
        """스케줄 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "스케줄 목록 조회",
                "data": [
                    {"id": 1, "staff": "김철수", "date": "2024-07-10", "shift": "morning"},
                    {"id": 2, "staff": "이영희", "date": "2024-07-10", "shift": "afternoon"},
                    {"id": 3, "staff": "박민수", "date": "2024-07-10", "shift": "night"}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "스케줄 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_schedule_detail(self, schedule_id):
        """스케줄 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"스케줄 {schedule_id} 상세 정보",
                "data": {
                    "id": schedule_id,
                    "staff": "김철수",
                    "date": "2024-07-10",
                    "shift": "morning",
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "status": "confirmed"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"스케줄 {schedule_id} 정보 수정 완료",
                "data": {"id": schedule_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"스케줄 {schedule_id} 삭제 완료"
            }), 200
    
    def handle_attendance(self):
        """출근 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "출근 기록 조회",
                "data": [
                    {"id": 1, "staff": "김철수", "date": "2024-07-10", "check_in": "09:00", "check_out": "17:00"},
                    {"id": 2, "staff": "이영희", "date": "2024-07-10", "check_in": "10:00", "check_out": "18:00"},
                    {"id": 3, "staff": "박민수", "date": "2024-07-10", "check_in": "11:00", "check_out": None}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "출근 기록 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_attendance_detail(self, attendance_id):
        """출근 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"출근 기록 {attendance_id} 상세 정보",
                "data": {
                    "id": attendance_id,
                    "staff": "김철수",
                    "date": "2024-07-10",
                    "check_in": "09:00",
                    "check_out": "17:00",
                    "total_hours": 8,
                    "status": "completed"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"출근 기록 {attendance_id} 정보 수정 완료",
                "data": {"id": attendance_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"출근 기록 {attendance_id} 삭제 완료"
            }), 200
    
    def handle_qsc(self):
        """QSC 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "QSC 평가 목록 조회",
                "data": [
                    {"id": 1, "category": "품질", "score": 85, "date": "2024-07-10", "evaluator": "매니저"},
                    {"id": 2, "category": "서비스", "score": 90, "date": "2024-07-10", "evaluator": "매니저"},
                    {"id": 3, "category": "청결", "score": 88, "date": "2024-07-10", "evaluator": "매니저"}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "QSC 평가 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_qsc_detail(self, qsc_id):
        """QSC 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"QSC 평가 {qsc_id} 상세 정보",
                "data": {
                    "id": qsc_id,
                    "category": "품질",
                    "score": 85,
                    "date": "2024-07-10",
                    "evaluator": "매니저",
                    "details": {
                        "음식_품질": 90,
                        "온도_관리": 80,
                        "신선도": 85
                    },
                    "comments": "전반적으로 양호하나 온도 관리 개선 필요"
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"QSC 평가 {qsc_id} 정보 수정 완료",
                "data": {"id": qsc_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"QSC 평가 {qsc_id} 삭제 완료"
            }), 200
    
    def handle_analytics(self):
        """분석 API"""
        return jsonify({
            "message": "분석 데이터",
            "data": {
                "sales_summary": {
                    "today": 1500000,
                    "week": 8500000,
                    "month": 35000000
                },
                "staff_performance": {
                    "total_staff": 15,
                    "active_staff": 12,
                    "avg_hours": 8.5
                },
                "inventory_status": {
                    "total_items": 150,
                    "low_stock": 5,
                    "out_of_stock": 2
                },
                "customer_satisfaction": {
                    "avg_rating": 4.2,
                    "total_reviews": 1250
                }
            }
        })
    
    def handle_iot(self):
        """IoT 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": "IoT 기기 목록 조회",
                "data": [
                    {"id": 1, "name": "온도센서_냉장고", "type": "temperature", "status": "online", "value": 4.2},
                    {"id": 2, "name": "습도센서_창고", "type": "humidity", "status": "online", "value": 65.5},
                    {"id": 3, "name": "무게센서_저울", "type": "weight", "status": "offline", "value": 0.0}
                ]
            })
        elif request.method == "POST":
            data = request.get_json()
            return jsonify({
                "message": "IoT 기기 등록 완료",
                "data": {"id": 4, **data}
            }), 201
    
    def handle_iot_detail(self, device_id):
        """IoT 상세 관리 API"""
        if request.method == "GET":
            return jsonify({
                "message": f"IoT 기기 {device_id} 상세 정보",
                "data": {
                    "id": device_id,
                    "name": "온도센서_냉장고",
                    "type": "temperature",
                    "status": "online",
                    "value": 4.2,
                    "location": "주방_냉장고",
                    "last_update": "2024-07-10T14:30:00",
                    "alerts": ["온도_높음"]
                }
            })
        elif request.method == "PUT":
            data = request.get_json()
            return jsonify({
                "message": f"IoT 기기 {device_id} 정보 수정 완료",
                "data": {"id": device_id, **data}
            })
        elif request.method == "DELETE":
            return jsonify({
                "message": f"IoT 기기 {device_id} 삭제 완료"
            }), 200

def initialize_plugin():
    """플러그인 초기화 함수"""
    logger.info("외식업 플러그인 초기화 시작")
    plugin = RestaurantPlugin()
    logger.info("외식업 플러그인 초기화 완료")
    return plugin 