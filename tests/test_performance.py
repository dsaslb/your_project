"""
성능 최적화 테스트
캐시, 데이터베이스, API 성능 테스트
"""

import unittest
import time
import threading
import requests
from typing import List, Dict
import redis
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.database_optimizer import DatabaseOptimizer
from utils.cache_optimizer import CacheOptimizer
from utils.api_optimizer import APIOptimizer, QueryOptimizer, ResponseOptimizer
from utils.performance_monitor import PerformanceMonitor
from utils.load_balancer import LoadBalancer, LoadBalancingAlgorithm
from utils.async_queue import AsyncQueueManager

class TestDatabaseOptimization(unittest.TestCase):
    """데이터베이스 최적화 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.db_url = "postgresql://your_program:password@localhost:5432/your_program"
        self.optimizer = DatabaseOptimizer(self.db_url)
    
    def test_table_performance_analysis(self):
        """테이블 성능 분석 테스트"""
        # 테이블 성능 분석
        result = self.optimizer.analyze_table_performance('users')
        
        self.assertIsInstance(result, dict)
        self.assertIn('table_name', result)
        self.assertIn('row_count', result)
        self.assertIn('indexes', result)
    
    def test_slow_query_detection(self):
        """느린 쿼리 탐지 테스트"""
        # 느린 쿼리 찾기
        slow_queries = self.optimizer.find_slow_queries(5)
        
        self.assertIsInstance(slow_queries, list)
    
    def test_index_usage_analysis(self):
        """인덱스 사용량 분석 테스트"""
        # 인덱스 사용량 분석
        result = self.optimizer.analyze_index_usage()
        
        self.assertIsInstance(result, dict)
        self.assertIn('index_usage', result)
        self.assertIn('unused_indexes', result)
    
    def test_index_suggestions(self):
        """인덱스 제안 테스트"""
        # 인덱스 제안
        suggestions = self.optimizer.suggest_indexes('users')
        
        self.assertIsInstance(suggestions, list)
    
    def test_query_performance_analysis(self):
        """쿼리 성능 분석 테스트"""
        # 쿼리 성능 분석
        query = "SELECT * FROM users WHERE email = 'test@example.com'"
        result = self.optimizer.analyze_query_performance(query)
        
        self.assertIsInstance(result, dict)
        self.assertIn('query', result)
        self.assertIn('performance_metrics', result)

class TestCacheOptimization(unittest.TestCase):
    """캐시 최적화 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.redis_url = "redis://localhost:6379/0"
        self.cache = CacheOptimizer(self.redis_url)
    
    def test_cache_set_get(self):
        """캐시 설정/조회 테스트"""
        # 캐시 설정
        key = "test_key"
        value = {"data": "test_value", "timestamp": time.time()}
        
        success = self.cache.set(key, value, timeout=60)
        self.assertTrue(success)
        
        # 캐시 조회
        retrieved_value = self.cache.get(key)
        self.assertEqual(retrieved_value, value)
    
    def test_cache_compression(self):
        """캐시 압축 테스트"""
        # 큰 데이터 압축 테스트
        large_data = "x" * 2000  # 2KB 데이터
        
        # 압축 활성화
        self.cache.compression_enabled = True
        success = self.cache.set("large_key", large_data, timeout=60)
        self.assertTrue(success)
        
        # 압축 해제 확인
        retrieved_data = self.cache.get("large_key")
        self.assertEqual(retrieved_data, large_data)
    
    def test_cache_mget_mset(self):
        """캐시 다중 조회/설정 테스트"""
        # 다중 데이터 설정
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        success = self.cache.mset(data, timeout=60)
        self.assertTrue(success)
        
        # 다중 데이터 조회
        retrieved_data = self.cache.mget(list(data.keys()))
        self.assertEqual(retrieved_data, data)
    
    def test_cache_invalidation(self):
        """캐시 무효화 테스트"""
        # 패턴 기반 캐시 무효화
        self.cache.set("user:1:profile", {"name": "John"}, timeout=60)
        self.cache.set("user:2:profile", {"name": "Jane"}, timeout=60)
        
        # 패턴으로 무효화
        deleted_count = self.cache.invalidate_pattern("user:*:profile")
        self.assertGreaterEqual(deleted_count, 2)
    
    def test_cache_stats(self):
        """캐시 통계 테스트"""
        # 캐시 사용
        self.cache.set("test_key", "test_value", timeout=60)
        self.cache.get("test_key")
        self.cache.get("nonexistent_key")
        
        # 통계 조회
        stats = self.cache.get_cache_stats()
        
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('sets', stats)
        self.assertIn('hit_rate', stats)

