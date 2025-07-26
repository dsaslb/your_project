"""
WebSocket 실시간 통신 관리
Socket.io를 사용한 실시간 알림 및 업데이트
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, session
import threading
import random

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 연결 및 이벤트 관리"""
    
    def __init__(self, app=None):
        self.socketio = None
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, List[str]] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 WebSocket 초기화"""
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,  # SocketIO 로그 비활성화
            engineio_logger=False  # Engine.IO 로그 비활성화
        )
        
        self._register_events()
        logger.info("WebSocket 매니저 초기화 완료")
    
    def _register_events(self):
        """WebSocket 이벤트 핸들러 등록"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """클라이언트 연결 처리"""
            client_id = request.sid
            user_id = session.get('user_id')
            
            self.connected_clients[client_id] = {
                'user_id': user_id,
                'connected_at': datetime.now(),
                'rooms': [],
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr
            }
            
            logger.info(f"클라이언트 연결: {client_id} (사용자: {user_id})")
            emit('connected', {
                'client_id': client_id,
                'timestamp': datetime.now().isoformat(),
                'message': '연결되었습니다.'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """클라이언트 연결 해제 처리"""
            client_id = request.sid
            
            if client_id in self.connected_clients:
                # 모든 룸에서 제거
                for room in self.connected_clients[client_id]['rooms']:
                    self._remove_from_room(client_id, room)
                
                del self.connected_clients[client_id]
                logger.info(f"클라이언트 연결 해제: {client_id}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """룸 참가 처리"""
            room = data.get('room')
            client_id = request.sid
            
            if room:
                join_room(room)
                self._add_to_room(client_id, room)
                logger.info(f"클라이언트 {client_id}가 룸 {room}에 참가")
                
                emit('room_joined', {
                    'room': room,
                    'timestamp': datetime.now().isoformat()
                }, room=room)
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """룸 나가기 처리"""
            room = data.get('room')
            client_id = request.sid
            
            if room:
                leave_room(room)
                self._remove_from_room(client_id, room)
                logger.info(f"클라이언트 {client_id}가 룸 {room}에서 나감")
                
                emit('room_left', {
                    'room': room,
                    'timestamp': datetime.now().isoformat()
                }, room=room)
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """메시지 전송 처리"""
            room = data.get('room')
            message = data.get('message')
            message_type = data.get('type', 'message')
            
            if room and message:
                emit('new_message', {
                    'room': room,
                    'message': message,
                    'type': message_type,
                    'sender': session.get('user_id'),
                    'timestamp': datetime.now().isoformat()
                }, room=room)
                
                logger.info(f"룸 {room}에 메시지 전송: {message_type}")
        
        @self.socketio.on('ping')
        def handle_ping():
            """핑 요청 처리"""
            emit('pong', {
                'timestamp': datetime.now().isoformat()
            })
    
    def _add_to_room(self, client_id: str, room: str):
        """클라이언트를 룸에 추가"""
        if client_id in self.connected_clients:
            if room not in self.connected_clients[client_id]['rooms']:
                self.connected_clients[client_id]['rooms'].append(room)
            
            if room not in self.rooms:
                self.rooms[room] = []
            
            if client_id not in self.rooms[room]:
                self.rooms[room].append(client_id)
    
    def _remove_from_room(self, client_id: str, room: str):
        """클라이언트를 룸에서 제거"""
        if client_id in self.connected_clients:
            if room in self.connected_clients[client_id]['rooms']:
                self.connected_clients[client_id]['rooms'].remove(room)
        
        if room in self.rooms and client_id in self.rooms[room]:
            self.rooms[room].remove(client_id)
            
            # 빈 룸 정리
            if not self.rooms[room]:
                del self.rooms[room]
    
    def broadcast_notification(self, notification: Dict[str, Any], room: str = None):
        """알림 브로드캐스트"""
        data = {
            'type': 'notification',
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        }
        
        if room:
            self.socketio.emit('notification', data, room=room)
            logger.info(f"룸 {room}에 알림 브로드캐스트")
        else:
            self.socketio.emit('notification', data)
            logger.info("전체 알림 브로드캐스트")
    
    def send_to_user(self, user_id: int, event: str, data: Dict[str, Any]):
        """특정 사용자에게 메시지 전송"""
        target_clients = [
            client_id for client_id, client_info in self.connected_clients.items()
            if client_info.get('user_id') == user_id
        ]
        
        for client_id in target_clients:
            self.socketio.emit(event, data, room=client_id)
        
        logger.info(f"사용자 {user_id}에게 {event} 이벤트 전송")
    
    def send_to_room(self, room: str, event: str, data: Dict[str, Any]):
        """특정 룸에 메시지 전송"""
        self.socketio.emit(event, data, room=room)
        logger.info(f"룸 {room}에 {event} 이벤트 전송")
    
    def broadcast_system_alert(self, alert: Dict[str, Any]):
        """시스템 알림 브로드캐스트"""
        data = {
            'type': 'system_alert',
            'alert': alert,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('system_alert', data)
        logger.info("시스템 알림 브로드캐스트")
    
    def broadcast_plugin_update(self, plugin_name: str, status: str):
        """플러그인 업데이트 브로드캐스트"""
        data = {
            'type': 'plugin_update',
            'plugin_name': plugin_name,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        self.socketio.emit('plugin_update', data)
        logger.info(f"플러그인 업데이트 브로드캐스트: {plugin_name} - {status}")

    def broadcast_order_update(self, order_data: Dict[str, Any]):
        """주문 업데이트 브로드캐스트"""
        data = {
            'type': 'order_update',
            'order': order_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 주문 관련 룸에 브로드캐스트
        self.socketio.emit('order_update', data, room=f"orders_{order_data.get('brand_id')}")
        logger.info(f"주문 업데이트 브로드캐스트: {order_data.get('order_id')}")

    def broadcast_inventory_alert(self, inventory_data: Dict[str, Any]):
        """재고 알림 브로드캐스트"""
        data = {
            'type': 'inventory_alert',
            'inventory': inventory_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 재고 관리자 룸에 브로드캐스트
        self.socketio.emit('inventory_alert', data, room=f"inventory_{inventory_data.get('brand_id')}")
        logger.info(f"재고 알림 브로드캐스트: {inventory_data.get('product_name')}")

    def broadcast_customer_feedback(self, feedback_data: Dict[str, Any]):
        """고객 피드백 브로드캐스트"""
        data = {
            'type': 'customer_feedback',
            'feedback': feedback_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 고객 서비스 룸에 브로드캐스트
        self.socketio.emit('customer_feedback', data, room=f"customer_service_{feedback_data.get('brand_id')}")
        logger.info(f"고객 피드백 브로드캐스트: {feedback_data.get('rating')}점")

    def broadcast_store_status(self, store_data: Dict[str, Any]):
        """매장 상태 브로드캐스트"""
        data = {
            'type': 'store_status',
            'store': store_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 매장 관리 룸에 브로드캐스트
        self.socketio.emit('store_status', data, room=f"store_management_{store_data.get('brand_id')}")
        logger.info(f"매장 상태 브로드캐스트: {store_data.get('store_name')}")

    def broadcast_employee_activity(self, activity_data: Dict[str, Any]):
        """직원 활동 브로드캐스트"""
        data = {
            'type': 'employee_activity',
            'activity': activity_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 직원 관리 룸에 브로드캐스트
        self.socketio.emit('employee_activity', data, room=f"employee_management_{activity_data.get('brand_id')}")
        logger.info(f"직원 활동 브로드캐스트: {activity_data.get('employee_name')}")

    def broadcast_sales_report(self, sales_data: Dict[str, Any]):
        """매출 리포트 브로드캐스트"""
        data = {
            'type': 'sales_report',
            'sales': sales_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 매출 관리 룸에 브로드캐스트
        self.socketio.emit('sales_report', data, room=f"sales_management_{sales_data.get('brand_id')}")
        logger.info(f"매출 리포트 브로드캐스트: {sales_data.get('period')}")
    
    def get_connected_clients_count(self) -> int:
        """연결된 클라이언트 수 반환"""
        return len(self.connected_clients)
    
    def get_room_clients_count(self, room: str) -> int:
        """특정 룸의 클라이언트 수 반환"""
        return len(self.rooms.get(room, []))
    
    def get_connected_users(self) -> List[int]:
        """연결된 사용자 ID 목록 반환"""
        return list(set([
            client_info['user_id'] for client_info in self.connected_clients.values()
            if client_info.get('user_id')
        ]))
    
    def get_room_info(self) -> Dict[str, Any]:
        """룸 정보 반환"""
        return {
            'total_rooms': len(self.rooms),
            'rooms': {
                room: {
                    'client_count': len(clients),
                    'clients': clients
                }
                for room, clients in self.rooms.items()
            }
        }
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """종합 통계 반환"""
        stats = {
            'connected_clients': self.get_connected_clients_count(),
            'connected_users': self.get_connected_users(),
            'room_info': self.get_room_info(),
            'broadcast_active': hasattr(self, '_dashboard_broadcast_thread') and 
                              self._dashboard_broadcast_thread.is_alive(),
            'timestamp': datetime.now().isoformat()
        }
        
        # 시스템 모니터링에 통계 전달
        try:
            from utils.system_monitor import system_monitor
            system_monitor.update_websocket_stats(stats)
        except ImportError:
            pass  # 시스템 모니터링이 없어도 계속 작동
        
        return stats

    def start_dashboard_broadcast(self):
        """대시보드 통계 브로드캐스트 시작 (개선된 버전)"""
        def emit_dashboard_stats():
            self._stop_broadcast = False
            while not getattr(self, '_stop_broadcast', False):
                try:
                    # 연결된 클라이언트가 있을 때만 브로드캐스트
                    if self.get_connected_clients_count() > 0:
                        stats = {
                            'active_users': self.get_connected_clients_count(),
                            'orders': random.randint(100, 200),
                            'timestamp': datetime.now().isoformat()
                        }
                        self.socketio.emit('dashboard_stats', stats)
                        logger.debug(f"대시보드 통계 브로드캐스트: {stats['active_users']}명 연결")
                    else:
                        logger.debug("연결된 클라이언트가 없어 브로드캐스트 건너뜀")
                    
                    # 30초마다 실행 (5초에서 변경)
                    self.socketio.sleep(30)
                except Exception as e:
                    logger.error(f"대시보드 브로드캐스트 오류: {e}")
                    self.socketio.sleep(60)  # 오류 시 1분 대기
            
            logger.info("대시보드 브로드캐스트가 중지되었습니다.")
        
        # 이미 실행 중인지 확인
        if hasattr(self, '_dashboard_broadcast_thread') and self._dashboard_broadcast_thread.is_alive():
            logger.info("대시보드 브로드캐스트가 이미 실행 중입니다.")
            return
        
        self._dashboard_broadcast_thread = threading.Thread(target=emit_dashboard_stats, daemon=True)
        self._dashboard_broadcast_thread.start()
        logger.info("대시보드 브로드캐스트가 시작되었습니다.")
    
    def stop_dashboard_broadcast(self):
        """대시보드 통계 브로드캐스트 중지"""
        if hasattr(self, '_dashboard_broadcast_thread') and self._dashboard_broadcast_thread.is_alive():
            # 스레드 중지 플래그 설정
            self._stop_broadcast = True
            logger.info("대시보드 브로드캐스트 중지 요청됨")
        else:
            logger.info("실행 중인 대시보드 브로드캐스트가 없습니다.")

# 전역 WebSocket 매니저 인스턴스
websocket_manager = WebSocketManager() 