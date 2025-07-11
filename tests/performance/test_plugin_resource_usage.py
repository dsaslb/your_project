import psutil
import time
import json
import requests
import threading
from datetime import datetime

class PluginResourceUsageTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            "cpu_usage": [],
            "memory_usage": [],
            "response_times": [],
            "plugin_status": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def monitor_system_resources(self, duration=60):
        """시스템 리소스 모니터링"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # CPU 사용량 측정
            cpu_percent = psutil.cpu_percent(interval=1)
            self.results["cpu_usage"].append({
                "timestamp": time.time(),
                "cpu_percent": cpu_percent
            })
            
            # 메모리 사용량 측정
            memory = psutil.virtual_memory()
            self.results["memory_usage"].append({
                "timestamp": time.time(),
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024
            })
            
            time.sleep(1)
    
    def test_api_response_times(self):
        """API 응답 시간 테스트"""
        endpoints = [
            "/api/admin/plugin-monitoring/status",
            "/api/admin/plugin-monitoring/metrics",
            "/api/admin/plugin-monitoring/performance",
            "/api/admin/plugin-monitoring/health",
            "/api/admin/plugin-monitoring/dashboard"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                self.results["response_times"].append({
                    "endpoint": endpoint,
                    "response_time_ms": (end_time - start_time) * 1000,
                    "status_code": response.status_code,
                    "timestamp": time.time()
                })
            except Exception as e:
                self.results["response_times"].append({
                    "endpoint": endpoint,
                    "response_time_ms": -1,
                    "status_code": -1,
                    "error": str(e),
                    "timestamp": time.time()
                })
    
    def test_plugin_status(self):
        """플러그인 상태 테스트"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            if response.status_code == 200:
                plugin_status = response.json()
                self.results["plugin_status"].append({
                    "timestamp": time.time(),
                    "status": plugin_status
                })
        except Exception as e:
            self.results["plugin_status"].append({
                "timestamp": time.time(),
                "error": str(e)
            })
    
    def run_load_test(self, concurrent_users=10, duration=60):
        """부하 테스트 실행"""
        def worker():
            start_time = time.time()
            while time.time() - start_time < duration:
                self.test_api_response_times()
                self.test_plugin_status()
                time.sleep(2)
        
        threads = []
        for i in range(concurrent_users):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
    def generate_report(self):
        """테스트 리포트 생성"""
        if not self.results["cpu_usage"]:
            return {"error": "No data collected"}
        
        # CPU 사용량 통계
        cpu_values = [item["cpu_percent"] for item in self.results["cpu_usage"]]
        cpu_stats = {
            "average": sum(cpu_values) / len(cpu_values),
            "max": max(cpu_values),
            "min": min(cpu_values)
        }
        
        # 메모리 사용량 통계
        memory_values = [item["memory_percent"] for item in self.results["memory_usage"]]
        memory_stats = {
            "average": sum(memory_values) / len(memory_values),
            "max": max(memory_values),
            "min": min(memory_values)
        }
        
        # 응답 시간 통계
        response_times = [item["response_time_ms"] for item in self.results["response_times"] if item["response_time_ms"] > 0]
        response_stats = {
            "average": sum(response_times) / len(response_times) if response_times else 0,
            "max": max(response_times) if response_times else 0,
            "min": min(response_times) if response_times else 0
        }
        
        report = {
            "test_info": {
                "timestamp": self.results["timestamp"],
                "duration": len(self.results["cpu_usage"]),
                "total_requests": len(self.results["response_times"])
            },
            "cpu_usage": cpu_stats,
            "memory_usage": memory_stats,
            "response_times": response_stats,
            "plugin_status_count": len(self.results["plugin_status"]),
            "recommendations": self.generate_recommendations(cpu_stats, memory_stats, response_stats)
        }
        
        return report
    
    def generate_recommendations(self, cpu_stats, memory_stats, response_stats):
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        if cpu_stats["average"] > 80:
            recommendations.append("CPU 사용량이 높습니다. 플러그인 최적화가 필요합니다.")
        
        if memory_stats["average"] > 85:
            recommendations.append("메모리 사용량이 높습니다. 메모리 누수 검사가 필요합니다.")
        
        if response_stats["average"] > 2000:
            recommendations.append("응답 시간이 느립니다. API 최적화가 필요합니다.")
        
        if response_stats["max"] > 5000:
            recommendations.append("최대 응답 시간이 너무 깁니다. 병목 지점을 찾아 최적화하세요.")
        
        if not recommendations:
            recommendations.append("시스템 성능이 양호합니다.")
        
        return recommendations
    
    def save_results(self, filename="plugin-resource-usage.json"):
        """결과를 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        report = self.generate_report()
        with open("plugin-resource-usage-report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

def main():
    """메인 테스트 실행"""
    print("플러그인 리소스 사용량 테스트 시작...")
    
    tester = PluginResourceUsageTest()
    
    # 시스템 리소스 모니터링 (백그라운드)
    resource_thread = threading.Thread(target=tester.monitor_system_resources, args=(60,))
    resource_thread.start()
    
    # 부하 테스트 실행
    print("부하 테스트 실행 중...")
    tester.run_load_test(concurrent_users=5, duration=30)
    
    # 리소스 모니터링 완료 대기
    resource_thread.join()
    
    # 결과 저장
    tester.save_results()
    
    # 리포트 출력
    report = tester.generate_report()
    print("\n=== 플러그인 리소스 사용량 테스트 결과 ===")
    print(f"테스트 시간: {report['test_info']['duration']}초")
    print(f"총 요청 수: {report['test_info']['total_requests']}")
    print(f"CPU 사용량 평균: {report['cpu_usage']['average']:.2f}%")
    print(f"메모리 사용량 평균: {report['memory_usage']['average']:.2f}%")
    print(f"응답 시간 평균: {report['response_times']['average']:.2f}ms")
    print("\n권장사항:")
    for rec in report['recommendations']:
        print(f"- {rec}")
    
    print("\n테스트 완료! 결과가 plugin-resource-usage.json 파일에 저장되었습니다.")

if __name__ == "__main__":
    main() 