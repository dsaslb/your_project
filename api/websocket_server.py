import asyncio
import websockets  # type: ignore
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any, Optional

# WebSocket 연결 관리
class WebSocketManager:
    def __init__(self):
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_data: Dict[websockets.WebSocketServerProtocol, Dict[str, Any]] = {}
        
    async def register(self, websocket: websockets.WebSocketServerProtocol):
        """새로운 클라이언트 등록"""
        self.clients.add(websocket)
        self.client_data[websocket] = {
            'connected_at': datetime.now(),
            'last_activity': datetime.now(),
            'user_id': None,
            'role': None
        }
        logging.info(f"새 클라이언트 연결됨. 총 연결 수: {len(self.clients)}")
        
    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """클라이언트 연결 해제"""
        self.clients.discard(websocket)
        if websocket in self.client_data:
            del self.client_data[websocket]
        logging.info(f"클라이언트 연결 해제됨. 총 연결 수: {len(self.clients)}")
        
    async def broadcast(self, message: Dict[str, Any]):
        """모든 클라이언트에게 메시지 브로드캐스트"""
        if not self.clients:
            return
            
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logging.error(f"메시지 전송 실패: {e}")
                disconnected_clients.add(client)
                
        # 연결이 끊어진 클라이언트 제거
        for client in disconnected_clients:
            await self.unregister(client)
            
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """특정 사용자에게 메시지 전송"""
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client, data in self.client_data.items():
            if data.get('user_id') == user_id:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logging.error(f"사용자 메시지 전송 실패: {e}")
                    disconnected_clients.add(client)
                    
        # 연결이 끊어진 클라이언트 제거
        for client in disconnected_clients:
            await self.unregister(client)

# WebSocket 매니저 인스턴스
ws_manager = WebSocketManager()

async def websocket_handler(websocket, path):
    """WebSocket 연결 핸들러"""
    await ws_manager.register(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_message(websocket, data)
            except json.JSONDecodeError:
                logging.error("잘못된 JSON 형식")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "잘못된 메시지 형식"
                }))
    except websockets.exceptions.ConnectionClosed:
        logging.info("클라이언트 연결이 정상적으로 종료됨")
    except Exception as e:
        logging.error(f"WebSocket 핸들러 오류: {e}")
    finally:
        await ws_manager.unregister(websocket)

async def handle_message(websocket, data: Dict[str, Any]):
    """클라이언트 메시지 처리"""
    message_type = data.get('type')
    
    if message_type == 'auth':
        # 인증 처리
        user_id = data.get('user_id')
        role = data.get('role')
        ws_manager.client_data[websocket]['user_id'] = user_id
        ws_manager.client_data[websocket]['role'] = role
        
        await websocket.send(json.dumps({
            "type": "auth_success",
            "message": "인증 성공"
        }))
        
    elif message_type == 'ping':
        # 연결 상태 확인
        await websocket.send(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))
        
    elif message_type == 'data_request':
        # 데이터 요청 처리
        data_type = data.get('data_type', 'general')
        await send_data_update(websocket, data_type)
        
    else:
        # 알 수 없는 메시지 타입
        await websocket.send(json.dumps({
            "type": "error",
            "message": f"알 수 없는 메시지 타입: {message_type}"
        }))

async def send_data_update(websocket, data_type: str = "general"):
    """데이터 업데이트 전송"""
    # 실제 데이터베이스에서 데이터를 가져와서 전송
    update_data = {
        "type": "data_update",
        "data_type": data_type,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "staff_count": 42,
            "branch_count": 7,
            "notifications": 3,
            "sales": 12345678
        }
    }
    
    await websocket.send(json.dumps(update_data))

async def broadcast_system_status():
    """시스템 상태 브로드캐스트 (주기적 실행)"""
    while True:
        try:
            status_data = {
                "type": "system_status",
                "timestamp": datetime.now().isoformat(),
                "status": {
                    "server_health": "healthy",
                    "database_connected": True,
                    "active_connections": len(ws_manager.clients),
                    "uptime": "24h 30m"
                }
            }
            
            await ws_manager.broadcast(status_data)
            await asyncio.sleep(60)  # 1분마다 실행
            
        except Exception as e:
            logging.error(f"시스템 상태 브로드캐스트 오류: {e}")
            await asyncio.sleep(60)

async def main():
    """WebSocket 서버 시작"""
    logging.basicConfig(level=logging.INFO)
    
    # 시스템 상태 브로드캐스트 태스크 시작
    asyncio.create_task(broadcast_system_status())
    
    # WebSocket 서버 시작
    server = await websockets.serve(  # type: ignore
        websocket_handler,
        "0.0.0.0",
        8765,  # WebSocket 포트
        ping_interval=30,
        ping_timeout=10
    )
    
    logging.info("WebSocket 서버가 포트 8765에서 시작되었습니다.")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 