#!/usr/bin/env python3
"""
고도화된 플러그인 모니터링 시스템 테스트 스크립트
실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기 기능 테스트
"""

import requests
import json
import time
import random
import threading
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedMonitoringTester:
    """고도화된 모니터링 시스템 테스터"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_plugins = [
            "restaurant_management",
            "core_management", 
            "deployed",
            "marketplace"
        ]
        
        # 테스트 데이터
        self.metric_types = [
            "cpu_usage", "memory_usage", "response_time", 
            "error_rate", "request_count", "throughput"
        ]
        
        self.log_levels = ["debug", "info", "warning", "error", "critical"]
        self.event_types = ["startup", "shutdown", "error", "performance_alert", "custom_event"]
        
    def login(self):
        """로그인 (테스트용)"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
            if response.status_code == 200:
                logger.info("로그인 성공")
                return True
            else:
                logger.warning("로그인 실패, 게스트 모드로 진행")
                return False
        except Exception as e:
            logger.error(f"로그인 오류: {e}")
            return False
    
    def test_monitoring_status(self):
        """모니터링 상태 테스트"""
        logger.info("=== 모니터링 상태 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/status")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    logger.info("✅ 모니터링 상태 조회 성공")
                    logger.info(f"   - 모니터링 활성: {data['data']['monitoring_active']}")
                    logger.info(f"   - 전체 플러그인: {data['data']['total_plugins']}")
                    logger.info(f"   - 활성 플러그인: {data['data']['active_plugins']}")
                    logger.info(f"   - 총 메트릭: {data['data']['total_metrics']}")
                    return True
                else:
                    logger.error(f"❌ 모니터링 상태 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 모니터링 상태 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 모니터링 상태 테스트 오류: {e}")
            return False
    
    def test_plugins_list(self):
        """플러그인 목록 테스트"""
        logger.info("=== 플러그인 목록 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    plugins = data['data']
                    logger.info(f"✅ 플러그인 목록 조회 성공: {len(plugins)}개 플러그인")
                    
                    for plugin in plugins[:3]:  # 처음 3개만 출력
                        logger.info(f"   - {plugin['plugin_id']}: {plugin['status']}")
                    
                    return plugins
                else:
                    logger.error(f"❌ 플러그인 목록 조회 실패: {data['message']}")
                    return []
            else:
                logger.error(f"❌ 플러그인 목록 조회 HTTP 오류: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ 플러그인 목록 테스트 오류: {e}")
            return []
    
    def test_plugin_summary(self, plugin_id):
        """플러그인 요약 테스트"""
        logger.info(f"=== 플러그인 요약 테스트: {plugin_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/summary")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    summary = data['data']
                    logger.info("✅ 플러그인 요약 조회 성공")
                    logger.info(f"   - 상태: {summary['status']}")
                    logger.info(f"   - 메트릭 수: {summary['metrics_count']}")
                    logger.info(f"   - 로그 수: {summary['logs_count']}")
                    logger.info(f"   - 에러 수: {summary['error_logs_count']}")
                    return True
                else:
                    logger.error(f"❌ 플러그인 요약 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 플러그인 요약 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 플러그인 요약 테스트 오류: {e}")
            return False
    
    def test_metrics_recording(self, plugin_id):
        """메트릭 기록 테스트"""
        logger.info(f"=== 메트릭 기록 테스트: {plugin_id} ===")
        
        success_count = 0
        for metric_type in self.metric_types:
            try:
                metric_data = {
                    "metric_type": metric_type,
                    "value": random.uniform(0, 100),
                    "metadata": {
                        "source": "test_script",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/metrics",
                    json=metric_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        success_count += 1
                        logger.info(f"   ✅ {metric_type} 메트릭 기록 성공")
                    else:
                        logger.error(f"   ❌ {metric_type} 메트릭 기록 실패: {data['message']}")
                else:
                    logger.error(f"   ❌ {metric_type} 메트릭 기록 HTTP 오류: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"   ❌ {metric_type} 메트릭 기록 오류: {e}")
        
        logger.info(f"메트릭 기록 완료: {success_count}/{len(self.metric_types)} 성공")
        return success_count > 0
    
    def test_logs_recording(self, plugin_id):
        """로그 기록 테스트"""
        logger.info(f"=== 로그 기록 테스트: {plugin_id} ===")
        
        success_count = 0
        for level in self.log_levels:
            try:
                log_data = {
                    "level": level,
                    "message": f"테스트 로그 메시지 - {level} 레벨",
                    "context": {
                        "test_id": f"test_{int(time.time())}",
                        "level": level
                    }
                }
                
                if level in ["error", "critical"]:
                    log_data["traceback"] = "테스트용 스택 트레이스\n  File 'test.py', line 1\n    raise Exception('테스트 에러')"
                
                response = self.session.post(
                    f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/logs",
                    json=log_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        success_count += 1
                        logger.info(f"   ✅ {level} 로그 기록 성공")
                    else:
                        logger.error(f"   ❌ {level} 로그 기록 실패: {data['message']}")
                else:
                    logger.error(f"   ❌ {level} 로그 기록 HTTP 오류: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"   ❌ {level} 로그 기록 오류: {e}")
        
        logger.info(f"로그 기록 완료: {success_count}/{len(self.log_levels)} 성공")
        return success_count > 0
    
    def test_events_recording(self, plugin_id):
        """이벤트 기록 테스트"""
        logger.info(f"=== 이벤트 기록 테스트: {plugin_id} ===")
        
        success_count = 0
        for event_type in self.event_types:
            try:
                event_data = {
                    "event_type": event_type,
                    "description": f"테스트 이벤트 - {event_type}",
                    "severity": random.choice(["low", "medium", "high", "critical"]),
                    "data": {
                        "test_id": f"test_{int(time.time())}",
                        "event_type": event_type,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/events",
                    json=event_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        success_count += 1
                        logger.info(f"   ✅ {event_type} 이벤트 기록 성공")
                    else:
                        logger.error(f"   ❌ {event_type} 이벤트 기록 실패: {data['message']}")
                else:
                    logger.error(f"   ❌ {event_type} 이벤트 기록 HTTP 오류: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"   ❌ {event_type} 이벤트 기록 오류: {e}")
        
        logger.info(f"이벤트 기록 완료: {success_count}/{len(self.event_types)} 성공")
        return success_count > 0
    
    def test_snapshot_creation(self, plugin_id):
        """스냅샷 생성 테스트"""
        logger.info(f"=== 스냅샷 생성 테스트: {plugin_id} ===")
        
        try:
            snapshot_data = {
                "cpu_usage": random.uniform(0, 100),
                "memory_usage": random.uniform(0, 100),
                "response_time": random.uniform(10, 1000),
                "error_rate": random.uniform(0, 0.1),
                "request_count": random.randint(100, 10000),
                "throughput": random.uniform(10, 1000),
                "disk_io": {
                    "read_bytes": random.randint(1000000, 100000000),
                    "write_bytes": random.randint(1000000, 100000000)
                },
                "network_io": {
                    "rx_bytes": random.randint(1000000, 100000000),
                    "tx_bytes": random.randint(1000000, 100000000)
                },
                "custom_metrics": {
                    "custom_metric_1": random.uniform(0, 100),
                    "custom_metric_2": random.uniform(0, 100)
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/snapshots",
                json=snapshot_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    logger.info("✅ 스냅샷 생성 성공")
                    return True
                else:
                    logger.error(f"❌ 스냅샷 생성 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 스냅샷 생성 HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 스냅샷 생성 테스트 오류: {e}")
            return False
    
    def test_metrics_retrieval(self, plugin_id):
        """메트릭 조회 테스트"""
        logger.info(f"=== 메트릭 조회 테스트: {plugin_id} ===")
        
        try:
            # 모든 메트릭 조회
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/metrics?hours=1")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    metrics = data['data']
                    logger.info(f"✅ 메트릭 조회 성공: {len(metrics)}개 메트릭")
                    return True
                else:
                    logger.error(f"❌ 메트릭 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 메트릭 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 메트릭 조회 테스트 오류: {e}")
            return False
    
    def test_logs_retrieval(self, plugin_id):
        """로그 조회 테스트"""
        logger.info(f"=== 로그 조회 테스트: {plugin_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/logs?hours=1")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    logs = data['data']
                    logger.info(f"✅ 로그 조회 성공: {len(logs)}개 로그")
                    return True
                else:
                    logger.error(f"❌ 로그 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 로그 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 로그 조회 테스트 오류: {e}")
            return False
    
    def test_events_retrieval(self, plugin_id):
        """이벤트 조회 테스트"""
        logger.info(f"=== 이벤트 조회 테스트: {plugin_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/events?hours=1")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    events = data['data']
                    logger.info(f"✅ 이벤트 조회 성공: {len(events)}개 이벤트")
                    return True
                else:
                    logger.error(f"❌ 이벤트 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 이벤트 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 이벤트 조회 테스트 오류: {e}")
            return False
    
    def test_snapshots_retrieval(self, plugin_id):
        """스냅샷 조회 테스트"""
        logger.info(f"=== 스냅샷 조회 테스트: {plugin_id} ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/snapshots?hours=1")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    snapshots = data['data']
                    logger.info(f"✅ 스냅샷 조회 성공: {len(snapshots)}개 스냅샷")
                    return True
                else:
                    logger.error(f"❌ 스냅샷 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 스냅샷 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 스냅샷 조회 테스트 오류: {e}")
            return False
    
    def test_analytics_trends(self):
        """분석 트렌드 테스트"""
        logger.info("=== 분석 트렌드 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/analytics/trends?hours=24&metric_type=cpu_usage")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    trends = data['data']['trends']
                    logger.info(f"✅ 분석 트렌드 조회 성공: {len(trends)}개 데이터 포인트")
                    return True
                else:
                    logger.error(f"❌ 분석 트렌드 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 분석 트렌드 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 분석 트렌드 테스트 오류: {e}")
            return False
    
    def test_performance_analytics(self):
        """성능 분석 테스트"""
        logger.info("=== 성능 분석 테스트 ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/advanced-monitoring/analytics/performance?hours=24")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    analytics = data['data']
                    logger.info("✅ 성능 분석 조회 성공")
                    logger.info(f"   - 총 스냅샷: {analytics['total_snapshots']}")
                    logger.info(f"   - 평균 CPU: {analytics['average_cpu']:.2f}%")
                    logger.info(f"   - 평균 메모리: {analytics['average_memory']:.2f}%")
                    return True
                else:
                    logger.error(f"❌ 성능 분석 조회 실패: {data['message']}")
                    return False
            else:
                logger.error(f"❌ 성능 분석 조회 HTTP 오류: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 성능 분석 테스트 오류: {e}")
            return False
    
    def simulate_real_time_data(self, plugin_id, duration=60):
        """실시간 데이터 시뮬레이션"""
        logger.info(f"=== 실시간 데이터 시뮬레이션: {plugin_id} ({duration}초) ===")
        
        start_time = time.time()
        success_count = 0
        
        while time.time() - start_time < duration:
            try:
                # 메트릭 시뮬레이션
                for metric_type in self.metric_types:
                    metric_data = {
                        "metric_type": metric_type,
                        "value": random.uniform(0, 100),
                        "metadata": {"simulation": True}
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/metrics",
                        json=metric_data
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                
                # 로그 시뮬레이션 (10% 확률)
                if random.random() < 0.1:
                    log_data = {
                        "level": random.choice(self.log_levels),
                        "message": f"시뮬레이션 로그 - {datetime.now().strftime('%H:%M:%S')}",
                        "context": {"simulation": True}
                    }
                    
                    self.session.post(
                        f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/logs",
                        json=log_data
                    )
                
                # 이벤트 시뮬레이션 (5% 확률)
                if random.random() < 0.05:
                    event_data = {
                        "event_type": random.choice(self.event_types),
                        "description": f"시뮬레이션 이벤트 - {datetime.now().strftime('%H:%M:%S')}",
                        "severity": random.choice(["low", "medium", "high"]),
                        "data": {"simulation": True}
                    }
                    
                    self.session.post(
                        f"{self.base_url}/api/advanced-monitoring/plugins/{plugin_id}/events",
                        json=event_data
                    )
                
                time.sleep(2)  # 2초마다 데이터 생성
                
            except Exception as e:
                logger.error(f"시뮬레이션 오류: {e}")
                time.sleep(1)
        
        logger.info(f"시뮬레이션 완료: {success_count}개 메트릭 생성")
    
    def run_full_test(self):
        """전체 테스트 실행"""
        logger.info("🚀 고도화된 플러그인 모니터링 시스템 테스트 시작")
        
        # 로그인 시도
        self.login()
        
        # 기본 기능 테스트
        test_results = []
        
        # 1. 모니터링 상태 테스트
        test_results.append(("모니터링 상태", self.test_monitoring_status()))
        
        # 2. 플러그인 목록 테스트
        plugins = self.test_plugins_list()
        test_results.append(("플러그인 목록", len(plugins) > 0))
        
        # 3. 각 플러그인별 테스트
        for plugin_id in self.test_plugins[:2]:  # 처음 2개만 테스트
            logger.info(f"\n📊 플러그인 테스트: {plugin_id}")
            
            # 요약 테스트
            test_results.append((f"{plugin_id} 요약", self.test_plugin_summary(plugin_id)))
            
            # 데이터 기록 테스트
            test_results.append((f"{plugin_id} 메트릭 기록", self.test_metrics_recording(plugin_id)))
            test_results.append((f"{plugin_id} 로그 기록", self.test_logs_recording(plugin_id)))
            test_results.append((f"{plugin_id} 이벤트 기록", self.test_events_recording(plugin_id)))
            test_results.append((f"{plugin_id} 스냅샷 생성", self.test_snapshot_creation(plugin_id)))
            
            # 데이터 조회 테스트
            test_results.append((f"{plugin_id} 메트릭 조회", self.test_metrics_retrieval(plugin_id)))
            test_results.append((f"{plugin_id} 로그 조회", self.test_logs_retrieval(plugin_id)))
            test_results.append((f"{plugin_id} 이벤트 조회", self.test_events_retrieval(plugin_id)))
            test_results.append((f"{plugin_id} 스냅샷 조회", self.test_snapshots_retrieval(plugin_id)))
        
        # 4. 분석 기능 테스트
        test_results.append(("분석 트렌드", self.test_analytics_trends()))
        test_results.append(("성능 분석", self.test_performance_analytics()))
        
        # 5. 실시간 시뮬레이션 (30초)
        if plugins:
            simulation_thread = threading.Thread(
                target=self.simulate_real_time_data,
                args=(plugins[0]['plugin_id'], 30)
            )
            simulation_thread.daemon = True
            simulation_thread.start()
            simulation_thread.join()
        
        # 결과 요약
        logger.info("\n" + "="*50)
        logger.info("📋 테스트 결과 요약")
        logger.info("="*50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
            if result:
                passed += 1
        
        logger.info(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")
        
        return passed == total

def main():
    """메인 함수"""
    import sys
    
    # 명령행 인수 처리
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    # 테스터 생성 및 실행
    tester = AdvancedMonitoringTester(base_url)
    success = tester.run_full_test()
    
    # 종료 코드
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 