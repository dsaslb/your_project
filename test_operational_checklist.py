"""
운영 체크리스트 테스트
- 배포 전 셀프테스트
- 장애 주입 테스트
- 중복 처리 테스트
"""
import requests
import json
import time
import uuid
from datetime import datetime, timezone

class OperationalTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """테스트 결과 로깅"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def test_health_endpoints(self):
        """헬스체크 엔드포인트 테스트"""
        print("\n🏥 헬스체크 엔드포인트 테스트")
        print("=" * 50)
        
        # /healthz 테스트
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("healthz", True, f"DB: {data.get('database', {}).get('status', 'unknown')}")
            else:
                self.log_test("healthz", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("healthz", False, str(e))
        
        # /readyz 테스트
        try:
            response = requests.get(f"{self.base_url}/readyz", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("readyz", True, f"Ready: {data.get('ok', False)}")
            else:
                self.log_test("readyz", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("readyz", False, str(e))
        
        # /metrics 테스트
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("metrics", True, f"Outbox: {data.get('outbox', {}).get('total_events', 0)}")
            else:
                self.log_test("metrics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("metrics", False, str(e))
    
    def test_batch_sync_duplicates(self):
        """배치 동기화 중복 처리 테스트"""
        print("\n🔄 배치 동기화 중복 처리 테스트")
        print("=" * 50)
        
        # 중복 idem 키로 테스트
        duplicate_idem = str(uuid.uuid4())
        
        test_items = [
            {
                "type": "attendance",
                "idem": duplicate_idem,
                "payload": {
                    "user_id": 1,
                    "type": "in",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "lat": 37.5665,
                    "lng": 126.9780
                }
            }
        ]
        
        # 첫 번째 요청
        try:
            response1 = requests.post(
                f"{self.base_url}/api/mobile/sync/batch",
                json={
                    "items": test_items,
                    "meta": {
                        "device_id": "test-device-1",
                        "branch_id": 1,
                        "user_id": 1
                    }
                },
                headers={"X-Idempotency-Key": str(uuid.uuid4())},
                timeout=10
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                first_result = data1["results"][0]["status"]
                self.log_test("batch_sync_first", True, f"Status: {first_result}")
            else:
                self.log_test("batch_sync_first", False, f"Status: {response1.status_code}")
                return
        except Exception as e:
            self.log_test("batch_sync_first", False, str(e))
            return
        
        # 두 번째 요청 (중복)
        try:
            response2 = requests.post(
                f"{self.base_url}/api/mobile/sync/batch",
                json={
                    "items": test_items,
                    "meta": {
                        "device_id": "test-device-1",
                        "branch_id": 1,
                        "user_id": 1
                    }
                },
                headers={"X-Idempotency-Key": str(uuid.uuid4())},
                timeout=10
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                second_result = data2["results"][0]["status"]
                if second_result == "dup":
                    self.log_test("batch_sync_duplicate", True, "중복 처리 성공")
                else:
                    self.log_test("batch_sync_duplicate", False, f"예상: dup, 실제: {second_result}")
            else:
                self.log_test("batch_sync_duplicate", False, f"Status: {response2.status_code}")
        except Exception as e:
            self.log_test("batch_sync_duplicate", False, str(e))
    
    def test_outbox_worker(self):
        """Outbox 워커 테스트"""
        print("\n📦 Outbox 워커 테스트")
        print("=" * 50)
        
        # 이벤트 생성
        try:
            response = requests.post(
                f"{self.base_url}/api/mobile/sync/batch",
                json={
                    "items": [{
                        "type": "attendance",
                        "idem": str(uuid.uuid4()),
                        "payload": {
                            "user_id": 1,
                            "type": "out",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    }],
                    "meta": {
                        "device_id": "test-outbox",
                        "branch_id": 1,
                        "user_id": 1
                    }
                },
                headers={"X-Idempotency-Key": str(uuid.uuid4())},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("outbox_event_creation", True, "이벤트 생성 성공")
                
                # 잠시 대기 후 메트릭 확인
                time.sleep(2)
                
                metrics_response = requests.get(f"{self.base_url}/metrics", timeout=5)
                if metrics_response.status_code == 200:
                    metrics_data = metrics_response.json()
                    outbox_stats = metrics_data.get("outbox", {})
                    pending = outbox_stats.get("pending_events", 0)
                    
                    if pending == 0:
                        self.log_test("outbox_worker_delivery", True, "워커가 이벤트 전송 완료")
                    else:
                        self.log_test("outbox_worker_delivery", False, f"대기 중인 이벤트: {pending}")
                else:
                    self.log_test("outbox_worker_delivery", False, "메트릭 조회 실패")
            else:
                self.log_test("outbox_event_creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("outbox_worker", False, str(e))
    
    def test_conflict_resolution(self):
        """충돌 해결 규칙 테스트"""
        print("\n⚔️ 충돌 해결 규칙 테스트")
        print("=" * 50)
        
        # 출퇴근 시간 외 테스트
        try:
            response = requests.post(
                f"{self.base_url}/api/mobile/sync/batch",
                json={
                    "items": [{
                        "type": "attendance",
                        "idem": str(uuid.uuid4()),
                        "payload": {
                            "user_id": 1,
                            "type": "in",
                            "timestamp": "2024-01-01T15:00:00Z",  # 출근 시간 외
                            "lat": 37.5665,
                            "lng": 126.9780
                        }
                    }],
                    "meta": {
                        "device_id": "test-conflict",
                        "branch_id": 1,
                        "user_id": 1
                    }
                },
                headers={"X-Idempotency-Key": str(uuid.uuid4())},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data["results"][0]["status"]
                if result == "error":
                    self.log_test("conflict_resolution", True, "시간 외 출근 거부됨")
                else:
                    self.log_test("conflict_resolution", False, f"예상: error, 실제: {result}")
            else:
                self.log_test("conflict_resolution", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("conflict_resolution", False, str(e))
    
    def test_network_failure_simulation(self):
        """네트워크 장애 시뮬레이션 테스트"""
        print("\n🌐 네트워크 장애 시뮬레이션 테스트")
        print("=" * 50)
        
        # 여러 개의 오프라인 액션 시뮬레이션
        offline_actions = []
        for i in range(3):
            offline_actions.append({
                "type": "attendance",
                "idem": str(uuid.uuid4()),
                "payload": {
                    "user_id": 1,
                    "type": "in",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "lat": 37.5665 + i * 0.001,
                    "lng": 126.9780 + i * 0.001
                }
            })
        
        try:
            response = requests.post(
                f"{self.base_url}/api/mobile/sync/batch",
                json={
                    "items": offline_actions,
                    "meta": {
                        "device_id": "test-network-failure",
                        "branch_id": 1,
                        "user_id": 1
                    }
                },
                headers={"X-Idempotency-Key": str(uuid.uuid4())},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data["results"]
                success_count = sum(1 for r in results if r["status"] == "ok")
                
                if success_count == 3:
                    self.log_test("network_failure_recovery", True, f"3개 액션 모두 성공")
                else:
                    self.log_test("network_failure_recovery", False, f"성공: {success_count}/3")
            else:
                self.log_test("network_failure_recovery", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("network_failure_recovery", False, str(e))
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 운영 체크리스트 테스트 시작")
        print("=" * 60)
        
        self.test_health_endpoints()
        self.test_batch_sync_duplicates()
        self.test_outbox_worker()
        self.test_conflict_resolution()
        self.test_network_failure_simulation()
        
        # 결과 요약
        print("\n📊 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed_tests == total_tests

def main():
    """메인 실행 함수"""
    tester = OperationalTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 모든 테스트 통과! 운영 준비 완료!")
        return 0
    else:
        print("\n⚠️ 일부 테스트 실패. 운영 전 문제 해결 필요.")
        return 1

if __name__ == "__main__":
    exit(main())
