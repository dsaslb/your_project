import os
import json
import time
import logging
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """메시지 우선순위"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

class MessageStatus(Enum):
    """메시지 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class QueueType(Enum):
    """큐 타입"""
    STANDARD = "standard"
    PRIORITY = "priority"
    DEAD_LETTER = "dead_letter"
    EVENT_STREAM = "event_stream"

@dataclass
class QueueConfig:
    """메시지 큐 설정 클래스"""
    data_dir: str
    max_queue_size: int = 10000
    message_ttl: int = 3600  # 1시간
    retry_attempts: int = 3
    retry_delay: int = 60  # 1분
    cleanup_interval: int = 300  # 5분

@dataclass
class Queue:
    """큐 정보"""
    queue_id: str
    name: str
    queue_type: QueueType
    max_size: int
    current_size: int = 0
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Message:
    """메시지 정보"""
    message_id: str
    queue_id: str
    topic: str
    payload: Any
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Subscription:
    """구독 정보"""
    subscription_id: str
    queue_id: str
    topic: str
    callback_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None

class QueueManager:
    """메시지 큐 관리자 클래스"""
    
    def __init__(self, config: QueueConfig):
        self.config = config
        self.queues: Dict[str, Queue] = {}
        self.messages: Dict[str, Message] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.processing_messages: Dict[str, datetime] = {}
        
        # 설정 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 큐 생성
        self.create_default_queues()
        
        # 기존 데이터 로드
        self.load_data()
        
        # 백그라운드 작업 스레드 시작
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def init_database(self):
        """메시지 큐 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        
        # 데이터베이스 잠금 문제 해결을 위한 설정
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        cursor = conn.cursor()
        
        # 큐 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queues (
                queue_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                queue_type TEXT NOT NULL,
                max_size INTEGER NOT NULL,
                current_size INTEGER NOT NULL DEFAULT 0,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 메시지 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                queue_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'pending',
                retry_count INTEGER NOT NULL DEFAULT 0,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (queue_id) REFERENCES queues (queue_id)
            )
        ''')
        
        # 구독 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id TEXT PRIMARY KEY,
                queue_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                callback_url TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (queue_id) REFERENCES queues (queue_id)
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_queue_id ON messages(queue_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_priority ON messages(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_expires_at ON messages(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_queue_id ON subscriptions(queue_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_topic ON subscriptions(topic)')
        
        conn.commit()
        conn.close()
    
    def create_default_queues(self):
        """기본 큐 생성"""
        default_queues = [
            {"name": "기본 큐", "queue_type": QueueType.STANDARD, "max_size": 1000},
            {"name": "우선순위 큐", "queue_type": QueueType.PRIORITY, "max_size": 500},
            {"name": "이벤트 스트림", "queue_type": QueueType.EVENT_STREAM, "max_size": 5000},
            {"name": "데드 레터 큐", "queue_type": QueueType.DEAD_LETTER, "max_size": 100}
        ]
        
        for queue_data in default_queues:
            self.create_queue(
                name=queue_data["name"],
                queue_type=queue_data["queue_type"],
                max_size=queue_data["max_size"]
            )
    
    def create_queue(self, name: str, queue_type: QueueType, max_size: int = None) -> str:
        """큐 생성"""
        queue_id = str(uuid.uuid4())
        
        if max_size is None:
            max_size = self.config.max_queue_size
        
        queue = Queue(
            queue_id=queue_id,
            name=name,
            queue_type=queue_type,
            max_size=max_size,
            current_size=0,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.queues[queue_id] = queue
        self._save_queue(queue)
        
        logger.info(f"큐 생성: {name} (타입: {queue_type.value})")
        return queue_id
    
    def publish_message(self, queue_id: str, topic: str, payload: Any, 
                       priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """메시지 발행"""
        if queue_id not in self.queues:
            raise ValueError(f"큐를 찾을 수 없습니다: {queue_id}")
        
        queue = self.queues[queue_id]
        if not queue.is_active:
            raise ValueError(f"큐가 비활성화되어 있습니다: {queue.name}")
        
        if queue.current_size >= queue.max_size:
            raise ValueError(f"큐가 가득 찼습니다: {queue.name}")
        
        message_id = str(uuid.uuid4())
        
        # 만료 시간 계산
        expires_at = None
        if self.config.message_ttl > 0:
            expires_at = datetime.utcnow() + timedelta(seconds=self.config.message_ttl)
        
        message = Message(
            message_id=message_id,
            queue_id=queue_id,
            topic=topic,
            payload=payload,
            priority=priority,
            status=MessageStatus.PENDING,
            retry_count=0,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.messages[message_id] = message
        queue.current_size += 1
        queue.updated_at = datetime.utcnow()
        
        self._save_message(message)
        self._save_queue(queue)
        
        logger.info(f"메시지 발행: {topic} -> {queue.name}")
        return message_id
    
    def consume_message(self, queue_id: str, timeout: int = 30) -> Optional[Message]:
        """메시지 소비"""
        if queue_id not in self.queues:
            return None
        
        queue = self.queues[queue_id]
        if not queue.is_active:
            return None
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 큐에서 메시지 찾기
            available_messages = [
                msg for msg in self.messages.values()
                if msg.queue_id == queue_id and msg.status == MessageStatus.PENDING
                and (msg.expires_at is None or msg.expires_at > datetime.utcnow())
            ]
            
            if not available_messages:
                time.sleep(0.1)
                continue
            
            # 우선순위에 따라 정렬
            if queue.queue_type == QueueType.PRIORITY:
                available_messages.sort(key=lambda x: x.priority.value, reverse=True)
            
            # 첫 번째 메시지 선택
            message = available_messages[0]
            message.status = MessageStatus.PROCESSING
            message.updated_at = datetime.utcnow()
            
            self.processing_messages[message.message_id] = datetime.utcnow()
            self._save_message(message)
            
            return message
        
        return None
    
    def complete_message(self, message_id: str, success: bool = True):
        """메시지 완료 처리"""
        if message_id not in self.messages:
            return
        
        message = self.messages[message_id]
        queue = self.queues[message.queue_id]
        
        if success:
            message.status = MessageStatus.COMPLETED
        else:
            message.retry_count += 1
            if message.retry_count >= self.config.retry_attempts:
                message.status = MessageStatus.FAILED
                self._move_to_dead_letter(message)
            else:
                message.status = MessageStatus.PENDING
        
        message.updated_at = datetime.utcnow()
        
        if message_id in self.processing_messages:
            del self.processing_messages[message_id]
        
        queue.current_size = max(0, queue.current_size - 1)
        queue.updated_at = datetime.utcnow()
        
        self._save_message(message)
        self._save_queue(queue)
        
        logger.info(f"메시지 완료: {message_id} (상태: {message.status.value})")
    
    def subscribe(self, queue_id: str, topic: str, callback_url: str = None) -> str:
        """토픽 구독"""
        if queue_id not in self.queues:
            raise ValueError(f"큐를 찾을 수 없습니다: {queue_id}")
        
        subscription_id = str(uuid.uuid4())
        
        subscription = Subscription(
            subscription_id=subscription_id,
            queue_id=queue_id,
            topic=topic,
            callback_url=callback_url,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.subscriptions[subscription_id] = subscription
        self._save_subscription(subscription)
        
        logger.info(f"구독 생성: {topic} -> {self.queues[queue_id].name}")
        return subscription_id
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """큐 통계 조회"""
        stats = {
            'total_queues': len(self.queues),
            'active_queues': len([q for q in self.queues.values() if q.is_active]),
            'total_messages': len(self.messages),
            'pending_messages': len([m for m in self.messages.values() if m.status == MessageStatus.PENDING]),
            'processing_messages': len([m for m in self.messages.values() if m.status == MessageStatus.PROCESSING]),
            'completed_messages': len([m for m in self.messages.values() if m.status == MessageStatus.COMPLETED]),
            'failed_messages': len([m for m in self.messages.values() if m.status == MessageStatus.FAILED]),
            'total_subscriptions': len(self.subscriptions),
            'active_subscriptions': len([s for s in self.subscriptions.values() if s.is_active])
        }
        
        # 큐별 통계
        queue_stats = []
        for queue in self.queues.values():
            queue_messages = [m for m in self.messages.values() if m.queue_id == queue.queue_id]
            
            queue_stats.append({
                'queue_id': queue.queue_id,
                'name': queue.name,
                'type': queue.queue_type.value,
                'current_size': queue.current_size,
                'max_size': queue.max_size,
                'utilization': (queue.current_size / queue.max_size * 100) if queue.max_size > 0 else 0,
                'pending_count': len([m for m in queue_messages if m.status == MessageStatus.PENDING]),
                'processing_count': len([m for m in queue_messages if m.status == MessageStatus.PROCESSING]),
                'completed_count': len([m for m in queue_messages if m.status == MessageStatus.COMPLETED]),
                'failed_count': len([m for m in queue_messages if m.status == MessageStatus.FAILED])
            })
        
        stats['queue_stats'] = queue_stats
        
        return stats
    
    def purge_queue(self, queue_id: str):
        """큐 정리 (모든 메시지 삭제)"""
        if queue_id not in self.queues:
            return
        
        # 큐의 모든 메시지 삭제
        messages_to_delete = [msg_id for msg_id, msg in self.messages.items() if msg.queue_id == queue_id]
        
        for msg_id in messages_to_delete:
            del self.messages[msg_id]
            if msg_id in self.processing_messages:
                del self.processing_messages[msg_id]
        
        queue = self.queues[queue_id]
        queue.current_size = 0
        queue.updated_at = datetime.utcnow()
        
        self._save_queue(queue)
        
        # 데이터베이스에서도 삭제
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages WHERE queue_id = ?', (queue_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"큐 정리 완료: {queue.name}")
    
    def _move_to_dead_letter(self, message: Message):
        """데드 레터 큐로 메시지 이동"""
        dead_letter_queue = None
        for queue in self.queues.values():
            if queue.queue_type == QueueType.DEAD_LETTER:
                dead_letter_queue = queue
                break
        
        if dead_letter_queue:
            dead_letter_message = Message(
                message_id=str(uuid.uuid4()),
                queue_id=dead_letter_queue.queue_id,
                topic=f"dead_letter.{message.topic}",
                payload=message.payload,
                priority=message.priority,
                status=MessageStatus.PENDING,
                retry_count=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.messages[dead_letter_message.message_id] = dead_letter_message
            dead_letter_queue.current_size += 1
            dead_letter_queue.updated_at = datetime.utcnow()
            
            self._save_message(dead_letter_message)
            self._save_queue(dead_letter_queue)
            
            logger.info(f"메시지를 데드 레터 큐로 이동: {message.message_id}")
    
    def _cleanup_worker(self):
        """정리 작업 워커 스레드"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # 만료된 메시지 삭제
                expired_messages = [
                    msg_id for msg_id, msg in self.messages.items()
                    if msg.expires_at and msg.expires_at <= current_time
                ]
                
                for msg_id in expired_messages:
                    message = self.messages[msg_id]
                    queue = self.queues[message.queue_id]
                    
                    del self.messages[msg_id]
                    if msg_id in self.processing_messages:
                        del self.processing_messages[msg_id]
                    
                    queue.current_size = max(0, queue.current_size - 1)
                    queue.updated_at = current_time
                    
                    self._save_queue(queue)
                
                # 오래된 처리 중인 메시지 복구
                stale_threshold = current_time - timedelta(minutes=30)
                stale_messages = [
                    msg_id for msg_id, processing_time in self.processing_messages.items()
                    if processing_time <= stale_threshold
                ]
                
                for msg_id in stale_messages:
                    if msg_id in self.messages:
                        message = self.messages[msg_id]
                        message.status = MessageStatus.PENDING
                        message.updated_at = current_time
                        self._save_message(message)
                    
                    del self.processing_messages[msg_id]
                
                if expired_messages or stale_messages:
                    logger.info(f"정리 완료: 만료 메시지 {len(expired_messages)}개, 복구 메시지 {len(stale_messages)}개")
                
                time.sleep(self.config.cleanup_interval)
                
            except Exception as e:
                logger.error(f"정리 작업 오류: {str(e)}")
                time.sleep(60)
    
    def load_data(self):
        """데이터 로드"""
        try:
            self._load_queues()
            self._load_messages()
            self._load_subscriptions()
            
            logger.info(f"메시지 큐 데이터 로드 완료: {len(self.queues)}개 큐, {len(self.messages)}개 메시지")
            
        except Exception as e:
            logger.error(f"메시지 큐 데이터 로드 오류: {str(e)}")
    
    # 데이터베이스 저장 메서드들
    def _save_queue(self, queue: Queue):
        """큐를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO queues 
            (queue_id, name, queue_type, max_size, current_size, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            queue.queue_id,
            queue.name,
            queue.queue_type.value,
            queue.max_size,
            queue.current_size,
            queue.is_active,
            queue.created_at.isoformat(),
            queue.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_message(self, message: Message):
        """메시지를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO messages 
            (message_id, queue_id, topic, payload, priority, status, retry_count, 
             expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.message_id,
            message.queue_id,
            message.topic,
            json.dumps(message.payload, ensure_ascii=False),
            message.priority.value,
            message.status.value,
            message.retry_count,
            message.expires_at.isoformat() if message.expires_at else None,
            message.created_at.isoformat(),
            message.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_subscription(self, subscription: Subscription):
        """구독을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO subscriptions 
            (subscription_id, queue_id, topic, callback_url, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            subscription.subscription_id,
            subscription.queue_id,
            subscription.topic,
            subscription.callback_url,
            subscription.is_active,
            subscription.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _load_queues(self):
        """데이터베이스에서 큐 로드"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM queues')
        rows = cursor.fetchall()
        
        for row in rows:
            queue = Queue(
                queue_id=row[0],
                name=row[1],
                queue_type=QueueType(row[2]),
                max_size=row[3],
                current_size=row[4],
                is_active=bool(row[5]),
                created_at=datetime.fromisoformat(row[6]),
                updated_at=datetime.fromisoformat(row[7])
            )
            self.queues[queue.queue_id] = queue
        
        conn.close()
    
    def _load_messages(self):
        """데이터베이스에서 메시지 로드"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM messages')
        rows = cursor.fetchall()
        
        for row in rows:
            message = Message(
                message_id=row[0],
                queue_id=row[1],
                topic=row[2],
                payload=json.loads(row[3]),
                priority=MessagePriority(row[4]),
                status=MessageStatus(row[5]),
                retry_count=row[6],
                expires_at=datetime.fromisoformat(row[7]) if row[7] else None,
                created_at=datetime.fromisoformat(row[8]),
                updated_at=datetime.fromisoformat(row[9])
            )
            self.messages[message.message_id] = message
            
            # 처리 중인 메시지 복원
            if message.status == MessageStatus.PROCESSING:
                self.processing_messages[message.message_id] = message.updated_at
        
        conn.close()
    
    def _load_subscriptions(self):
        """데이터베이스에서 구독 로드"""
        db_path = os.path.join(self.config.data_dir, 'message_queue.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM subscriptions')
        rows = cursor.fetchall()
        
        for row in rows:
            subscription = Subscription(
                subscription_id=row[0],
                queue_id=row[1],
                topic=row[2],
                callback_url=row[3],
                is_active=bool(row[4]),
                created_at=datetime.fromisoformat(row[5])
            )
            self.subscriptions[subscription.subscription_id] = subscription
        
        conn.close() 