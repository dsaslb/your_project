#!/usr/bin/env python3
"""
고도화된 알림 시스템 테스트 스크립트
실시간 알림 기능을 테스트하고 검증
"""

import time
import random
import logging
import requests
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAlertTester:
    """고도화된 알림 시스템 테스터"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_system_status(self) -> bool:
        """시스템 상태 테스트"""
        try:
            logger.info("시스템 상태 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    status = data['data']
                    logger.info(f"✅ 시스템 상태: 모니터링={status['monitoring_active']}")
                    logger.info(f"✅ 활성 알림: {status['active_alerts_count']}개")
                    logger.info(f"✅ 24시간 알림: {status['total_alerts_24h']}개")
                    logger.info(f"✅ 알림 규칙: {status['alert_rules_count']}개")
                    return True
                else:
                    logger.error(f"❌ 시스템 상태 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 시스템 상태 테스트 오류: {e}")
            return False
    
    def test_active_alerts(self) -> bool:
        """활성 알림 조회 테스트"""
        try:
            logger.info("활성 알림 조회 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/alerts/active")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    alerts = data['data']
                    logger.info(f"✅ 활성 알림 조회 성공: {len(alerts)}개")
                    for alert in alerts[:3]:  # 처음 3개만 출력
                        logger.info(f"  - {alert['plugin_name']}: {alert['message']}")
                    return True
                else:
                    logger.error(f"❌ 활성 알림 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 활성 알림 테스트 오류: {e}")
            return False
    
    def test_alert_history(self) -> bool:
        """알림 히스토리 조회 테스트"""
        try:
            logger.info("알림 히스토리 조회 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/alerts/history?hours=24")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    alerts = data['data']
                    logger.info(f"✅ 알림 히스토리 조회 성공: {len(alerts)}개")
                    return True
                else:
                    logger.error(f"❌ 알림 히스토리 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 알림 히스토리 테스트 오류: {e}")
            return False
    
    def test_alert_rules(self) -> bool:
        """알림 규칙 조회 테스트"""
        try:
            logger.info("알림 규칙 조회 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/rules")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    rules = data['data']
                    logger.info(f"✅ 알림 규칙 조회 성공: {len(rules)}개")
                    for rule in rules[:3]:  # 처음 3개만 출력
                        logger.info(f"  - {rule['name']}: {rule['metric']} {rule['operator']} {rule['threshold']}")
                    return True
                else:
                    logger.error(f"❌ 알림 규칙 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 알림 규칙 테스트 오류: {e}")
            return False
    
    def test_channel_configs(self) -> bool:
        """채널 설정 조회 테스트"""
        try:
            logger.info("채널 설정 조회 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/channels/config")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    configs = data['data']
                    logger.info(f"✅ 채널 설정 조회 성공: {len(configs)}개 채널")
                    for channel, config in configs.items():
                        logger.info(f"  - {channel}: 활성={config['enabled']}, 설정={config['configured']}")
                    return True
                else:
                    logger.error(f"❌ 채널 설정 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 채널 설정 테스트 오류: {e}")
            return False
    
    def test_statistics(self) -> bool:
        """알림 통계 조회 테스트"""
        try:
            logger.info("알림 통계 조회 테스트 시작")
            response = self.session.get(f"{self.base_url}/api/enhanced-alerts/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['data']
                    logger.info(f"✅ 알림 통계 조회 성공")
                    logger.info(f"  - 24시간 알림: {stats['total_alerts_24h']}개")
                    logger.info(f"  - 활성 알림: {stats['active_alerts']}개")
                    logger.info(f"  - 심각도 분포: {stats['severity_distribution']}")
                    return True
                else:
                    logger.error(f"❌ 알림 통계 조회 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 알림 통계 테스트 오류: {e}")
            return False
    
    def test_create_alert_rule(self) -> bool:
        """알림 규칙 생성 테스트"""
        try:
            logger.info("알림 규칙 생성 테스트 시작")
            
            rule_data = {
                "name": "테스트 규칙",
                "description": "테스트용 알림 규칙입니다.",
                "metric": "test_metric",
                "operator": ">",
                "threshold": 90.0,
                "severity": "warning",
                "channels": ["web", "dashboard"],
                "cooldown_minutes": 5,
                "enabled": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/enhanced-alerts/rules",
                json=rule_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info(f"✅ 알림 규칙 생성 성공: {data['data']['name']}")
                    return True
                else:
                    logger.error(f"❌ 알림 규칙 생성 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 알림 규칙 생성 테스트 오류: {e}")
            return False
    
    def test_channel_test(self) -> bool:
        """채널 테스트"""
        try:
            logger.info("채널 테스트 시작")
            
            # web 채널 테스트
            response = self.session.post(f"{self.base_url}/api/enhanced-alerts/test/web")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ web 채널 테스트 성공")
                    return True
                else:
                    logger.error(f"❌ web 채널 테스트 실패: {data.get('message')}")
                    return False
            else:
                logger.error(f"❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 채널 테스트 오류: {e}")
            return False
    
    def simulate_plugin_metrics(self) -> None:
        """플러그인 메트릭 시뮬레이션"""
        logger.info("플러그인 메트릭 시뮬레이션 시작")
        
        try:
            # 고도화된 알림 시스템 import
            from core.backend.enhanced_alert_system import enhanced_alert_system
            
            if not enhanced_alert_system:
                logger.error("고도화된 알림 시스템을 사용할 수 없습니다.")
                return
            
            # 테스트 플러그인 등록
            test_plugins = [
                ("test_plugin_1", "테스트 플러그인 1"),
                ("test_plugin_2", "테스트 플러그인 2"),
                ("test_plugin_3", "테스트 플러그인 3")
            ]
            
            for plugin_id, plugin_name in test_plugins:
                # 다양한 메트릭 시뮬레이션
                for i in range(10):
                    # CPU 사용률 시뮬레이션 (때때로 임계값 초과)
                    cpu_usage = random.uniform(20, 100)
                    
                    # 메모리 사용률 시뮬레이션
                    memory_usage = random.uniform(30, 95)
                    
                    # 에러율 시뮬레이션
                    error_rate = random.uniform(0, 15)
                    
                    # 응답시간 시뮬레이션
                    response_time = random.uniform(0.1, 8.0)
                    
                    metrics = {
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory_usage,
                        'error_rate': error_rate,
                        'response_time': response_time,
                        'error_count': int(error_rate * 10),
                        'request_count': 100,
                        'uptime': random.uniform(100, 3600),
                        'last_activity': random.uniform(0, 300)
                    }
                    
                    enhanced_alert_system.check_metrics(plugin_id, plugin_name, metrics)
                    
                    logger.info(f"메트릭 업데이트: {plugin_name} - CPU: {cpu_usage:.1f}%, 메모리: {memory_usage:.1f}%")
                    
                    time.sleep(2)  # 2초 대기
                    
        except Exception as e:
            logger.error(f"메트릭 시뮬레이션 오류: {e}")
    
    def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        logger.info("=" * 50)
        logger.info("고도화된 알림 시스템 테스트 시작")
        logger.info("=" * 50)
        
        test_results = []
        
        # API 테스트
        test_results.append(("시스템 상태", self.test_system_status()))
        test_results.append(("활성 알림 조회", self.test_active_alerts()))
        test_results.append(("알림 히스토리", self.test_alert_history()))
        test_results.append(("알림 규칙 조회", self.test_alert_rules()))
        test_results.append(("채널 설정 조회", self.test_channel_configs()))
        test_results.append(("알림 통계 조회", self.test_statistics()))
        test_results.append(("알림 규칙 생성", self.test_create_alert_rule()))
        test_results.append(("채널 테스트", self.test_channel_test()))
        
        # 결과 요약
        logger.info("=" * 50)
        logger.info("테스트 결과 요약")
        logger.info("=" * 50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"전체 결과: {passed}/{total} 통과")
        
        if passed == total:
            logger.info("🎉 모든 테스트가 성공했습니다!")
        else:
            logger.warning(f"⚠️ {total - passed}개 테스트가 실패했습니다.")
        
        return passed == total

def main():
    """메인 함수"""
    tester = EnhancedAlertTester()
    
    # API 테스트 실행
    api_success = tester.run_all_tests()
    
    if api_success:
        # 메트릭 시뮬레이션 실행
        logger.info("\n" + "=" * 50)
        logger.info("메트릭 시뮬레이션 시작 (30초간)")
        logger.info("=" * 50)
        
        import threading
        simulation_thread = threading.Thread(target=tester.simulate_plugin_metrics, daemon=True)
        simulation_thread.start()
        
        # 30초간 시뮬레이션 실행
        time.sleep(30)
        
        logger.info("메트릭 시뮬레이션 완료")
        
        # 최종 상태 확인
        logger.info("\n최종 상태 확인:")
        tester.test_system_status()
        tester.test_active_alerts()
    
    return 0 if api_success else 1

if __name__ == "__main__":
    exit(main()) 