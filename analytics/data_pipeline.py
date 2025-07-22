import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from queue import Queue, PriorityQueue
import warnings
warnings.filterwarnings('ignore')

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from kafka import KafkaProducer, KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

@dataclass
class DataEvent:
    """데이터 이벤트 클래스"""
    event_id: str
    event_type: str
    data: Any
    timestamp: datetime
    source: str
    priority: int = 1
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

@dataclass
class PipelineConfig:
    """파이프라인 설정 클래스"""
    batch_size: int = 100
    batch_timeout: int = 60  # 초
    max_retries: int = 3
    retry_delay: int = 5  # 초
    enable_streaming: bool = True
    enable_batch_processing: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 초
    data_validation: bool = True
    error_handling: str = "continue"  # continue, stop, retry

class DataPipeline:
    """실시간 데이터 파이프라인"""
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.logger = self._setup_logger()
        
        # 데이터 큐
        self.input_queue = PriorityQueue()
        self.processing_queue = Queue()
        self.output_queue = Queue()
        self.error_queue = Queue()
        
        # 처리 상태
        self.is_running = False
        self.processing_thread = None
        self.batch_processor = None
        
        # 데이터 저장소
        self.data_cache = {}
        self.batch_buffer = deque(maxlen=self.config.batch_size * 2)
        
        # 통계
        self.stats = {
            "total_events": 0,
            "processed_events": 0,
            "failed_events": 0,
            "batch_count": 0,
            "stream_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # 프로세서들
        self.preprocessors = []
        self.transformers = []
        self.validators = []
        self.loaders = []
        
        # Redis 연결 (선택사항)
        self.redis_client = None
        if REDIS_AVAILABLE and self.config.cache_enabled:
            self._setup_redis()
        
        # Kafka 연결 (선택사항)
        self.kafka_producer = None
        self.kafka_consumer = None
        if KAFKA_AVAILABLE:
            self._setup_kafka()
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('data_pipeline')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_redis(self):
        """Redis 설정"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Redis 연결 성공")
        except Exception as e:
            self.logger.warning(f"Redis 연결 실패: {e}")
            self.redis_client = None
    
    def _setup_kafka(self):
        """Kafka 설정"""
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.logger.info("Kafka Producer 연결 성공")
        except Exception as e:
            self.logger.warning(f"Kafka Producer 연결 실패: {e}")
            self.kafka_producer = None
    
    def add_preprocessor(self, processor: Callable):
        """전처리기 추가"""
        self.preprocessors.append(processor)
        self.logger.info(f"전처리기 추가: {processor.__name__}")
    
    def add_transformer(self, transformer: Callable):
        """변환기 추가"""
        self.transformers.append(transformer)
        self.logger.info(f"변환기 추가: {transformer.__name__}")
    
    def add_validator(self, validator: Callable):
        """검증기 추가"""
        self.validators.append(validator)
        self.logger.info(f"검증기 추가: {validator.__name__}")
    
    def add_loader(self, loader: Callable):
        """로더 추가"""
        self.loaders.append(loader)
        self.logger.info(f"로더 추가: {loader.__name__}")
    
    def start(self):
        """파이프라인 시작"""
        if self.is_running:
            self.logger.warning("파이프라인이 이미 실행 중입니다.")
            return
        
        self.is_running = True
        
        # 스트리밍 처리 스레드 시작
        self.processing_thread = threading.Thread(target=self._streaming_processor)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # 배치 처리 스레드 시작
        if self.config.enable_batch_processing:
            self.batch_processor = threading.Thread(target=self._batch_processor)
            self.batch_processor.daemon = True
            self.batch_processor.start()
        
        self.logger.info("데이터 파이프라인 시작됨")
    
    def stop(self):
        """파이프라인 중지"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=10)
        
        if self.batch_processor:
            self.batch_processor.join(timeout=10)
        
        self.logger.info("데이터 파이프라인 중지됨")
    
    def ingest_data(self, data: Any, event_type: str = "data", 
                   source: str = "unknown", priority: int = 1, 
                   metadata: Dict = None) -> str:
        """데이터 수집"""
        event_id = f"event_{int(time.time() * 1000000)}"
        
        event = DataEvent(
            event_id=event_id,
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source,
            priority=priority,
            metadata=metadata or {}
        )
        
        # 우선순위 큐에 추가 (낮은 숫자가 높은 우선순위)
        self.input_queue.put((priority, event))
        
        self.stats["total_events"] += 1
        
        self.logger.debug(f"데이터 수집: {event_id} ({event_type})")
        
        return event_id
    
    def _streaming_processor(self):
        """스트리밍 처리 루프"""
        while self.is_running:
            try:
                # 입력 큐에서 이벤트 가져오기
                try:
                    priority, event = self.input_queue.get(timeout=1)
                except:
                    continue
                
                # 실시간 처리
                if self.config.enable_streaming:
                    self._process_event(event)
                
                # 배치 버퍼에 추가
                if self.config.enable_batch_processing:
                    self.batch_buffer.append(event)
                
            except Exception as e:
                self.logger.error(f"스트리밍 처리 오류: {e}")
    
    def _batch_processor(self):
        """배치 처리 루프"""
        last_batch_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # 배치 크기 또는 시간 조건 확인
                if (len(self.batch_buffer) >= self.config.batch_size or 
                    current_time - last_batch_time >= self.config.batch_timeout):
                    
                    if self.batch_buffer:
                        batch_events = list(self.batch_buffer)
                        self.batch_buffer.clear()
                        
                        self._process_batch(batch_events)
                        last_batch_time = current_time
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"배치 처리 오류: {e}")
    
    def _process_event(self, event: DataEvent):
        """개별 이벤트 처리"""
        try:
            processed_data = event.data
            
            # 전처리
            for preprocessor in self.preprocessors:
                processed_data = preprocessor(processed_data, event)
            
            # 변환
            for transformer in self.transformers:
                processed_data = transformer(processed_data, event)
            
            # 검증
            if self.config.data_validation:
                for validator in self.validators:
                    if not validator(processed_data, event):
                        raise ValueError(f"데이터 검증 실패: {event.event_id}")
            
            # 적재
            for loader in self.loaders:
                loader(processed_data, event)
            
            # 출력 큐에 추가
            self.output_queue.put({
                "event_id": event.event_id,
                "processed_data": processed_data,
                "timestamp": datetime.now().isoformat()
            })
            
            self.stats["processed_events"] += 1
            self.stats["stream_count"] += 1
            
            # Kafka로 전송 (선택사항)
            if self.kafka_producer:
                self._send_to_kafka(event, processed_data)
            
            self.logger.debug(f"이벤트 처리 완료: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"이벤트 처리 실패: {event.event_id} - {e}")
            self.stats["failed_events"] += 1
            
            # 오류 큐에 추가
            self.error_queue.put({
                "event_id": event.event_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            # 오류 처리 정책
            if self.config.error_handling == "stop":
                self.stop()
            elif self.config.error_handling == "retry":
                # 재시도 로직 (간단한 구현)
                pass
    
    def _process_batch(self, events: List[DataEvent]):
        """배치 처리"""
        try:
            # 배치 데이터 준비
            batch_data = [event.data for event in events]
            
            # 배치 전처리
            for preprocessor in self.preprocessors:
                batch_data = [preprocessor(data, event) for data, event in zip(batch_data, events)]
            
            # 배치 변환
            for transformer in self.transformers:
                batch_data = [transformer(data, event) for data, event in zip(batch_data, events)]
            
            # 배치 검증
            if self.config.data_validation:
                for i, (data, event) in enumerate(zip(batch_data, events)):
                    for validator in self.validators:
                        if not validator(data, event):
                            raise ValueError(f"배치 데이터 검증 실패: {event.event_id}")
            
            # 배치 적재
            for loader in self.loaders:
                for data, event in zip(batch_data, events):
                    loader(data, event)
            
            self.stats["batch_count"] += 1
            self.stats["processed_events"] += len(events)
            
            self.logger.info(f"배치 처리 완료: {len(events)}개 이벤트")
            
        except Exception as e:
            self.logger.error(f"배치 처리 실패: {e}")
            self.stats["failed_events"] += len(events)
    
    def _send_to_kafka(self, event: DataEvent, processed_data: Any):
        """Kafka로 데이터 전송"""
        if not self.kafka_producer:
            return
        
        try:
            message = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "data": processed_data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source
            }
            
            self.kafka_producer.send('data_pipeline', message)
            self.logger.debug(f"Kafka 전송: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Kafka 전송 실패: {e}")
    
    def get_processed_data(self, timeout: float = 1.0) -> Optional[Dict]:
        """처리된 데이터 가져오기"""
        try:
            return self.output_queue.get(timeout=timeout)
        except:
            return None
    
    def get_all_processed_data(self) -> List[Dict]:
        """모든 처리된 데이터 가져오기"""
        data = []
        while not self.output_queue.empty():
            data.append(self.output_queue.get_nowait())
        return data
    
    def get_errors(self) -> List[Dict]:
        """오류 데이터 가져오기"""
        errors = []
        while not self.error_queue.empty():
            errors.append(self.error_queue.get_nowait())
        return errors
    
    def cache_data(self, key: str, data: Any, ttl: int = None):
        """데이터 캐싱"""
        if not self.config.cache_enabled:
            return
        
        ttl = ttl or self.config.cache_ttl
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data))
            except Exception as e:
                self.logger.warning(f"Redis 캐시 실패: {e}")
        else:
            # 메모리 캐시
            self.data_cache[key] = {
                "data": data,
                "expires_at": datetime.now() + timedelta(seconds=ttl)
            }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """캐시된 데이터 가져오기"""
        if not self.config.cache_enabled:
            return None
        
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    self.stats["cache_hits"] += 1
                    return json.loads(data)
                else:
                    self.stats["cache_misses"] += 1
                    return None
            except Exception as e:
                self.logger.warning(f"Redis 캐시 조회 실패: {e}")
                return None
        else:
            # 메모리 캐시
            cached = self.data_cache.get(key)
            if cached and cached["expires_at"] > datetime.now():
                self.stats["cache_hits"] += 1
                return cached["data"]
            else:
                self.stats["cache_misses"] += 1
                if key in self.data_cache:
                    del self.data_cache[key]
                return None
    
    def get_stats(self) -> Dict:
        """파이프라인 통계 조회"""
        return {
            **self.stats,
            "queue_sizes": {
                "input_queue": self.input_queue.qsize(),
                "processing_queue": self.processing_queue.qsize(),
                "output_queue": self.output_queue.qsize(),
                "error_queue": self.error_queue.qsize(),
                "batch_buffer": len(self.batch_buffer)
            },
            "is_running": self.is_running,
            "cache_size": len(self.data_cache) if not self.redis_client else None
        }
    
    def clear_cache(self):
        """캐시 정리"""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                self.logger.warning(f"Redis 캐시 정리 실패: {e}")
        else:
            self.data_cache.clear()
        
        self.logger.info("캐시 정리 완료")