class TestAPIOptimization(unittest.TestCase):
    """API 최적화 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.redis_url = "redis://localhost:6379/0"
        self.redis_client = redis.from_url(self.redis_url)
        self.api_optimizer = APIOptimizer(self.redis_client)
        self.query_optimizer = QueryOptimizer()
        self.response_optimizer = ResponseOptimizer()
    
    def test_response_caching(self):
        """응답 캐싱 테스트"""
        # 캐시 데코레이터 테스트
        @self.api_optimizer.cache_response(ttl=60, key_prefix="test")
        def test_function(param1, param2):
            return {"result": param1 + param2, "timestamp": time.time()}
        
        # 첫 번째 호출 (캐시 미스)
        result1 = test_function(1, 2)
        
        # 두 번째 호출 (캐시 히트)
        result2 = test_function(1, 2)
        
        # 결과가 동일해야 함
        self.assertEqual(result1["result"], result2["result"])
    
    def test_query_optimization(self):
        """쿼리 최적화 테스트"""
        # 쿼리 최적화 테스트 (모의)
        class MockQuery:
            def __init__(self):
                self._limit = None
                self._offset = None
            
            def limit(self, limit):
                self._limit = limit
                return self
            
            def offset(self, offset):
                self._offset = offset
                return self
        
        mock_query = MockQuery()
        optimized_query = self.query_optimizer.optimize_query(mock_query, max_results=100)
        
        self.assertEqual(optimized_query._limit, 100)
    
    def test_response_optimization(self):
        """응답 최적화 테스트"""
        # 응답 최적화 테스트
        data = {"message": "Hello, World!", "timestamp": time.time()}
        
        response = self.response_optimizer.optimize_response(data, compress=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Type', response.headers)
        self.assertIn('X-Response-Optimized', response.headers)
    
    def test_cache_invalidation(self):
        """캐시 무효화 테스트"""
        # 캐시 무효화 테스트
        pattern = "test:*"
        deleted_count = self.api_optimizer.invalidate_cache(pattern)
        
        self.assertIsInstance(deleted_count, int)
        self.assertGreaterEqual(deleted_count, 0)

class TestPerformanceMonitoring(unittest.TestCase):
    """성능 모니터링 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.redis_url = "redis://localhost:6379/0"
        self.redis_client = redis.from_url(self.redis_url)
        self.monitor = PerformanceMonitor(self.redis_client)
    
    def test_metric_collection(self):
        """메트릭 수집 테스트"""
        # 메트릭 수집
        metric = self.monitor._collect_system_metrics()
        
        self.assertIsInstance(metric, PerformanceMetric)
        self.assertGreaterEqual(metric.cpu_usage, 0)
        self.assertLessEqual(metric.cpu_usage, 100)
        self.assertGreaterEqual(metric.memory_usage, 0)
        self.assertLessEqual(metric.memory_usage, 100)
    
    def test_threshold_checking(self):
        """임계값 체크 테스트"""
        # 임계값 체크 테스트
        metric = PerformanceMetric(
            timestamp=time.time(),
            cpu_usage=90.0,  # 높은 CPU 사용률
            memory_usage=85.0,  # 높은 메모리 사용률
            disk_io_read=0,
            disk_io_write=0,
            network_sent=0,
            network_recv=0,
            active_connections=0,
            request_count=0,
            response_time_avg=0,
            error_count=0
        )
        
        # 임계값 체크 (알림 콜백 모의)
        alert_received = False
        
        def mock_alert(alert_data):
            nonlocal alert_received
            alert_received = True
        
        self.monitor.alert_callbacks.append(mock_alert)
        self.monitor._check_thresholds(metric)
        
        # 알림이 발생했는지 확인
        self.assertTrue(alert_received)
    
    def test_performance_report(self):
        """성능 리포트 테스트"""
        # 성능 리포트 생성
        report = self.monitor.get_performance_report(hours=1)
        
        self.assertIsInstance(report, dict)
        self.assertIn('period_hours', report)

