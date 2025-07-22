"""
WebSocket 실시간 서버
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional
from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeServer:
    """실시간 WebSocket 서버"""
    
    def __init__(self):
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.rooms: Dict[str, Set[str]] = {
            'admin': set(),
            'employee': set(),
            'brand': set(),
            'branch': set()
        }
        self.user_rooms: Dict[str, Set[str]] = {}
        
    async def register_client(self, websocket: WebSocketServerProtocol, user_id: str, user_type: str):
        """클라이언트 등록"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        
        # 사용자 타입별 방에 추가
        if user_type in self.rooms:
            self.rooms[user_type].add(client_id)
        
        # 사용자별 방 관리
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(client_id)
        
        logger.info(f"클라이언트 등록: {client_id} (사용자: {user_id}, 타입: {user_type})")
        
        # 환영 메시지 전송
        await self.send_to_client(client_id, {
            'type': 'welcome',
            'client_id': client_id,
            'message': '실시간 서버에 연결되었습니다.',
            'timestamp': datetime.now().isoformat()
        })
        
        return client_id
    
    async def unregister_client(self, client_id: str):
        """클라이언트 등록 해제"""
        if client_id in self.clients:
            websocket = self.clients[client_id]
            
            # 모든 방에서 제거
            for room_clients in self.rooms.values():
                room_clients.discard(client_id)
            
            # 사용자별 방에서 제거
            for user_clients in self.user_rooms.values():
                user_clients.discard(client_id)
            
            del self.clients[client_id]
            logger.info(f"클라이언트 등록 해제: {client_id}")
    
    async def send_to_client(self, client_id: str, message: dict):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.clients:
            try:
                websocket = self.clients[client_id]
                await websocket.send(json.dumps(message, ensure_ascii=False))
            except ConnectionClosed:
                await self.unregister_client(client_id)
            except Exception as e:
                logger.error(f"메시지 전송 실패: {e}")
    
    async def broadcast_to_room(self, room: str, message: dict):
        """특정 방의 모든 클라이언트에게 브로드캐스트"""
        if room in self.rooms:
            for client_id in self.rooms[room].copy():
                await self.send_to_client(client_id, message)
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """특정 사용자의 모든 클라이언트에게 브로드캐스트"""
        if user_id in self.user_rooms:
            for client_id in self.user_rooms[user_id].copy():
                await self.send_to_client(client_id, message)
    
    async def broadcast_to_all(self, message: dict):
        """모든 클라이언트에게 브로드캐스트"""
        for client_id in list(self.clients.keys()):
            await self.send_to_client(client_id, message)
    
    async def handle_clock_in_out(self, user_id: str, action: str, timestamp: str):
        """출근/퇴근 알림 처리"""
        message = {
            'type': 'clock_event',
            'user_id': user_id,
            'action': action,
            'timestamp': timestamp,
            'message': f'직원 {user_id}이(가) {action}했습니다.'
        }
        
        # 관리자에게 알림
        await self.broadcast_to_room('admin', message)
        
        # 해당 사용자에게 알림
        await self.broadcast_to_user(user_id, message)
    
    async def handle_schedule_update(self, employee_id: str, schedule_data: dict):
        """스케줄 업데이트 알림 처리"""
        message = {
            'type': 'schedule_update',
            'employee_id': employee_id,
            'schedule': schedule_data,
            'timestamp': datetime.now().isoformat(),
            'message': f'직원 {employee_id}의 스케줄이 업데이트되었습니다.'
        }
        
        # 관리자에게 알림
        await self.broadcast_to_room('admin', message)
        
        # 해당 직원에게 알림
        await self.broadcast_to_user(employee_id, message)
    
    async def handle_notification(self, target_type: str, target_id: str, notification: dict):
        """일반 알림 처리"""
        message = {
            'type': 'notification',
            'target_type': target_type,
            'target_id': target_id,
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        }
        
        if target_type == 'all':
            await self.broadcast_to_all(message)
        elif target_type == 'admin':
            await self.broadcast_to_room('admin', message)
        elif target_type == 'user':
            await self.broadcast_to_user(target_id, message)
        elif target_type == 'room':
            await self.broadcast_to_room(target_id, message)
    
    async def handle_system_alert(self, alert_type: str, message: str):
        """시스템 알림 처리"""
        alert = {
            'type': 'system_alert',
            'alert_type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # 모든 관리자에게 알림
        await self.broadcast_to_room('admin', alert)
        
        # 긴급 알림인 경우 모든 사용자에게 알림
        if alert_type == 'error':
            await self.broadcast_to_all(alert)
    
    async def handle_dashboard_update(self, dashboard_type: str, data: dict):
        """대시보드 업데이트 처리"""
        message = {
            'type': 'dashboard_update',
            'dashboard_type': dashboard_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        if dashboard_type == 'admin':
            await self.broadcast_to_room('admin', message)
        elif dashboard_type == 'employee':
            await self.broadcast_to_room('employee', message)
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, client_id: str, message: dict):
        """클라이언트 메시지 처리"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'ping':
                # 핑 응답
                await self.send_to_client(client_id, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            
            elif msg_type == 'join_room':
                # 방 참가
                room = message.get('room')
                if room and room in self.rooms:
                    self.rooms[room].add(client_id)
                    await self.send_to_client(client_id, {
                        'type': 'room_joined',
                        'room': room,
                        'timestamp': datetime.now().isoformat()
                    })
            
            elif msg_type == 'leave_room':
                # 방 나가기
                room = message.get('room')
                if room and room in self.rooms:
                    self.rooms[room].discard(client_id)
                    await self.send_to_client(client_id, {
                        'type': 'room_left',
                        'room': room,
                        'timestamp': datetime.now().isoformat()
                    })
            
            elif msg_type == 'chat':
                # 채팅 메시지
                room = message.get('room', 'general')
                chat_message = {
                    'type': 'chat',
                    'room': room,
                    'user_id': message.get('user_id'),
                    'message': message.get('message'),
                    'timestamp': datetime.now().isoformat()
                }
                await self.broadcast_to_room(room, chat_message)
            
            elif msg_type == 'request_dashboard':
                # 대시보드 데이터 요청
                dashboard_type = message.get('dashboard_type')
                if dashboard_type:
                    # 실제로는 데이터베이스에서 데이터를 가져와야 함
                    dashboard_data = {
                        'type': 'dashboard_data',
                        'dashboard_type': dashboard_type,
                        'data': {
                            'stats': {'total_users': len(self.clients)},
                            'last_updated': datetime.now().isoformat()
                        }
                    }
                    await self.send_to_client(client_id, dashboard_data)
            
            else:
                # 알 수 없는 메시지 타입
                await self.send_to_client(client_id, {
                    'type': 'error',
                    'message': f'알 수 없는 메시지 타입: {msg_type}',
                    'timestamp': datetime.now().isoformat()
                })
        
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '메시지 처리 중 오류가 발생했습니다.',
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_connection(self, websocket: WebSocketServerProtocol):
        """클라이언트 연결 처리"""
        client_id = None
        
        try:
            # 초기 인증 메시지 대기
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            user_id = auth_data.get('user_id', 'anonymous')
            user_type = auth_data.get('user_type', 'guest')
            
            # 클라이언트 등록
            client_id = await self.register_client(websocket, user_id, user_type)
            
            # 연결 성공 알림
            await self.broadcast_to_room('admin', {
                'type': 'user_connected',
                'user_id': user_id,
                'user_type': user_type,
                'client_id': client_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # 메시지 수신 루프
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, client_id, data)
                except json.JSONDecodeError:
                    await self.send_to_client(client_id, {
                        'type': 'error',
                        'message': '잘못된 JSON 형식입니다.',
                        'timestamp': datetime.now().isoformat()
                    })
        
        except ConnectionClosed:
            logger.info(f"클라이언트 연결 종료: {client_id}")
        except Exception as e:
            logger.error(f"연결 처리 오류: {e}")
        finally:
            if client_id:
                await self.unregister_client(client_id)
                # 연결 해제 알림
                await self.broadcast_to_room('admin', {
                    'type': 'user_disconnected',
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                })

# 전역 서버 인스턴스
realtime_server = RealTimeServer()

async def main():
    """메인 함수"""
    host = "localhost"
    port = 8765
    
    logger.info(f"WebSocket 서버 시작: ws://{host}:{port}")
    
    async with serve(realtime_server.handle_connection, host, port):
        await asyncio.Future()  # 무한 대기

if __name__ == "__main__":
    asyncio.run(main()) 