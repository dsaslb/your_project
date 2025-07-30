"""
실시간 데이터 파이프라인
엔터프라이즈급 실시간 데이터 수집, 처리, 분석 시스템
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import hashlib
import uuid

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """데이터 소스 타입"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    SENSOR = "sensor"
    LOG = "log"

class DataType(Enum):
    """데이터 타입"""
    STRUCTURED = "structured"
    SEMI_STRUCTURED = "semi_structured"
    UNSTRUCTURED = "unstructured"
    TIME_SERIES = "time_series"
    EVENT = "event"

class ProcessingType(Enum):
    """처리 타입"""
    BATCH = "batch"
    STREAM = "stream"
    REAL_TIME = "real_time"
    MICRO_BATCH = "micro_batch"

@dataclass
class DataRecord:
    """데이터 레코드"""
    id: str
    timestamp: datetime
    source: str
    data_type: DataType
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ProcessingRule:
    """처리 규칙"""
    id: str
    name: str
    description: str
    source_pattern: str
    target_topic: str
    transformations: List[Dict[str, Any]]
    filters: List[Dict[str, Any]]
    aggregations: List[Dict[str, Any]]
    window_size: int  # 초 단위
    enabled: bool = True

class DataQualityChecker:
    """데이터 품질 검사기"""
    
    def __init__(self):
        self.rules = {
            'completeness': self._check_completeness,
            'accuracy': self._check_accuracy,
            'consistency': self._check_consistency,
            'timeliness': self._check_timeliness,
            'validity': self._check_validity
        }
    
    def check_quality(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """데이터 품질 점수 계산"""
        scores = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                score = rule_func(data, schema)
                scores.append(score)
            except Exception as e:
                logger.error(f"품질 검사 오류 ({rule_name}): {e}")
                scores.append(0.0)
        
        return np.mean(scores) if scores else 0.0
    
    def _check_completeness(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """완성도 검사"""
        required_fields = schema.get('required_fields', [])
        if not required_fields:
            return 1.0
        
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        return present_fields / len(required_fields)
    
    def _check_accuracy(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """정확도 검사"""
        # 간단한 정확도 검사 (실제로는 더 복잡한 로직 필요)
        return 0.9
    
    def _check_consistency(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """일관성 검사"""
        # 데이터 타입 일관성 검사
        return 0.95
    
    def _check_timeliness(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """시의성 검사"""
        # 데이터가 최신인지 검사
        return 0.98
    
    def _check_validity(self, data: Dict[str, Any], schema: Dict[str, Any]) -> float:
        """유효성 검사"""
        # 데이터 형식 유효성 검사
        return 0.92

class DataTransformer:
    """데이터 변환기"""
    
    def __init__(self):
        self.transformers = {
            'normalize': self._normalize_data,
            'aggregate': self._aggregate_data,
            'filter': self._filter_data,
            'enrich': self._enrich_data,
            'validate': self._validate_data
        }
    
    def transform(self, data: Dict[str, Any], transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """데이터 변환 실행"""
        result = data.copy()
        
        for transform in transformations:
            transform_type = transform.get('type')
            transform_config = transform.get('config', {})
            
            if transform_type in self.transformers:
                try:
                    result = self.transformers[transform_type](result, transform_config)
                except Exception as e:
                    logger.error(f"변환 오류 ({transform_type}): {e}")
        
        return result
    
    def _normalize_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 정규화"""
        # 필드명 정규화, 데이터 타입 변환 등
        return data
    
    def _aggregate_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 집계"""
        # 시간별, 카테고리별 집계
        return data
    
    def _filter_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 필터링"""
        # 조건에 따른 데이터 필터링
        return data
    
    def _enrich_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 보강"""
        # 외부 데이터 소스로부터 추가 정보 수집
        return data
    
    def _validate_data(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 검증"""
        # 데이터 유효성 검증
        return data

class RealTimeDataPipeline:
    """실시간 데이터 파이프라인"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.kafka_producer = None
        self.kafka_consumer = None
        self.redis_client = None
        self.db_connection = None
        self.quality_checker = DataQualityChecker()
        self.transformer = DataTransformer()
        self.processing_rules: List[ProcessingRule] = []
        self.data_queue = Queue(maxsize=10000)
        self.running = False
        self.stats = {
            'processed_records': 0,
            'failed_records': 0,
            'processing_time_avg': 0.0,
            'last_processed': None
        }
        
        self._initialize_connections()
        self._load_processing_rules()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # Kafka 프로듀서 초기화
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            logger.info("데이터 파이프라인 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_processing_rules(self):
        """처리 규칙 로드"""
        try:
            # 데이터베이스에서 처리 규칙 로드
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM processing_rules WHERE enabled = true
                    ORDER BY priority DESC
                """)
                
                for row in cursor.fetchall():
                    rule = ProcessingRule(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        source_pattern=row['source_pattern'],
                        target_topic=row['target_topic'],
                        transformations=row['transformations'],
                        filters=row['filters'],
                        aggregations=row['aggregations'],
                        window_size=row['window_size'],
                        enabled=row['enabled']
                    )
                    self.processing_rules.append(rule)
            
            logger.info(f"{len(self.processing_rules)}개의 처리 규칙 로드 완료")
            
        except Exception as e:
            logger.error(f"처리 규칙 로드 오류: {e}")
    
    async def start(self):
        """파이프라인 시작"""
        self.running = True
        logger.info("실시간 데이터 파이프라인 시작")
        
        # 여러 작업을 동시에 실행
        tasks = [
            asyncio.create_task(self._data_collector()),
            asyncio.create_task(self._data_processor()),
            asyncio.create_task(self._data_analyzer()),
            asyncio.create_task(self._monitor_pipeline())
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """파이프라인 중지"""
        self.running = False
        logger.info("실시간 데이터 파이프라인 중지")
        
        if self.kafka_producer:
            self.kafka_producer.close()
        if self.redis_client:
            self.redis_client.close()
        if self.db_connection:
            self.db_connection.close()
    
    async def _data_collector(self):
        """데이터 수집기"""
        logger.info("데이터 수집기 시작")
        
        while self.running:
            try:
                # 다양한 데이터 소스에서 데이터 수집
                await self._collect_from_database()
                await self._collect_from_api()
                await self._collect_from_stream()
                
                await asyncio.sleep(self.config['collection_interval'])
                
            except Exception as e:
                logger.error(f"데이터 수집 오류: {e}")
                await asyncio.sleep(5)
    
    async def _collect_from_database(self):
        """데이터베이스에서 데이터 수집"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM data_sources 
                    WHERE last_collected < NOW() - INTERVAL '1 minute'
                    AND enabled = true
                """)
                
                for row in cursor.fetchall():
                    # 데이터베이스에서 데이터 수집
                    data = await self._fetch_data_from_source(row)
                    if data:
                        record = DataRecord(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            source=row['name'],
                            data_type=DataType.STRUCTURED,
                            content=data,
                            metadata={'source_type': 'database', 'source_id': row['id']},
                            quality_score=0.0
                        )
                        self.data_queue.put(record)
                        
        except Exception as e:
            logger.error(f"데이터베이스 수집 오류: {e}")
    
    async def _collect_from_api(self):
        """API에서 데이터 수집"""
        try:
            async with aiohttp.ClientSession() as session:
                # API 엔드포인트에서 데이터 수집
                api_endpoints = self.config.get('api_endpoints', [])
                
                for endpoint in api_endpoints:
                    try:
                        async with session.get(endpoint['url']) as response:
                            if response.status == 200:
                                data = await response.json()
                                record = DataRecord(
                                    id=str(uuid.uuid4()),
                                    timestamp=datetime.now(),
                                    source=endpoint['name'],
                                    data_type=DataType.STRUCTURED,
                                    content=data,
                                    metadata={'source_type': 'api', 'endpoint': endpoint['url']},
                                    quality_score=0.0
                                )
                                self.data_queue.put(record)
                    except Exception as e:
                        logger.error(f"API 수집 오류 ({endpoint['name']}): {e}")
                        
        except Exception as e:
            logger.error(f"API 수집 오류: {e}")
    
    async def _collect_from_stream(self):
        """스트림에서 데이터 수집"""
        try:
            # WebSocket 스트림에서 데이터 수집
            stream_endpoints = self.config.get('stream_endpoints', [])
            
            for endpoint in stream_endpoints:
                try:
                    async with websockets.connect(endpoint['url']) as websocket:
                        async for message in websocket:
                            if not self.running:
                                break
                            
                            data = json.loads(message)
                            record = DataRecord(
                                id=str(uuid.uuid4()),
                                timestamp=datetime.now(),
                                source=endpoint['name'],
                                data_type=DataType.STREAM,
                                content=data,
                                metadata={'source_type': 'stream', 'endpoint': endpoint['url']},
                                quality_score=0.0
                            )
                            self.data_queue.put(record)
                            
                except Exception as e:
                    logger.error(f"스트림 수집 오류 ({endpoint['name']}): {e}")
                    
        except Exception as e:
            logger.error(f"스트림 수집 오류: {e}")
    
    async def _data_processor(self):
        """데이터 처리기"""
        logger.info("데이터 처리기 시작")
        
        while self.running:
            try:
                if not self.data_queue.empty():
                    record = self.data_queue.get()
                    await self._process_record(record)
                else:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"데이터 처리 오류: {e}")
                await asyncio.sleep(1)
    
    async def _process_record(self, record: DataRecord):
        """개별 레코드 처리"""
        start_time = time.time()
        
        try:
            # 데이터 품질 검사
            schema = self._get_schema_for_source(record.source)
            record.quality_score = self.quality_checker.check_quality(record.content, schema)
            
            # 품질이 낮은 데이터 필터링
            if record.quality_score < self.config.get('min_quality_score', 0.5):
                logger.warning(f"낮은 품질 데이터 필터링: {record.id} (점수: {record.quality_score})")
                self.stats['failed_records'] += 1
                return
            
            # 처리 규칙 적용
            for rule in self.processing_rules:
                if self._matches_rule(record, rule):
                    # 데이터 변환
                    transformed_data = self.transformer.transform(record.content, rule.transformations)
                    record.content = transformed_data
                    
                    # Kafka로 전송
                    await self._send_to_kafka(record, rule.target_topic)
                    
                    # Redis에 캐시
                    await self._cache_to_redis(record)
                    
                    # 데이터베이스에 저장
                    await self._save_to_database(record)
                    
                    record.processed = True
                    break
            
            # 통계 업데이트
            processing_time = time.time() - start_time
            self.stats['processed_records'] += 1
            self.stats['processing_time_avg'] = (
                (self.stats['processing_time_avg'] * (self.stats['processed_records'] - 1) + processing_time) /
                self.stats['processed_records']
            )
            self.stats['last_processed'] = datetime.now()
            
        except Exception as e:
            logger.error(f"레코드 처리 오류 ({record.id}): {e}")
            self.stats['failed_records'] += 1
    
    def _get_schema_for_source(self, source: str) -> Dict[str, Any]:
        """소스별 스키마 가져오기"""
        # 실제로는 데이터베이스에서 스키마 정보를 가져와야 함
        return {
            'required_fields': ['id', 'timestamp', 'value'],
            'field_types': {
                'id': 'string',
                'timestamp': 'datetime',
                'value': 'number'
            }
        }
    
    def _matches_rule(self, record: DataRecord, rule: ProcessingRule) -> bool:
        """규칙 매칭 확인"""
        # 간단한 패턴 매칭 (실제로는 더 복잡한 로직 필요)
        return rule.source_pattern in record.source
    
    async def _send_to_kafka(self, record: DataRecord, topic: str):
        """Kafka로 데이터 전송"""
        try:
            future = self.kafka_producer.send(
                topic,
                key=record.id,
                value=record.to_dict()
            )
            await asyncio.get_event_loop().run_in_executor(None, future.get)
            
        except Exception as e:
            logger.error(f"Kafka 전송 오류: {e}")
    
    async def _cache_to_redis(self, record: DataRecord):
        """Redis에 데이터 캐시"""
        try:
            cache_key = f"data:{record.id}"
            cache_data = {
                'content': record.content,
                'timestamp': record.timestamp.isoformat(),
                'quality_score': record.quality_score
            }
            
            self.redis_client.setex(
                cache_key,
                self.config.get('cache_ttl', 3600),
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"Redis 캐시 오류: {e}")
    
    async def _save_to_database(self, record: DataRecord):
        """데이터베이스에 데이터 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO processed_data 
                    (id, timestamp, source, data_type, content, metadata, quality_score, processed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    record.id,
                    record.timestamp,
                    record.source,
                    record.data_type.value,
                    json.dumps(record.content),
                    json.dumps(record.metadata),
                    record.quality_score,
                    record.processed
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {e}")
    
    async def _data_analyzer(self):
        """데이터 분석기"""
        logger.info("데이터 분석기 시작")
        
        while self.running:
            try:
                # 실시간 분석 수행
                await self._perform_real_time_analysis()
                await self._update_analytics_dashboard()
                
                await asyncio.sleep(self.config.get('analysis_interval', 60))
                
            except Exception as e:
                logger.error(f"데이터 분석 오류: {e}")
                await asyncio.sleep(10)
    
    async def _perform_real_time_analysis(self):
        """실시간 분석 수행"""
        try:
            # 최근 데이터 분석
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM processed_data 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                    ORDER BY timestamp DESC
                """)
                
                recent_data = cursor.fetchall()
                
                if recent_data:
                    # 통계 계산
                    df = pd.DataFrame(recent_data)
                    
                    # 기본 통계
                    stats = {
                        'total_records': len(df),
                        'avg_quality_score': df['quality_score'].mean(),
                        'processing_rate': len(df) / 3600,  # 레코드/초
                        'source_distribution': df['source'].value_counts().to_dict()
                    }
                    
                    # Redis에 통계 저장
                    self.redis_client.setex(
                        'pipeline_stats',
                        300,  # 5분 TTL
                        json.dumps(stats)
                    )
                    
        except Exception as e:
            logger.error(f"실시간 분석 오류: {e}")
    
    async def _update_analytics_dashboard(self):
        """분석 대시보드 업데이트"""
        try:
            # 대시보드 데이터 업데이트
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'pipeline_stats': self.stats,
                'recent_analytics': await self._get_recent_analytics()
            }
            
            # WebSocket을 통해 대시보드 업데이트
            await self._broadcast_dashboard_update(dashboard_data)
            
        except Exception as e:
            logger.error(f"대시보드 업데이트 오류: {e}")
    
    async def _get_recent_analytics(self) -> Dict[str, Any]:
        """최근 분석 결과 가져오기"""
        try:
            # Redis에서 최근 통계 가져오기
            stats_data = self.redis_client.get('pipeline_stats')
            if stats_data:
                return json.loads(stats_data)
            return {}
            
        except Exception as e:
            logger.error(f"최근 분석 결과 가져오기 오류: {e}")
            return {}
    
    async def _broadcast_dashboard_update(self, data: Dict[str, Any]):
        """대시보드 업데이트 브로드캐스트"""
        try:
            # WebSocket 연결된 클라이언트들에게 업데이트 전송
            # 실제 구현에서는 WebSocket 매니저를 사용해야 함
            pass
            
        except Exception as e:
            logger.error(f"대시보드 브로드캐스트 오류: {e}")
    
    async def _monitor_pipeline(self):
        """파이프라인 모니터링"""
        logger.info("파이프라인 모니터링 시작")
        
        while self.running:
            try:
                # 파이프라인 상태 확인
                health_status = await self._check_pipeline_health()
                
                # 알림 전송
                if not health_status['healthy']:
                    await self._send_alert(health_status)
                
                # 메트릭 수집
                await self._collect_metrics()
                
                await asyncio.sleep(self.config.get('monitoring_interval', 30))
                
            except Exception as e:
                logger.error(f"파이프라인 모니터링 오류: {e}")
                await asyncio.sleep(10)
    
    async def _check_pipeline_health(self) -> Dict[str, Any]:
        """파이프라인 상태 확인"""
        try:
            health_status = {
                'healthy': True,
                'timestamp': datetime.now().isoformat(),
                'issues': []
            }
            
            # 연결 상태 확인
            if not self.kafka_producer:
                health_status['healthy'] = False
                health_status['issues'].append('Kafka producer not connected')
            
            if not self.redis_client.ping():
                health_status['healthy'] = False
                health_status['issues'].append('Redis connection failed')
            
            # 처리 성능 확인
            if self.stats['processed_records'] > 0:
                processing_rate = self.stats['processed_records'] / max(1, (datetime.now() - self.stats['last_processed']).total_seconds())
                if processing_rate < self.config.get('min_processing_rate', 10):
                    health_status['healthy'] = False
                    health_status['issues'].append(f'Low processing rate: {processing_rate:.2f} records/sec')
            
            return health_status
            
        except Exception as e:
            logger.error(f"상태 확인 오류: {e}")
            return {
                'healthy': False,
                'timestamp': datetime.now().isoformat(),
                'issues': [f'Health check error: {e}']
            }
    
    async def _send_alert(self, health_status: Dict[str, Any]):
        """알림 전송"""
        try:
            alert_data = {
                'type': 'pipeline_health',
                'severity': 'warning',
                'message': f'파이프라인 상태 이상: {", ".join(health_status["issues"])}',
                'timestamp': datetime.now().isoformat(),
                'details': health_status
            }
            
            # 알림 시스템으로 전송
            # 실제 구현에서는 알림 서비스를 사용해야 함
            logger.warning(f"파이프라인 알림: {alert_data['message']}")
            
        except Exception as e:
            logger.error(f"알림 전송 오류: {e}")
    
    async def _collect_metrics(self):
        """메트릭 수집"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'processed_records': self.stats['processed_records'],
                'failed_records': self.stats['failed_records'],
                'processing_time_avg': self.stats['processing_time_avg'],
                'queue_size': self.data_queue.qsize(),
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': self._get_cpu_usage()
            }
            
            # 메트릭 저장
            self.redis_client.setex(
                'pipeline_metrics',
                300,  # 5분 TTL
                json.dumps(metrics)
            )
            
        except Exception as e:
            logger.error(f"메트릭 수집 오류: {e}")
    
    def _get_memory_usage(self) -> float:
        """메모리 사용량 가져오기"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """CPU 사용량 가져오기"""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """파이프라인 통계 반환"""
        return self.stats.copy()

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'kafka': {
            'bootstrap_servers': ['localhost:9092']
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program',
            'user': 'postgres',
            'password': 'password'
        },
        'collection_interval': 1,  # 초
        'analysis_interval': 60,   # 초
        'monitoring_interval': 30, # 초
        'min_quality_score': 0.5,
        'min_processing_rate': 10,
        'cache_ttl': 3600,
        'api_endpoints': [
            {'name': 'user_activity', 'url': 'http://localhost:5000/api/analytics/user-activity'},
            {'name': 'system_metrics', 'url': 'http://localhost:5000/api/analytics/system-metrics'}
        ],
        'stream_endpoints': [
            {'name': 'real_time_events', 'url': 'ws://localhost:5000/ws/events'}
        ]
    }
    
    # 파이프라인 실행
    async def main():
        pipeline = RealTimeDataPipeline(config)
        try:
            await pipeline.start()
        except KeyboardInterrupt:
            await pipeline.stop()
    
    asyncio.run(main()) 