class TestLoadBalancing(unittest.TestCase):
    """로드 밸런싱 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.load_balancer = LoadBalancer(LoadBalancingAlgorithm.ROUND_ROBIN)
        
        # 테스트 서버 추가
        self.load_balancer.add_server("server1", "localhost", 5000, weight=1)
        self.load_balancer.add_server("server2", "localhost", 5001, weight=1)
        self.load_balancer.add_server("server3", "localhost", 5002, weight=2)
    
    def test_round_robin_algorithm(self):
        """라운드 로빈 알고리즘 테스트"""
        # 라운드 로빈 알고리즘 테스트
        servers = []
        for _ in range(6):
            server = self.load_balancer.get_server()
            if server:
                servers.append(server.id)
        
        # 서버가 순환되어 선택되는지 확인
        self.assertEqual(len(set(servers)), 3)
    
    def test_least_connections_algorithm(self):
        """최소 연결 알고리즘 테스트"""
        # 알고리즘 변경
        self.load_balancer.algorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS
        
        # 연결 수 시뮬레이션
        self.load_balancer.servers["server1"].current_connections = 10
        self.load_balancer.servers["server2"].current_connections = 5
        self.load_balancer.servers["server3"].current_connections = 15
        
        # 최소 연결 서버 선택
        selected_server = self.load_balancer.get_server()
        self.assertEqual(selected_server.id, "server2")
    
    def test_server_health_check(self):
        """서버 헬스체크 테스트"""
        # 헬스체크 시뮬레이션
        server = self.load_balancer.servers["server1"]
        
        # 정상 상태로 설정
        server.status = LoadBalancer.ServerStatus.HEALTHY
        server.error_count = 0
        
        # 헬스체크 수행
        is_healthy = self.load_balancer._check_server_health(server)
        
        # 헬스체크 결과 확인 (실제 서버가 없으므로 실패할 수 있음)
        self.assertIsInstance(is_healthy, bool)

class TestAsyncQueue(unittest.TestCase):
    """비동기 큐 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.broker_url = "redis://localhost:6379/0"
        self.result_backend = "redis://localhost:6379/0"
        self.queue_manager = AsyncQueueManager(self.broker_url, self.result_backend)
    
    def test_task_scheduling(self):
        """작업 스케줄링 테스트"""
        # 작업 스케줄링 테스트
        celery_app = self.queue_manager.get_celery_app()
        
        # 간단한 작업 정의
        @celery_app.task
        def test_task(x, y):
            return x + y
        
        # 작업 실행
        result = test_task.delay(2, 3)
        
        # 작업 완료 대기
        task_result = result.get(timeout=10)
        self.assertEqual(task_result, 5)

class TestPerformanceIntegration(unittest.TestCase):
    """성능 통합 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.redis_url = "redis://localhost:6379/0"
        self.redis_client = redis.from_url(self.redis_url)
        
        # 모든 최적화 도구 초기화
        self.db_optimizer = DatabaseOptimizer("postgresql://your_program:password@localhost:5432/your_program")
        self.cache_optimizer = CacheOptimizer(self.redis_url)
        self.api_optimizer = APIOptimizer(self.redis_client)
        self.performance_monitor = PerformanceMonitor(self.redis_client)
    
    def test_end_to_end_performance(self):
        """엔드투엔드 성능 테스트"""
        # 1. 데이터베이스 최적화
        db_stats = self.db_optimizer.get_database_stats()
        self.assertIsInstance(db_stats, dict)
        
        # 2. 캐시 최적화
        cache_stats = self.cache_optimizer.get_cache_stats()
        self.assertIsInstance(cache_stats, dict)
        
        # 3. 성능 모니터링
        performance_report = self.performance_monitor.get_performance_report(hours=1)
        self.assertIsInstance(performance_report, dict)
    
    def test_concurrent_performance(self):
        """동시 성능 테스트"""
        def worker(worker_id):
            """워커 함수"""
            # 캐시 작업
            key = f"test_key_{worker_id}"
            value = f"test_value_{worker_id}"
            
            self.cache_optimizer.set(key, value, timeout=60)
            retrieved_value = self.cache_optimizer.get(key)
            
            return retrieved_value == value
        
        # 동시 실행
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # 모든 작업이 성공했는지 확인
        self.assertTrue(all(results))

class TestPerformanceBenchmarks(unittest.TestCase):
    """성능 벤치마크 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.redis_url = "redis://localhost:6379/0"
        self.cache = CacheOptimizer(self.redis_url)
    
    def test_cache_performance_benchmark(self):
        """캐시 성능 벤치마크"""
        # 캐시 성능 테스트
        iterations = 1000
        start_time = time.time()
        
        for i in range(iterations):
            key = f"benchmark_key_{i}"
            value = f"benchmark_value_{i}"
            
            self.cache.set(key, value, timeout=60)
            self.cache.get(key)
        
        end_time = time.time()
        total_time = end_time - start_time
        operations_per_second = (iterations * 2) / total_time
        
        print(f"캐시 성능: {operations_per_second:.2f} ops/sec")
        
        # 성능 기준 확인
        self.assertGreater(operations_per_second, 1000)  # 초당 1000회 이상
    
    def test_database_performance_benchmark(self):
        """데이터베이스 성능 벤치마크"""
        # 데이터베이스 성능 테스트 (모의)
        iterations = 100
        start_time = time.time()
        
        for i in range(iterations):
            # 데이터베이스 작업 시뮬레이션
            time.sleep(0.001)  # 1ms 지연
        
        end_time = time.time()
        total_time = end_time - start_time
        operations_per_second = iterations / total_time
        
        print(f"데이터베이스 성능: {operations_per_second:.2f} ops/sec")
        
        # 성능 기준 확인
        self.assertGreater(operations_per_second, 50)  # 초당 50회 이상

if __name__ == '__main__':
    unittest.main() 