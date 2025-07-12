"""
실시간 플러그인 알림 WebSocket 서버
"""

import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime
from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
import threading
import queue

from .plugin_monitoring import plugin_monitor, Alert

logger = logging.getLogger(__name__)

class AlertWebSocketServer:
    """알림 WebSocket 서버"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.client_info: Dict[WebSocketServerProtocol, Dict] = {}
        self.alert_queue = queue.Queue()
        self.server = None
        self.running = False
        
        # 플러그인 모니터에 알림 콜백 등록
        plugin_monitor.add_alert_callback(self._on_alert_generated)
        
    async def start(self):
        """서버 시작"""
        if self.running:
            return
            
        self.running = True
        
        # 알림 처리 스레드 시작
        threading.Thread(target=self._process_alerts, daemon=True).start()
        
        # WebSocket 서버 시작
        self.server = await serve(
            self._handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"알림 WebSocket 서버 시작: ws://{self.host}:{self.port}")
        
        # 서버 실행
        await self.server.wait_closed()
        
    def stop(self):
        """서버 중지"""
        self.running = False
        if self.server:
            self.server.close()
        logger.info("알림 WebSocket 서버 중지")
        
    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """클라이언트 연결 처리"""
        client_id = id(websocket)
        self.clients.add(websocket)
        self.client_info[websocket] = {
            'id': client_id,
            'connected_at': datetime.utcnow(),
            'user_id': None,
            'role': None
        }
        
        logger.info(f"클라이언트 연결: {client_id}")
        
        try:
            # 연결 확인 메시지 전송
            await websocket.send(json.dumps({
                'type': 'connected',
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat()
            }))
            
            # 클라이언트로부터 메시지 수신
            async for message in websocket:
                if isinstance(message, str):
                    await self._handle_message(websocket, message)
                else:
                    # bytes를 문자열로 변환
                    await self._handle_message(websocket, message.decode('utf-8'))
                
        except ConnectionClosed:
            logger.info(f"클라이언트 연결 종료: {client_id}")
        except Exception as e:
            logger.error(f"클라이언트 처리 오류: {e}")
        finally:
            self.clients.discard(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
                
    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """클라이언트 메시지 처리"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'auth':
                # 인증 정보 처리
                self.client_info[websocket]['user_id'] = data.get('user_id')
                self.client_info[websocket]['role'] = data.get('role')
                
                await websocket.send(json.dumps({
                    'type': 'auth_success',
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
            elif msg_type == 'ping':
                # 핑 응답
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
            elif msg_type == 'resolve_alert':
                # 알림 해결 처리
                alert_id = data.get('alert_id')
                if alert_id:
                    plugin_monitor.resolve_alert(alert_id)
                    
            elif msg_type == 'get_metrics':
                # 플러그인 메트릭 요청
                plugin_id = data.get('plugin_id')
                if plugin_id:
                    metrics = plugin_monitor.get_plugin_metrics(plugin_id)
                    if metrics:
                        await websocket.send(json.dumps({
                            'type': 'metrics',
                            'plugin_id': plugin_id,
                            'data': self._serialize_metrics(metrics),
                            'timestamp': datetime.utcnow().isoformat()
                        }))
                        
            elif msg_type == 'get_all_metrics':
                # 모든 플러그인 메트릭 요청
                all_metrics = plugin_monitor.get_all_metrics()
                serialized_metrics = {
                    plugin_id: self._serialize_metrics(metrics)
                    for plugin_id, metrics in all_metrics.items()
                }
                
                await websocket.send(json.dumps({
                    'type': 'all_metrics',
                    'data': serialized_metrics,
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
            elif msg_type == 'get_active_alerts':
                # 활성 알림 요청
                active_alerts = plugin_monitor.get_active_alerts()
                serialized_alerts = [self._serialize_alert(alert) for alert in active_alerts]
                
                await websocket.send(json.dumps({
                    'type': 'active_alerts',
                    'data': serialized_alerts,
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
        except json.JSONDecodeError:
            logger.error(f"잘못된 JSON 메시지: {message}")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            
    def _on_alert_generated(self, alert: Alert):
        """알림 생성 시 호출되는 콜백"""
        # 알림 큐에 추가
        self.alert_queue.put(alert)
        
    def _process_alerts(self):
        """알림 처리 스레드"""
        while self.running:
            try:
                # 큐에서 알림 가져오기 (1초 타임아웃)
                alert = self.alert_queue.get(timeout=1)
                
                # 모든 클라이언트에게 알림 전송
                asyncio.run(self._broadcast_alert(alert))
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"알림 처리 오류: {e}")
                
    async def _broadcast_alert(self, alert: Alert):
        """모든 클라이언트에게 알림 브로드캐스트"""
        if not self.clients:
            return
            
        alert_data = self._serialize_alert(alert)
        message = json.dumps({
            'type': 'alert',
            'data': alert_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 연결이 끊어진 클라이언트 제거
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"클라이언트에게 알림 전송 실패: {e}")
                disconnected_clients.add(client)
                
        # 끊어진 클라이언트 제거
        for client in disconnected_clients:
            self.clients.discard(client)
            if client in self.client_info:
                del self.client_info[client]
                
    def _serialize_alert(self, alert: Alert) -> Dict:
        """알림 객체를 JSON 직렬화 가능한 형태로 변환"""
        return {
            'id': alert.id,
            'plugin_id': alert.plugin_id,
            'plugin_name': alert.plugin_name,
            'level': alert.level.value,
            'message': alert.message,
            'details': alert.details,
            'timestamp': alert.timestamp.isoformat(),
            'resolved': alert.resolved,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
        }
        
    def _serialize_metrics(self, metrics) -> Dict:
        """메트릭 객체를 JSON 직렬화 가능한 형태로 변환"""
        return {
            'plugin_id': metrics.plugin_id,
            'plugin_name': metrics.plugin_name,
            'cpu_usage': metrics.cpu_usage,
            'memory_usage': metrics.memory_usage,
            'response_time': metrics.response_time,
            'error_count': metrics.error_count,
            'request_count': metrics.request_count,
            'last_activity': metrics.last_activity.isoformat(),
            'status': metrics.status,
            'uptime': metrics.uptime
        }
        
    async def broadcast_system_message(self, message: str, level: str = "info"):
        """시스템 메시지 브로드캐스트"""
        if not self.clients:
            return
            
        system_message = json.dumps({
            'type': 'system_message',
            'message': message,
            'level': level,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(system_message)
            except ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"시스템 메시지 전송 실패: {e}")
                disconnected_clients.add(client)
                
        # 끊어진 클라이언트 제거
        for client in disconnected_clients:
            self.clients.discard(client)
            if client in self.client_info:
                del self.client_info[client]

# 전역 WebSocket 서버 인스턴스
alert_server = AlertWebSocketServer()

def start_alert_server():
    """알림 서버 시작 (별도 스레드에서 실행)"""
    def run_server():
        asyncio.run(alert_server.start())
        
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

def stop_alert_server():
    """알림 서버 중지"""
    alert_server.stop() 