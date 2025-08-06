#!/usr/bin/env python3
"""
모니터링 시스템 테스트 스크립트
"""

import requests
import json
import time
import sys
from datetime import datetime

# API 기본 URL
BASE_URL = "http://localhost:5000/api/monitoring"

def test_health_check():
    """모니터링 시스템 상태 확인 테스트"""
    print("🔍 모니터링 시스템 상태 확인...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 상태: {data.get('status')}")
            print(f"   실행 중: {data.get('is_running')}")
            print(f"   메시지: {data.get('message')}")
            return True
        else:
            print(f"❌ 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def test_system_stats():
    """시스템 통계 조회 테스트"""
    print("\n📊 시스템 통계 조회...")
    try:
        response = requests.get(f"{BASE_URL}/stats/system")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stats = data.get('data', {})
                print(f"✅ CPU 사용률: {stats.get('current_cpu', 0):.1f}%")
                print(f"   메모리 사용률: {stats.get('current_memory', 0):.1f}%")
                print(f"   디스크 사용률: {stats.get('current_disk', 0):.1f}%")
                print(f"   업타임: {stats.get('uptime_hours', 0):.1f}시간")
                print(f"   활성 알림: {stats.get('active_alerts', 0)}개")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_application_stats():
    """애플리케이션 통계 조회 테스트"""
    print("\n⚡ 애플리케이션 통계 조회...")
    try:
        response = requests.get(f"{BASE_URL}/stats/application")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stats = data.get('data', {})
                print(f"✅ 응답 시간: {stats.get('current_response_time', 0):.0f}ms")
                print(f"   요청 수 (1시간): {stats.get('total_requests_1h', 0)}")
                print(f"   에러율: {stats.get('error_rate_1h', 0):.2f}%")
                print(f"   활성 세션: {stats.get('active_sessions', 0)}")
                print(f"   DB 연결: {stats.get('database_connections', 0)}")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_metric_history():
    """메트릭 히스토리 조회 테스트"""
    print("\n📈 메트릭 히스토리 조회...")
    try:
        response = requests.get(f"{BASE_URL}/metrics/history?metric=cpu_percent&hours=24")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                history_data = data.get('data', {})
                history = history_data.get('history', [])
                print(f"✅ 메트릭: {history_data.get('metric_name')}")
                print(f"   기간: {history_data.get('hours')}시간")
                print(f"   데이터 포인트: {len(history)}개")
                if history:
                    latest = history[-1]
                    print(f"   최신 값: {latest.get('value', 0):.2f}")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_alerts():
    """알림 조회 테스트"""
    print("\n🚨 알림 조회...")
    try:
        response = requests.get(f"{BASE_URL}/alerts?limit=10")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                alerts = data.get('data', [])
                print(f"✅ 알림 수: {len(alerts)}개")
                for alert in alerts[:3]:  # 최대 3개만 표시
                    print(f"   - {alert.get('message', 'N/A')} ({alert.get('severity')})")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_alert_rules():
    """알림 규칙 조회 테스트"""
    print("\n⚙️ 알림 규칙 조회...")
    try:
        response = requests.get(f"{BASE_URL}/rules")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                rules = data.get('data', [])
                print(f"✅ 규칙 수: {len(rules)}개")
                for rule in rules[:3]:  # 최대 3개만 표시
                    print(f"   - {rule.get('name', 'N/A')} ({rule.get('severity')})")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_create_alert_rule():
    """알림 규칙 생성 테스트"""
    print("\n➕ 알림 규칙 생성...")
    try:
        rule_data = {
            "name": "테스트 알림 규칙",
            "metric_type": "system",
            "metric_name": "cpu_percent",
            "operator": ">",
            "threshold": 95,
            "duration": 60,
            "severity": "critical"
        }
        
        response = requests.post(f"{BASE_URL}/rules", json=rule_data)
        if response.status_code == 201:
            data = response.json()
            if data.get('status') == 'success':
                rule_id = data.get('data', {}).get('rule_id')
                print(f"✅ 규칙 생성 성공: {rule_id}")
                return rule_id
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return None

def test_delete_alert_rule(rule_id):
    """알림 규칙 삭제 테스트"""
    if not rule_id:
        return False
        
    print(f"\n🗑️ 알림 규칙 삭제: {rule_id}")
    try:
        response = requests.delete(f"{BASE_URL}/rules/{rule_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ 규칙 삭제 성공")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_monitoring_control():
    """모니터링 제어 테스트"""
    print("\n🎛️ 모니터링 제어...")
    
    # 상태 조회
    try:
        response = requests.get(f"{BASE_URL}/control/status")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                status = data.get('data', {})
                print(f"✅ 실행 중: {status.get('is_running')}")
                print(f"   수집 간격: {status.get('collection_interval')}초")
                print(f"   보존 기간: {status.get('retention_days')}일")
                print(f"   알림 활성화: {status.get('alert_enabled')}")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_metrics_collection():
    """메트릭 수집 테스트"""
    print("\n📊 메트릭 수집...")
    try:
        response = requests.post(f"{BASE_URL}/metrics/collect", json={"type": "all"})
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ 메트릭 수집 성공")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def test_cleanup():
    """데이터 정리 테스트"""
    print("\n🧹 데이터 정리...")
    try:
        response = requests.post(f"{BASE_URL}/cleanup")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ 데이터 정리 성공")
                return True
            else:
                print(f"❌ API 오류: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 요청 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 모니터링 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트 결과 추적
    test_results = []
    
    # 기본 기능 테스트
    test_results.append(("상태 확인", test_health_check()))
    test_results.append(("시스템 통계", test_system_stats()))
    test_results.append(("애플리케이션 통계", test_application_stats()))
    test_results.append(("메트릭 히스토리", test_metric_history()))
    test_results.append(("알림 조회", test_alerts()))
    test_results.append(("알림 규칙 조회", test_alert_rules()))
    
    # 규칙 생성/삭제 테스트
    rule_id = test_create_alert_rule()
    test_results.append(("알림 규칙 생성", rule_id is not None))
    
    if rule_id:
        test_results.append(("알림 규칙 삭제", test_delete_alert_rule(rule_id)))
    
    # 제어 기능 테스트
    test_results.append(("모니터링 제어", test_monitoring_control()))
    test_results.append(("메트릭 수집", test_metrics_collection()))
    test_results.append(("데이터 정리", test_cleanup()))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 테스트 결과 요약")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {total - passed}개")
    print(f"성공률: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 모든 테스트가 성공했습니다!")
        return 0
    else:
        print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)
