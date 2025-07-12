"""
플러그인 모니터링 시스템 성능 테스트
"""

import time
import requests
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
import logging
import argparse
import sys
from datetime import datetime
import websocket  # type: ignore
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTest:
    """성능 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def test_api_endpoint(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """단일 API 엔드포인트 테스트"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data or {}, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms
            
            return {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code < 400,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                'endpoint': endpoint,
                'method': method,
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_metrics_endpoint(self, plugin_id: str = "test_plugin") -> Dict[str, Any]:
        """메트릭 엔드포인트 테스트"""
        return self.test_api_endpoint(f"/api/advanced-monitoring/metrics/{plugin_id}?hours=24")
    
    def test_trends_endpoint(self, plugin_id: str = "test_plugin") -> Dict[str, Any]:
        """트렌드 엔드포인트 테스트"""
        return self.test_api_endpoint(f"/api/advanced-monitoring/trends/{plugin_id}")
    
    def test_analytics_endpoint(self, plugin_id: str = "test_plugin") -> Dict[str, Any]:
        """분석 엔드포인트 테스트"""
        return self.test_api_endpoint(f"/api/advanced-monitoring/analytics/{plugin_id}?hours=24")
    
    def test_plugin_registration(self) -> Dict[str, Any]:
        """플러그인 등록 테스트"""
        data = {
            "plugin_id": f"test_plugin_{int(time.time())}",
            "plugin_name": "테스트 플러그인"
        }
        return self.test_api_endpoint("/api/advanced-monitoring/register-plugin", "POST", data)
    
    def test_metrics_update(self, plugin_id: str = "test_plugin") -> Dict[str, Any]:
        """메트릭 업데이트 테스트"""
        data = {
            "plugin_id": plugin_id,
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time": 1.2,
                "error_count": 3,
                "request_count": 150,
                "throughput": 100.5,
                "active_connections": 25,
                "disk_read_bytes": 1024000,
                "disk_write_bytes": 512000,
                "network_rx_bytes": 2048000,
                "network_tx_bytes": 1024000
            }
        }
        return self.test_api_endpoint("/api/advanced-monitoring/update-metrics", "POST", data)
    
    def run_concurrent_tests(self, test_func, num_threads: int = 10, num_requests: int = 100) -> List[Dict[str, Any]]:
        """동시 테스트 실행"""
        results = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(test_func) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Test failed: {e}")
                    results.append({
                        'error': str(e),
                        'success': False,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return results
    
    def run_load_test(self, test_type: str, num_threads: int = 10, num_requests: int = 100) -> Dict[str, Any]:
        """부하 테스트 실행"""
        logger.info(f"Starting {test_type} load test with {num_threads} threads, {num_requests} requests")
        
        self.start_time = time.time()
        
        if test_type == "metrics":
            results = self.run_concurrent_tests(self.test_metrics_endpoint, num_threads, num_requests)
        elif test_type == "trends":
            results = self.run_concurrent_tests(self.test_trends_endpoint, num_threads, num_requests)
        elif test_type == "analytics":
            results = self.run_concurrent_tests(self.test_analytics_endpoint, num_threads, num_requests)
        elif test_type == "registration":
            results = self.run_concurrent_tests(self.test_plugin_registration, num_threads, num_requests)
        elif test_type == "update":
            results = self.run_concurrent_tests(self.test_metrics_update, num_threads, num_requests)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        self.end_time = time.time()
        
        return self.analyze_results(results, test_type)
    
    def analyze_results(self, results: List[Dict[str, Any]], test_type: str) -> Dict[str, Any]:
        """결과 분석"""
        successful_requests = [r for r in results if r.get('success', False)]
        failed_requests = [r for r in results if not r.get('success', False)]
        
        response_times = [r['response_time'] for r in successful_requests if 'response_time' in r]
        
        analysis = {
            'test_type': test_type,
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(results) * 100 if results else 0,
            'total_time': self.end_time - self.start_time if self.end_time and self.start_time else 0,
            'requests_per_second': len(results) / (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        }
        
        if response_times:
            analysis.update({
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
                'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
            })
        
        if failed_requests:
            error_counts = {}
            for req in failed_requests:
                error = req.get('error', 'Unknown error')
                error_counts[error] = error_counts.get(error, 0) + 1
            analysis['error_breakdown'] = error_counts
        
        return analysis
    
    def run_stress_test(self, test_type: str, max_threads: int = 50, max_requests: int = 1000) -> Dict[str, Any]:
        """스트레스 테스트 실행"""
        logger.info(f"Starting stress test for {test_type}")
        
        stress_results = []
        
        # 점진적으로 부하 증가
        for threads in [5, 10, 20, 30, 40, 50]:
            if threads > max_threads:
                break
                
            requests_per_thread = max_requests // threads
            if requests_per_thread < 1:
                requests_per_thread = 1
            
            logger.info(f"Testing with {threads} threads, {requests_per_thread} requests per thread")
            
            result = self.run_load_test(test_type, threads, requests_per_thread)
            result['threads'] = threads
            result['requests_per_thread'] = requests_per_thread
            
            stress_results.append(result)
            
            # 성능이 급격히 저하되면 중단
            if result['success_rate'] < 80 or result['avg_response_time'] > 5000:
                logger.warning(f"Performance degradation detected at {threads} threads")
                break
        
        return {
            'stress_test_type': test_type,
            'results': stress_results,
            'max_sustainable_load': self.find_max_sustainable_load(stress_results)
        }
    
    def find_max_sustainable_load(self, stress_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """최대 지속 가능한 부하 찾기"""
        sustainable_results = [
            r for r in stress_results 
            if r['success_rate'] >= 95 and r['avg_response_time'] <= 2000
        ]
        
        if not sustainable_results:
            return {
                'threads': 0,
                'requests_per_second': 0,
                'avg_response_time': 0
            }
        
        # 가장 높은 성능의 결과 반환
        best_result = max(sustainable_results, key=lambda x: x['requests_per_second'])
        
        return {
            'threads': best_result['threads'],
            'requests_per_second': best_result['requests_per_second'],
            'avg_response_time': best_result['avg_response_time']
        }
    
    def run_websocket_test(self, num_connections: int = 100) -> Dict[str, Any]:
        """WebSocket 연결 테스트"""
        
        logger.info(f"Starting WebSocket test with {num_connections} connections")
        
        results = []
        connections = []
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                results.append({
                    'type': 'message',
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error parsing message: {e}")
        
        def on_error(ws, error):
            results.append({
                'type': 'error',
                'error': str(error),
                'timestamp': datetime.now().isoformat()
            })
        
        def on_close(ws, close_status_code, close_msg):
            results.append({
                'type': 'close',
                'status_code': close_status_code,
                'message': close_msg,
                'timestamp': datetime.now().isoformat()
            })
        
        def on_open(ws):
            results.append({
                'type': 'open',
                'timestamp': datetime.now().isoformat()
            })
            
            # 인증 메시지 전송
            ws.send(json.dumps({
                'type': 'auth',
                'user_id': 'test_user',
                'role': 'admin'
            }))
        
        # WebSocket 연결 생성
        start_time = time.time()
        
        for i in range(num_connections):
            try:
                ws = websocket.WebSocketApp(
                    "ws://localhost:8765",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                
                wst = threading.Thread(target=ws.run_forever)
                wst.daemon = True
                wst.start()
                
                connections.append(ws)
                
            except Exception as e:
                logger.error(f"Failed to create WebSocket connection {i}: {e}")
        
        # 연결 완료 대기
        time.sleep(5)
        
        # 메시지 전송 테스트
        for i, ws in enumerate(connections[:10]):  # 처음 10개 연결만 테스트
            try:
                ws.send(json.dumps({
                    'type': 'get_all_metrics'
                }))
            except Exception as e:
                logger.error(f"Failed to send message on connection {i}: {e}")
        
        # 결과 수집 대기
        time.sleep(10)
        
        end_time = time.time()
        
        # 연결 정리
        for ws in connections:
            try:
                ws.close()
            except:
                pass
        
        # 결과 분석
        successful_connections = len([r for r in results if r['type'] == 'open'])
        received_messages = len([r for r in results if r['type'] == 'message'])
        
        return {
            'test_type': 'websocket',
            'total_connections': num_connections,
            'successful_connections': successful_connections,
            'connection_success_rate': successful_connections / num_connections * 100,
            'received_messages': received_messages,
            'total_time': end_time - start_time,
            'connections_per_second': num_connections / (end_time - start_time)
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 성능 테스트"""
        logger.info("Starting comprehensive performance test")
        
        test_results = {}
        
        # 각 엔드포인트별 부하 테스트
        endpoints = ['metrics', 'trends', 'analytics', 'registration', 'update']
        
        # pyright: ignore [reportUnusedVariable]
        # 앞으로도 pyright의 변수 미사용 등 경고가 발생하면 해당 줄 끝에 '# pyright: ignore' 주석을 달아 경고를 무시하세요.
        for endpoint in endpoints:  # pyright: ignore
            logger.info(f"Testing {endpoint} endpoint")
            test_results[endpoint] = self.run_load_test(endpoint, 10, 50)
        
        # WebSocket 테스트
        logger.info("Testing WebSocket connections")
        test_results['websocket'] = self.run_websocket_test(50)
        
        # 스트레스 테스트 (가장 중요한 엔드포인트)
        logger.info("Running stress test on metrics endpoint")
        test_results['stress_test'] = self.run_stress_test('metrics', 30, 300)
        
        # 종합 분석
        overall_analysis = {
            'timestamp': datetime.now().isoformat(),
            'test_duration': time.time() - self.start_time if self.start_time else 0,
            'endpoint_performance': test_results,
            'overall_health': self.calculate_overall_health(test_results)
        }
        
        return overall_analysis
    
    def calculate_overall_health(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """전체 시스템 건강도 계산"""
        endpoint_results = test_results.get('endpoint_performance', {})
        
        success_rates = []
        response_times = []
        throughput_rates = []
        
        for endpoint, result in endpoint_results.items():  # pyright: ignore
            if isinstance(result, dict):
                success_rates.append(result.get('success_rate', 0))
                response_times.append(result.get('avg_response_time', 0))
                throughput_rates.append(result.get('requests_per_second', 0))
        
        if not success_rates:
            return {
                'status': 'unknown',
                'score': 0,
                'issues': ['No test results available']
            }
        
        avg_success_rate = statistics.mean(success_rates)
        avg_response_time = statistics.mean(response_times)
        avg_throughput = statistics.mean(throughput_rates)
        
        # 건강도 점수 계산 (0-100)
        health_score = 0
        
        # 성공률 가중치 40%
        if avg_success_rate >= 99:
            health_score += 40
        elif avg_success_rate >= 95:
            health_score += 30
        elif avg_success_rate >= 90:
            health_score += 20
        elif avg_success_rate >= 80:
            health_score += 10
        
        # 응답 시간 가중치 30%
        if avg_response_time <= 500:
            health_score += 30
        elif avg_response_time <= 1000:
            health_score += 25
        elif avg_response_time <= 2000:
            health_score += 20
        elif avg_response_time <= 5000:
            health_score += 10
        
        # 처리량 가중치 30%
        if avg_throughput >= 100:
            health_score += 30
        elif avg_throughput >= 50:
            health_score += 25
        elif avg_throughput >= 20:
            health_score += 20
        elif avg_throughput >= 10:
            health_score += 10
        
        # 상태 결정
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        # 문제점 식별
        issues = []
        if avg_success_rate < 95:
            issues.append(f"Low success rate: {avg_success_rate:.1f}%")
        if avg_response_time > 2000:
            issues.append(f"High response time: {avg_response_time:.1f}ms")
        if avg_throughput < 20:
            issues.append(f"Low throughput: {avg_throughput:.1f} req/s")
        
        return {
            'status': status,
            'score': health_score,
            'avg_success_rate': avg_success_rate,
            'avg_response_time': avg_response_time,
            'avg_throughput': avg_throughput,
            'issues': issues
        }
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None):
        """결과를 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")
        return filename
    
    def print_summary(self, results: Dict[str, Any]):
        """결과 요약 출력"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        overall_health = results.get('overall_health', {})
        print(f"Overall Status: {overall_health.get('status', 'unknown').upper()}")
        print(f"Health Score: {overall_health.get('score', 0)}/100")
        print(f"Test Duration: {results.get('test_duration', 0):.2f} seconds")
        
        if overall_health.get('issues'):
            print("\nIssues Found:")
            for issue in overall_health['issues']:
                print(f"  - {issue}")
        
        print("\nEndpoint Performance:")
        endpoint_results = results.get('endpoint_performance', {})
        for endpoint, result in endpoint_results.items():  # pyright: ignore
            if isinstance(result, dict):
                print(f"  {endpoint}:")
                print(f"    Success Rate: {result.get('success_rate', 0):.1f}%")
                print(f"    Avg Response Time: {result.get('avg_response_time', 0):.1f}ms")
                print(f"    Throughput: {result.get('requests_per_second', 0):.1f} req/s")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Plugin Monitoring Performance Test')
    parser.add_argument('--base-url', default='http://localhost:5000', help='Base URL for testing')
    parser.add_argument('--test-type', choices=['load', 'stress', 'websocket', 'comprehensive'], 
                       default='comprehensive', help='Type of test to run')
    parser.add_argument('--threads', type=int, default=10, help='Number of threads for load test')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests per test')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = PerformanceTest(args.base_url)
    
    try:
        if args.test_type == 'load':
            results = tester.run_load_test('metrics', args.threads, args.requests)
        elif args.test_type == 'stress':
            results = tester.run_stress_test('metrics', args.threads, args.requests)
        elif args.test_type == 'websocket':
            results = tester.run_websocket_test(args.requests)
        else:  # comprehensive
            results = tester.run_comprehensive_test()
        
        # 결과 출력
        tester.print_summary(results)
        
        # 결과 저장
        if args.output:
            tester.save_results(results, args.output)
        else:
            tester.save_results(results)
        
        # 성공/실패 판정
        overall_health = results.get('overall_health', {})
        if overall_health.get('status') in ['poor', 'unknown']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 