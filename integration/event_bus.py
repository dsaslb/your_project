"""
이벤트 기반 아키텍처 시스템
시스템 간 통신을 위한 이벤트 버스, 메시지 큐, 실시간 알림 기능
"""

import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
import queue
import weakref
from collections import defaultdict
import pickle

# 로깅 설정
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """이벤트 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class EventStatus(Enum):
    """이벤트 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Event:
    """이벤트 데이터 클래스"""
    id: str
    type: str
    source: str
    target: Optional[str]
    data: Dict[str, Any]
    priority: EventPriority
    timestamp: datetime
    expires_at: Optional[datetime]
    status: EventStatus
    metadata: Dict[str, Any]

@dataclass
class EventHandler:
    """이벤트 핸들러"""
    id: str
    event_type: str
    handler: Callable
    priority: int
    is_async: bool
    timeout: int
    retry_count: int
    created_at: datetime

@dataclass
class EventSubscription:
    """이벤트 구독"""
    id: str
    subscriber_id: str
    event_type: str
    handler_id: str
    created_at: datetime
    is_active: bool

class EventBus:
    """이벤트 버스 시스템"""
    
    def __init__(self, db_path: str = "data/integration/events.db"):
        self.db_path = db_path
        self.event_queue = queue.PriorityQueue()
        self.handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.running_events: Dict[str, Event] = {}
        self.event_history: List[Event] = []
        self.max_history_size = 10000
        
        # 비동기 이벤트 처리
        self.async_loop = None
        self.async_thread = None
        
        # 실시간 알림
        self.websocket_connections: Dict[str, Any] = {}
        self.notification_handlers: List[Callable] = []
        
        # 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self.initialize_database()
        
        # 이벤트 처리 스레드 시작
        self.start_event_processor()
        
        # 비동기 이벤트 처리 시작
        self.start_async_processor()
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 이벤트 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        target TEXT,
                        data TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        expires_at TEXT,
                        status TEXT NOT NULL,
                        metadata TEXT NOT NULL
                    )
                """)
                
                # 이벤트 핸들러 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_handlers (
                        id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        handler_name TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        is_async INTEGER NOT NULL,
                        timeout INTEGER NOT NULL,
                        retry_count INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # 이벤트 구독 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_subscriptions (
                        id TEXT PRIMARY KEY,
                        subscriber_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        handler_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        is_active INTEGER NOT NULL
                    )
                """)
                
                # 이벤트 실행 로그 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS event_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL,
                        handler_id TEXT,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (event_id) REFERENCES events (id)
                    )
                """)
                
                # 인덱스 생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_handlers_type ON event_handlers(event_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_type ON event_subscriptions(event_type)")
                
                conn.commit()
                logger.info("이벤트 버스 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def start_event_processor(self):
        """이벤트 처리 스레드 시작"""
        def processor():
            while True:
                try:
                    # 우선순위 큐에서 이벤트 가져오기
                    priority, event = self.event_queue.get(timeout=1)
                    
                    if event:
                        self._process_event(event)
                    
                    self.event_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"이벤트 처리 오류: {str(e)}")
        
        thread = threading.Thread(target=processor, daemon=True)
        thread.start()
        logger.info("이벤트 처리 스레드 시작")
    
    def start_async_processor(self):
        """비동기 이벤트 처리 시작"""
        def async_processor():
            self.async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.async_loop)
            self.async_loop.run_forever()
        
        self.async_thread = threading.Thread(target=async_processor, daemon=True)
        self.async_thread.start()
        logger.info("비동기 이벤트 처리 스레드 시작")
    
    def publish_event(self, event_type: str, source: str, data: Dict[str, Any], 
                     target: str = None, priority: EventPriority = EventPriority.NORMAL,
                     expires_at: datetime = None, metadata: Dict[str, Any] = None) -> str:
        """이벤트 발행"""
        try:
            event_id = str(uuid.uuid4())
            now = datetime.now()
            
            event = Event(
                id=event_id,
                type=event_type,
                source=source,
                target=target,
                data=data,
                priority=priority,
                timestamp=now,
                expires_at=expires_at,
                status=EventStatus.PENDING,
                metadata=metadata or {}
            )
            
            # 이벤트 저장
            self._save_event(event)
            
            # 이벤트 큐에 추가 (우선순위 기반)
            self.event_queue.put((priority.value, event))
            
            # 이벤트 히스토리에 추가
            self.event_history.append(event)
            if len(self.event_history) > self.max_history_size:
                self.event_history.pop(0)
            
            # 실시간 알림 발송
            self._notify_subscribers(event)
            
            logger.info(f"이벤트 발행: {event_type} (ID: {event_id})")
            return event_id
            
        except Exception as e:
            logger.error(f"이벤트 발행 오류: {str(e)}")
            raise
    
    def subscribe(self, event_type: str, handler: Callable, subscriber_id: str = None,
                 priority: int = 0, is_async: bool = False, timeout: int = 30, 
                 retry_count: int = 3) -> str:
        """이벤트 구독"""
        try:
            handler_id = str(uuid.uuid4())
            subscriber_id = subscriber_id or str(uuid.uuid4())
            
            event_handler = EventHandler(
                id=handler_id,
                event_type=event_type,
                handler=handler,
                priority=priority,
                is_async=is_async,
                timeout=timeout,
                retry_count=retry_count,
                created_at=datetime.now()
            )
            
            # 핸들러 등록
            self.handlers[event_type].append(event_handler)
            self.handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
            
            # 구독 정보 저장
            subscription = EventSubscription(
                id=str(uuid.uuid4()),
                subscriber_id=subscriber_id,
                event_type=event_type,
                handler_id=handler_id,
                created_at=datetime.now(),
                is_active=True
            )
            
            self.subscriptions[event_type].append(subscription)
            self._save_subscription(subscription)
            
            logger.info(f"이벤트 구독 등록: {event_type} (핸들러: {handler_id})")
            return handler_id
            
        except Exception as e:
            logger.error(f"이벤트 구독 오류: {str(e)}")
            raise
    
    def unsubscribe(self, handler_id: str) -> bool:
        """이벤트 구독 해제"""
        try:
            # 핸들러 찾기 및 제거
            for event_type, handlers in self.handlers.items():
                for handler in handlers[:]:
                    if handler.id == handler_id:
                        handlers.remove(handler)
                        break
            
            # 구독 정보 비활성화
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE event_subscriptions 
                    SET is_active = 0 
                    WHERE handler_id = ?
                """, (handler_id,))
                conn.commit()
            
            logger.info(f"이벤트 구독 해제: {handler_id}")
            return True
            
        except Exception as e:
            logger.error(f"이벤트 구독 해제 오류: {str(e)}")
            return False
    
    def _process_event(self, event: Event):
        """이벤트 처리"""
        try:
            # 이벤트 상태를 처리 중으로 변경
            event.status = EventStatus.PROCESSING
            self._update_event_status(event.id, EventStatus.PROCESSING)
            
            # 만료된 이벤트인지 확인
            if event.expires_at and datetime.now() > event.expires_at:
                event.status = EventStatus.CANCELLED
                self._update_event_status(event.id, EventStatus.CANCELLED)
                return
            
            # 해당 이벤트 타입의 핸들러들 찾기
            handlers = self.handlers.get(event.type, [])
            
            if not handlers:
                logger.warning(f"이벤트 핸들러를 찾을 수 없습니다: {event.type}")
                event.status = EventStatus.COMPLETED
                self._update_event_status(event.id, EventStatus.COMPLETED)
                return
            
            # 핸들러 실행
            for handler in handlers:
                try:
                    if handler.is_async:
                        # 비동기 핸들러 실행
                        self._execute_async_handler(handler, event)
                    else:
                        # 동기 핸들러 실행
                        self._execute_sync_handler(handler, event)
                        
                except Exception as e:
                    logger.error(f"핸들러 실행 오류: {str(e)}")
                    self._log_event(event.id, handler.id, "ERROR", str(e))
            
            # 이벤트 완료
            event.status = EventStatus.COMPLETED
            self._update_event_status(event.id, EventStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"이벤트 처리 오류: {str(e)}")
            event.status = EventStatus.FAILED
            self._update_event_status(event.id, EventStatus.FAILED, str(e))
    
    def _execute_sync_handler(self, handler: EventHandler, event: Event):
        """동기 핸들러 실행"""
        try:
            start_time = time.time()
            
            # 핸들러 실행
            result = handler.handler(event)
            
            execution_time = time.time() - start_time
            
            # 실행 로그 기록
            self._log_event(event.id, handler.id, "INFO", 
                          f"핸들러 실행 완료 (소요시간: {execution_time:.2f}초)")
            
            return result
            
        except Exception as e:
            logger.error(f"동기 핸들러 실행 오류: {str(e)}")
            self._log_event(event.id, handler.id, "ERROR", str(e))
            raise
    
    def _execute_async_handler(self, handler: EventHandler, event: Event):
        """비동기 핸들러 실행"""
        try:
            if self.async_loop:
                # 비동기 루프에 태스크 추가
                future = asyncio.run_coroutine_threadsafe(
                    self._async_handler_wrapper(handler, event),
                    self.async_loop
                )
                
                # 타임아웃 설정
                try:
                    result = future.result(timeout=handler.timeout)
                    self._log_event(event.id, handler.id, "INFO", "비동기 핸들러 실행 완료")
                    return result
                except asyncio.TimeoutError:
                    logger.error(f"비동기 핸들러 타임아웃: {handler.id}")
                    self._log_event(event.id, handler.id, "ERROR", "타임아웃")
                    
        except Exception as e:
            logger.error(f"비동기 핸들러 실행 오류: {str(e)}")
            self._log_event(event.id, handler.id, "ERROR", str(e))
    
    async def _async_handler_wrapper(self, handler: EventHandler, event: Event):
        """비동기 핸들러 래퍼"""
        try:
            if asyncio.iscoroutinefunction(handler.handler):
                return await handler.handler(event)
            else:
                # 동기 함수를 비동기로 실행
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, handler.handler, event)
        except Exception as e:
            logger.error(f"비동기 핸들러 래퍼 오류: {str(e)}")
            raise
    
    def _notify_subscribers(self, event: Event):
        """구독자들에게 실시간 알림"""
        try:
            # 웹소켓 연결된 클라이언트들에게 알림
            notification_data = {
                'event_id': event.id,
                'event_type': event.type,
                'source': event.source,
                'data': event.data,
                'timestamp': event.timestamp.isoformat(),
                'priority': event.priority.value
            }
            
            # 웹소켓 연결된 클라이언트들에게 전송
            for connection_id, connection in self.websocket_connections.items():
                try:
                    if hasattr(connection, 'send'):
                        connection.send(json.dumps(notification_data))
                except Exception as e:
                    logger.error(f"웹소켓 알림 전송 오류: {str(e)}")
                    # 연결 제거
                    del self.websocket_connections[connection_id]
            
            # 추가 알림 핸들러들 실행
            for handler in self.notification_handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"알림 핸들러 오류: {str(e)}")
                    
        except Exception as e:
            logger.error(f"구독자 알림 오류: {str(e)}")
    
    def add_websocket_connection(self, connection_id: str, connection: Any):
        """웹소켓 연결 추가"""
        self.websocket_connections[connection_id] = connection
        logger.info(f"웹소켓 연결 추가: {connection_id}")
    
    def remove_websocket_connection(self, connection_id: str):
        """웹소켓 연결 제거"""
        if connection_id in self.websocket_connections:
            del self.websocket_connections[connection_id]
            logger.info(f"웹소켓 연결 제거: {connection_id}")
    
    def add_notification_handler(self, handler: Callable):
        """알림 핸들러 추가"""
        self.notification_handlers.append(handler)
        logger.info("알림 핸들러 추가")
    
    def _save_event(self, event: Event):
        """이벤트 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO events 
                    (id, type, source, target, data, priority, timestamp, expires_at, status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id, event.type, event.source, event.target,
                    json.dumps(event.data), event.priority.value,
                    event.timestamp.isoformat(),
                    event.expires_at.isoformat() if event.expires_at else None,
                    event.status.value, json.dumps(event.metadata)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"이벤트 저장 오류: {str(e)}")
    
    def _save_subscription(self, subscription: EventSubscription):
        """구독 정보 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO event_subscriptions 
                    (id, subscriber_id, event_type, handler_id, created_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    subscription.id, subscription.subscriber_id, subscription.event_type,
                    subscription.handler_id, subscription.created_at.isoformat(),
                    1 if subscription.is_active else 0
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"구독 정보 저장 오류: {str(e)}")
    
    def _update_event_status(self, event_id: str, status: EventStatus, error_message: str = None):
        """이벤트 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE events 
                    SET status = ? 
                    WHERE id = ?
                """, (status.value, event_id))
                conn.commit()
        except Exception as e:
            logger.error(f"이벤트 상태 업데이트 오류: {str(e)}")
    
    def _log_event(self, event_id: str, handler_id: str, level: str, message: str, metadata: Dict = None):
        """이벤트 로그 기록"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO event_logs 
                    (event_id, handler_id, level, message, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event_id, handler_id, level, message,
                    datetime.now().isoformat(),
                    json.dumps(metadata) if metadata else None
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"이벤트 로그 기록 오류: {str(e)}")
    
    def get_events(self, event_type: str = None, status: EventStatus = None, 
                  limit: int = 100, offset: int = 0) -> List[Event]:
        """이벤트 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND type = ?"
                    params.append(event_type)
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = Event(
                        id=row[0], type=row[1], source=row[2], target=row[3],
                        data=json.loads(row[4]), priority=EventPriority(row[5]),
                        timestamp=datetime.fromisoformat(row[6]),
                        expires_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        status=EventStatus(row[8]), metadata=json.loads(row[9])
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"이벤트 조회 오류: {str(e)}")
            return []
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """이벤트 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전체 이벤트 수
                cursor.execute("SELECT COUNT(*) FROM events")
                total_events = cursor.fetchone()[0]
                
                # 상태별 이벤트 수
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM events 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # 타입별 이벤트 수
                cursor.execute("""
                    SELECT type, COUNT(*) 
                    FROM events 
                    GROUP BY type
                """)
                type_counts = dict(cursor.fetchall())
                
                # 오늘 발행된 이벤트 수
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM events 
                    WHERE DATE(timestamp) = DATE('now')
                """)
                today_events = cursor.fetchone()[0]
                
                # 활성 구독 수
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM event_subscriptions 
                    WHERE is_active = 1
                """)
                active_subscriptions = cursor.fetchone()[0]
                
                return {
                    'total_events': total_events,
                    'status_counts': status_counts,
                    'type_counts': type_counts,
                    'today_events': today_events,
                    'active_subscriptions': active_subscriptions,
                    'active_handlers': sum(len(handlers) for handlers in self.handlers.values()),
                    'websocket_connections': len(self.websocket_connections)
                }
                
        except Exception as e:
            logger.error(f"이벤트 통계 조회 오류: {str(e)}")
            return {}
    
    def cleanup_old_events(self, days: int = 30):
        """오래된 이벤트 정리"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 오래된 이벤트 삭제
                cursor.execute("""
                    DELETE FROM events 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"오래된 이벤트 {deleted_count}개 정리 완료")
                return deleted_count
                
        except Exception as e:
            logger.error(f"이벤트 정리 오류: {str(e)}")
            return 0
    
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """이벤트 히스토리 조회"""
        return self.event_history[-limit:]
    
    def broadcast_message(self, message: str, message_type: str = "info", 
                         target_connections: List[str] = None):
        """브로드캐스트 메시지 전송"""
        try:
            broadcast_data = {
                'type': 'broadcast',
                'message': message,
                'message_type': message_type,
                'timestamp': datetime.now().isoformat()
            }
            
            if target_connections:
                # 특정 연결들에게만 전송
                for connection_id in target_connections:
                    if connection_id in self.websocket_connections:
                        try:
                            self.websocket_connections[connection_id].send(
                                json.dumps(broadcast_data)
                            )
                        except Exception as e:
                            logger.error(f"브로드캐스트 전송 오류: {str(e)}")
            else:
                # 모든 연결에게 전송
                for connection_id, connection in self.websocket_connections.items():
                    try:
                        connection.send(json.dumps(broadcast_data))
                    except Exception as e:
                        logger.error(f"브로드캐스트 전송 오류: {str(e)}")
            
            logger.info(f"브로드캐스트 메시지 전송: {message}")
            
        except Exception as e:
            logger.error(f"브로드캐스트 메시지 전송 오류: {str(e)}")
    
    def shutdown(self):
        """이벤트 버스 종료"""
        try:
            # 비동기 루프 종료
            if self.async_loop:
                self.async_loop.call_soon_threadsafe(self.async_loop.stop)
            
            # 웹소켓 연결 종료
            for connection_id, connection in self.websocket_connections.items():
                try:
                    if hasattr(connection, 'close'):
                        connection.close()
                except Exception as e:
                    logger.error(f"웹소켓 연결 종료 오류: {str(e)}")
            
            logger.info("이벤트 버스 종료 완료")
            
        except Exception as e:
            logger.error(f"이벤트 버스 종료 오류: {str(e)}") 