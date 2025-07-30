"""
🔄 시스템 통합 코어 모듈

모든 완성된 시스템들을 통합하여 엔터프라이즈급 통합 플랫폼을 제공합니다.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import redis
import psycopg2
from sqlalchemy import create_engine, text
from prometheus_client import Counter, Histogram, Gauge

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """시스템 상태 정보"""
    name: str
    status: str  # 'healthy', 'warning', 'error'
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None

class SystemIntegrationCore:
    """시스템 통합 코어 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        # PostgreSQL 연결
        self.db_engine = create_engine(
            config.get('database_url', 'postgresql://localhost/your_program')
        )
        
        # Prometheus 메트릭
        self.request_counter = Counter('system_integration_requests_total', 'Total requests')
        self.response_time = Histogram('system_integration_response_time', 'Response time')
        self.system_health = Gauge('system_integration_health', 'System health status')
        
        # 시스템 상태 저장소
        self.system_status: Dict[str, SystemStatus] = {}
        
        # 통합된 서비스 목록
        self.integrated_services = {
            'api_gateway': {
                'url': config.get('api_gateway_url', 'http://localhost:8000'),
                'health_endpoint': '/health',
                'weight': 1.0
            },
            'ai_ml_platform': {
                'url': config.get('ai_ml_url', 'http://localhost:8001'),
                'health_endpoint': '/health',
                'weight': 0.8
            },
            'data_analysis': {
                'url': config.get('data_analysis_url', 'http://localhost:8002'),
                'health_endpoint': '/health',
                'weight': 0.9
            },
            'blockchain': {
                'url': config.get('blockchain_url', 'http://localhost:8003'),
                'health_endpoint': '/health',
                'weight': 0.7
            },
            'iot_platform': {
                'url': config.get('iot_url', 'http://localhost:8004'),
                'health_endpoint': '/health',
                'weight': 0.6
            },
            'security_system': {
                'url': config.get('security_url', 'http://localhost:8005'),
                'health_endpoint': '/health',
                'weight': 1.0
            },
            'mobile_app_backend': {
                'url': config.get('mobile_backend_url', 'http://localhost:8006'),
                'health_endpoint': '/health',
                'weight': 0.8
            }
        }
    
    async def check_system_health(self, service_name: str) -> SystemStatus:
        """개별 시스템 헬스 체크"""
        service_config = self.integrated_services.get(service_name)
        if not service_config:
            return SystemStatus(
                name=service_name,
                status='error',
                response_time=0.0,
                last_check=datetime.now(),
                error_message='Service not configured'
            )
        
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{service_config['url']}{service_config['health_endpoint']}"
                async with session.get(url, timeout=5) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        status = 'healthy' if data.get('status') == 'ok' else 'warning'
                        return SystemStatus(
                            name=service_name,
                            status=status,
                            response_time=response_time,
                            last_check=datetime.now(),
                            error_message=data.get('message')
                        )
                    else:
                        return SystemStatus(
                            name=service_name,
                            status='error',
                            response_time=response_time,
                            last_check=datetime.now(),
                            error_message=f"HTTP {response.status}"
                        )
        except Exception as e:
            response_time = time.time() - start_time
            return SystemStatus(
                name=service_name,
                status='error',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_all_systems(self) -> Dict[str, SystemStatus]:
        """모든 시스템 헬스 체크"""
        tasks = []
        for service_name in self.integrated_services.keys():
            tasks.append(self.check_system_health(service_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, SystemStatus):
                service_name = list(self.integrated_services.keys())[i]
                self.system_status[service_name] = result
        
        # 전체 시스템 상태 업데이트
        healthy_count = sum(1 for status in self.system_status.values() 
                          if status.status == 'healthy')
        total_count = len(self.system_status)
        overall_health = healthy_count / total_count if total_count > 0 else 0
        self.system_health.set(overall_health)
        
        return self.system_status
    
    async def route_request(self, service_name: str, endpoint: str, 
                          method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """통합 요청 라우팅"""
        self.request_counter.inc()
        
        service_config = self.integrated_services.get(service_name)
        if not service_config:
            raise ValueError(f"Service {service_name} not found")
        
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{service_config['url']}{endpoint}"
                
                if method.upper() == 'GET':
                    async with session.get(url, timeout=10) as response:
                        result = await response.json()
                elif method.upper() == 'POST':
                    async with session.post(url, json=data, timeout=10) as response:
                        result = await response.json()
                elif method.upper() == 'PUT':
                    async with session.put(url, json=data, timeout=10) as response:
                        result = await response.json()
                elif method.upper() == 'DELETE':
                    async with session.delete(url, timeout=10) as response:
                        result = await response.json()
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response_time = time.time() - start_time
                self.response_time.observe(response_time)
                
                return {
                    'success': True,
                    'data': result,
                    'response_time': response_time,
                    'service': service_name
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self.response_time.observe(response_time)
            
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time,
                'service': service_name
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': self.system_health._value.get(),
            'total_requests': self.request_counter._value.get(),
            'systems': {}
        }
        
        for service_name, status in self.system_status.items():
            metrics['systems'][service_name] = {
                'status': status.status,
                'response_time': status.response_time,
                'last_check': status.last_check.isoformat(),
                'error_message': status.error_message
            }
        
        return metrics
    
    async def cache_data(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Redis 캐시에 데이터 저장"""
        try:
            serialized_data = json.dumps(data)
            self.redis_client.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            logger.error(f"Cache error: {e}")
            return False
    
    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Redis 캐시에서 데이터 조회"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def log_integration_event(self, event_type: str, details: Dict[str, Any]) -> bool:
        """통합 이벤트 로깅"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'details': details
            }
            
            # PostgreSQL에 로그 저장
            with self.db_engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO integration_logs (timestamp, event_type, details)
                    VALUES (:timestamp, :event_type, :details)
                """), log_entry)
                conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Logging error: {e}")
            return False
    
    async def start_monitoring(self):
        """시스템 모니터링 시작"""
        logger.info("Starting system integration monitoring...")
        
        while True:
            try:
                # 모든 시스템 헬스 체크
                await self.check_all_systems()
                
                # 메트릭 수집
                metrics = await self.get_system_metrics()
                
                # 캐시에 메트릭 저장
                await self.cache_data('system_metrics', metrics, ttl=300)
                
                # 로그 이벤트
                await self.log_integration_event('health_check', {
                    'healthy_systems': sum(1 for s in self.system_status.values() 
                                         if s.status == 'healthy'),
                    'total_systems': len(self.system_status)
                })
                
                # 30초 대기
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)

class IntegrationManager:
    """통합 관리자 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.core = SystemIntegrationCore(config)
        self.monitoring_task = None
    
    async def start(self):
        """통합 시스템 시작"""
        logger.info("Starting system integration...")
        
        # 모니터링 태스크 시작
        self.monitoring_task = asyncio.create_task(self.core.start_monitoring())
        
        logger.info("System integration started successfully")
    
    async def stop(self):
        """통합 시스템 중지"""
        logger.info("Stopping system integration...")
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("System integration stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            'integration_status': 'running',
            'systems': self.core.system_status,
            'metrics': await self.core.get_system_metrics()
        }

# 사용 예시
if __name__ == "__main__":
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'database_url': 'postgresql://localhost/your_program',
        'api_gateway_url': 'http://localhost:8000',
        'ai_ml_url': 'http://localhost:8001',
        'data_analysis_url': 'http://localhost:8002',
        'blockchain_url': 'http://localhost:8003',
        'iot_url': 'http://localhost:8004',
        'security_url': 'http://localhost:8005',
        'mobile_backend_url': 'http://localhost:8006'
    }
    
    async def main():
        manager = IntegrationManager(config)
        await manager.start()
        
        try:
            # 1분간 실행
            await asyncio.sleep(60)
        finally:
            await manager.stop()
    
    asyncio.run(main()) 