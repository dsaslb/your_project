"""
데이터 동기화 WebSocket 서버
실시간 데이터 업데이트와 캐시 동기화를 위한 WebSocket 서버

특징:
- 실시간 데이터 변경 알림
- 캐시 무효화 알림
- 자동 하트비트
- 클라이언트 인증
- 룸 기반 메시징 (역할별 구분)
"""

import asyncio
import json
import logging
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Any

# 상위 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed, WebSocketException

try:
    import jwt
except ImportError:
    print("Warning: PyJWT not installed. Authentication will be disabled.")
    jwt = None

try:
    from models import User, Brand, Store, Staff  # 기존 모델 import
    from utils.database import db  # 데이터베이스 유틸리티
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Models not available ({e}). Running in standalone mode.")
    MODELS_AVAILABLE = False
    # Mock classes for standalone mode
    class User:
        def __init__(self):
            self.id = None
            self.username = None
            self.role = None
    
    class Brand:
        pass
    
    class Store:
        pass
    
    class Staff:
        pass
    
    class db:
        @staticmethod
        def session():
            return None

logger = logging.getLogger(__name__)

class DataSyncWebSocketServer:
    def __init__(self, host='localhost', port=8765, secret_key='your-secret-key'):
        self.host = host
        self.port = port
        self.secret_key = secret_key
        
        # 연결된 클라이언트들
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.client_info: Dict[str, Dict] = {}  # 클라이언트 정보 (user_id, role, rooms)
        
        # 룸 시스템 (역할별 메시징)
        self.rooms: Dict[str, Set[str]] = {
            'super_admin': set(),
            'admin': set(),
            'brand_manager': set(),
            'store_manager': set(),
            'employee': set(),
            'all': set()
        }
        
        # 하트비트 관리
        self.heartbeat_interval = 30  # 30초마다 하트비트
        self.heartbeat_timeout = 60   # 60초 타임아웃
        self.heartbeat_task = None
        
    async def start_server(self):
        """WebSocket 서버 시작"""
        logger.info(f"데이터 동기화 WebSocket 서버 시작: {self.host}:{self.port}")
        
        # 하트비트 태스크 시작
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        
        # WebSocket 서버 시작
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        ):
            await asyncio.Future()  # 무한 실행
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """클라이언트 연결 처리"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{time.time()}"
        self.clients[client_id] = websocket
        self.client_info[client_id] = {
            'user_id': None,
            'role': None,
            'rooms': {'all'},
            'last_heartbeat': time.time(),
            'authenticated': False
        }
        
        logger.info(f"클라이언트 연결: {client_id}")
        
        try:
            # 환영 메시지 전송
            await self.send_to_client(client_id, {
                'type': 'welcome',
                'client_id': client_id,
                'message': '데이터 동기화 서버에 연결되었습니다',
                'timestamp': datetime.now().isoformat()
            })
            
            # 메시지 처리 루프
            async for message in websocket:
                await self.process_message(client_id, message)
                
        except ConnectionClosed:
            logger.info(f"클라이언트 연결 종료: {client_id}")
        except WebSocketException as e:
            logger.error(f"WebSocket 오류 [{client_id}]: {e}")
        except Exception as e:
            logger.error(f"클라이언트 처리 오류 [{client_id}]: {e}")
        finally:
            await self.disconnect_client(client_id)
    
    async def process_message(self, client_id: str, message: str):
        """클라이언트 메시지 처리"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'auth':
                await self.handle_auth(client_id, data)
            elif message_type == 'heartbeat_response':
                await self.handle_heartbeat_response(client_id, data)
            elif message_type == 'subscribe':
                await self.handle_subscribe(client_id, data)
            elif message_type == 'data_change':
                await self.handle_data_change(client_id, data)
            else:
                logger.warning(f"알 수 없는 메시지 타입 [{client_id}]: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"잘못된 JSON 메시지 [{client_id}]: {message}")
        except Exception as e:
            logger.error(f"메시지 처리 오류 [{client_id}]: {e}")
    
    async def handle_auth(self, client_id: str, data: Dict):
        """인증 처리"""
        if not jwt:
            await self.send_error(client_id, 'JWT 라이브러리가 설치되지 않았습니다')
            return
            
        if not MODELS_AVAILABLE:
            # 개발/테스트 모드: 간단한 인증
            user_id = data.get('user_id', 1)
            role = data.get('role', 'admin')
            
            self.client_info[client_id].update({
                'user_id': user_id,
                'role': role,
                'authenticated': True
            })
            
            await self.add_to_room(client_id, role)
            
            await self.send_to_client(client_id, {
                'type': 'auth_success',
                'user_id': user_id,
                'role': role,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"클라이언트 인증 성공 (개발 모드) [{client_id}]: user_{user_id} ({role})")
            return
        
        token = data.get('token')
        if not token:
            await self.send_error(client_id, '인증 토큰이 필요합니다')
            return
        
        try:
            # JWT 토큰 검증 (실제 구현에서는 더 복잡한 검증 필요)
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                await self.send_error(client_id, '유효하지 않은 토큰입니다')
                return
            
            # 사용자 정보 조회
            user = User.query.get(user_id)
            if not user:
                await self.send_error(client_id, '사용자를 찾을 수 없습니다')
                return
            
            # 클라이언트 정보 업데이트
            self.client_info[client_id].update({
                'user_id': user_id,
                'role': user.role,
                'authenticated': True
            })
            
            # 역할별 룸에 추가
            await self.add_to_room(client_id, user.role)
            
            # 인증 성공 응답
            await self.send_to_client(client_id, {
                'type': 'auth_success',
                'user_id': user_id,
                'role': user.role,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"클라이언트 인증 성공 [{client_id}]: {user.username} ({user.role})")
            
        except jwt.ExpiredSignatureError:
            await self.send_error(client_id, '만료된 토큰입니다')
        except jwt.InvalidTokenError:
            await self.send_error(client_id, '유효하지 않은 토큰입니다')
        except Exception as e:
            logger.error(f"인증 처리 오류 [{client_id}]: {e}")
            await self.send_error(client_id, '인증 처리 중 오류가 발생했습니다')
    
    async def handle_heartbeat_response(self, client_id: str, data: Dict):
        """하트비트 응답 처리"""
        self.client_info[client_id]['last_heartbeat'] = time.time()
    
    async def handle_subscribe(self, client_id: str, data: Dict):
        """구독 처리"""
        rooms = data.get('rooms', [])
        
        for room in rooms:
            if room in self.rooms:
                await self.add_to_room(client_id, room)
        
        await self.send_to_client(client_id, {
            'type': 'subscribe_success',
            'rooms': list(self.client_info[client_id]['rooms']),
            'timestamp': datetime.now().isoformat()
        })
    
    async def handle_data_change(self, client_id: str, data: Dict):
        """데이터 변경 알림 처리"""
        if not self.client_info[client_id]['authenticated']:
            await self.send_error(client_id, '인증이 필요합니다')
            return
        
        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        action = data.get('action')  # 'create', 'update', 'delete'
        
        # 다른 클라이언트들에게 데이터 변경 알림
        await self.broadcast_data_update(entity_type, entity_id, action, data.get('payload'))
    
    async def add_to_room(self, client_id: str, room: str):
        """클라이언트를 룸에 추가"""
        if room in self.rooms:
            self.rooms[room].add(client_id)
            self.rooms['all'].add(client_id)
            self.client_info[client_id]['rooms'].add(room)
    
    async def remove_from_rooms(self, client_id: str):
        """클라이언트를 모든 룸에서 제거"""
        for room_clients in self.rooms.values():
            room_clients.discard(client_id)
    
    async def disconnect_client(self, client_id: str):
        """클라이언트 연결 해제"""
        await self.remove_from_rooms(client_id)
        
        if client_id in self.clients:
            del self.clients[client_id]
        
        if client_id in self.client_info:
            del self.client_info[client_id]
        
        logger.info(f"클라이언트 연결 해제 완료: {client_id}")
    
    async def send_to_client(self, client_id: str, message: Dict):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except ConnectionClosed:
                await self.disconnect_client(client_id)
            except Exception as e:
                logger.error(f"클라이언트 메시지 전송 오류 [{client_id}]: {e}")
    
    async def send_error(self, client_id: str, error_message: str):
        """클라이언트에게 오류 메시지 전송"""
        await self.send_to_client(client_id, {
            'type': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def broadcast_to_room(self, room: str, message: Dict):
        """특정 룸의 모든 클라이언트에게 메시지 브로드캐스트"""
        if room in self.rooms:
            for client_id in self.rooms[room].copy():  # copy()로 수정 중 변경 방지
                await self.send_to_client(client_id, message)
    
    async def broadcast_data_update(self, entity_type: str, entity_id: str, action: str, payload: Any = None):
        """데이터 업데이트 브로드캐스트"""
        message = {
            'type': 'data_updated',
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        # 권한에 따라 다른 룸에 전송
        if entity_type in ['industry', 'brand']:
            # 업종/브랜드 변경은 모든 관리자에게 알림
            await self.broadcast_to_room('admin', message)
            await self.broadcast_to_room('super_admin', message)
        elif entity_type == 'store':
            # 매장 변경은 해당 브랜드 관리자와 상위 관리자에게 알림
            await self.broadcast_to_room('brand_manager', message)
            await self.broadcast_to_room('admin', message)
            await self.broadcast_to_room('super_admin', message)
        elif entity_type == 'employee':
            # 직원 변경은 해당 매장 관리자와 상위 관리자에게 알림
            await self.broadcast_to_room('store_manager', message)
            await self.broadcast_to_room('brand_manager', message)
            await self.broadcast_to_room('admin', message)
            await self.broadcast_to_room('super_admin', message)
        else:
            # 기타 변경사항은 모든 관리자에게 알림
            await self.broadcast_to_room('all', message)
    
    async def broadcast_cache_invalidation(self, keys):
        """캐시 무효화 브로드캐스트"""
        message = {
            'type': 'cache_invalidate',
            'keys': keys,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_room('all', message)
    
    async def broadcast_sync_request(self):
        """동기화 요청 브로드캐스트"""
        message = {
            'type': 'sync_request',
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast_to_room('all', message)
    
    async def heartbeat_loop(self):
        """하트비트 루프"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = time.time()
                disconnected_clients = []
                
                # 모든 클라이언트에게 하트비트 전송
                for client_id in list(self.clients.keys()):
                    client_info = self.client_info.get(client_id)
                    if not client_info:
                        continue
                    
                    # 타임아웃 체크
                    if current_time - client_info['last_heartbeat'] > self.heartbeat_timeout:
                        disconnected_clients.append(client_id)
                        continue
                    
                    # 하트비트 전송
                    await self.send_to_client(client_id, {
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # 타임아웃된 클라이언트 연결 해제
                for client_id in disconnected_clients:
                    logger.info(f"하트비트 타임아웃으로 클라이언트 연결 해제: {client_id}")
                    await self.disconnect_client(client_id)
                
            except Exception as e:
                logger.error(f"하트비트 루프 오류: {e}")
    
    def get_stats(self):
        """서버 통계 조회"""
        return {
            'total_clients': len(self.clients),
            'authenticated_clients': sum(1 for info in self.client_info.values() if info['authenticated']),
            'room_counts': {room: len(clients) for room, clients in self.rooms.items()},
            'server_uptime': time.time() - getattr(self, 'start_time', time.time())
        }

# 전역 서버 인스턴스
websocket_server = None

def create_websocket_server(host='localhost', port=8765, secret_key='your-secret-key'):
    """WebSocket 서버 생성"""
    global websocket_server
    websocket_server = DataSyncWebSocketServer(host, port, secret_key)
    return websocket_server

def get_websocket_server():
    """WebSocket 서버 인스턴스 조회"""
    return websocket_server

async def notify_data_change(entity_type: str, entity_id: str, action: str, payload: Any = None):
    """데이터 변경 알림 (외부에서 호출)"""
    if websocket_server:
        await websocket_server.broadcast_data_update(entity_type, entity_id, action, payload)

async def notify_cache_invalidation(keys):
    """캐시 무효화 알림 (외부에서 호출)"""
    if websocket_server:
        await websocket_server.broadcast_cache_invalidation(keys)

async def request_sync():
    """동기화 요청 (외부에서 호출)"""
    if websocket_server:
        await websocket_server.broadcast_sync_request()

if __name__ == '__main__':
    # 개발 환경에서 직접 실행
    import os
    
    host = os.getenv('WS_HOST', 'localhost')
    port = int(os.getenv('WS_PORT', 8765))
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    
    server = create_websocket_server(host, port, secret_key)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("WebSocket 서버 종료")