# 기본 프로세서들
def default_preprocessor(data: Any, event: DataEvent) -> Any:
    """기본 전처리기"""
    if isinstance(data, dict):
        # 타임스탬프 추가
        data['processed_at'] = datetime.now().isoformat()
        data['event_id'] = event.event_id
    return data

def default_transformer(data: Any, event: DataEvent) -> Any:
    """기본 변환기"""
    if isinstance(data, dict):
        # 데이터 정규화
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip().lower()
    return data

def default_validator(data: Any, event: DataEvent) -> bool:
    """기본 검증기"""
    if data is None:
        return False
    if isinstance(data, dict) and not data:
        return False
    return True

def default_loader(data: Any, event: DataEvent):
    """기본 로더"""
    # 여기서 데이터베이스나 파일에 저장
    pass

# 사용 예시
if __name__ == "__main__":
    # 파이프라인 설정
    config = PipelineConfig(
        batch_size=50,
        batch_timeout=30,
        enable_streaming=True,
        enable_batch_processing=True,
        cache_enabled=True
    )
    
    # 파이프라인 생성
    pipeline = DataPipeline(config)
    
    # 프로세서 추가
    pipeline.add_preprocessor(default_preprocessor)
    pipeline.add_transformer(default_transformer)
    pipeline.add_validator(default_validator)
    pipeline.add_loader(default_loader)
    
    # 파이프라인 시작
    pipeline.start()
    
    # 데이터 수집
    sample_data = {
        "user_id": "user123",
        "action": "purchase",
        "amount": 100.0,
        "product": "item001"
    }
    
    event_id = pipeline.ingest_data(
        sample_data,
        event_type="purchase",
        source="web",
        priority=1
    )
    
    # 처리된 데이터 확인
    time.sleep(2)
    processed_data = pipeline.get_processed_data()
    if processed_data:
        print(f"처리된 데이터: {processed_data}")
    
    # 통계 확인
    stats = pipeline.get_stats()
    print(f"파이프라인 통계: {stats}")
    
    # 파이프라인 중지
    pipeline.stop() 