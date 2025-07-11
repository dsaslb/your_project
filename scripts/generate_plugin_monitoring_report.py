#!/usr/bin/env python3
"""
플러그인 모니터링 리포트 생성기
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginMonitoringReportGenerator:
    """플러그인 모니터링 리포트 생성기"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.report_data = {}
    
    def collect_plugin_status(self) -> Dict[str, Any]:
        """플러그인 상태 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"플러그인 상태 수집 실패: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"플러그인 상태 수집 오류: {e}")
            return {}
    
    def collect_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/performance", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"성능 메트릭 수집 실패: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"성능 메트릭 수집 오류: {e}")
            return {}
    
    def collect_health_data(self) -> Dict[str, Any]:
        """헬스 데이터 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"헬스 데이터 수집 실패: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"헬스 데이터 수집 오류: {e}")
            return {}
    
    def generate_report(self) -> Dict[str, Any]:
        """리포트 생성"""
        logger.info("플러그인 모니터링 리포트 생성 시작")
        
        # 데이터 수집
        plugin_status = self.collect_plugin_status()
        performance_metrics = self.collect_performance_metrics()
        health_data = self.collect_health_data()
        
        # 리포트 구조 생성
        report = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "base_url": self.base_url,
                "version": "1.0"
            },
            "plugin_status": plugin_status,
            "performance_metrics": performance_metrics,
            "health_data": health_data,
            "summary": self._generate_summary(plugin_status, performance_metrics, health_data)
        }
        
        self.report_data = report
        logger.info("플러그인 모니터링 리포트 생성 완료")
        return report
    
    def _generate_summary(self, plugin_status: Dict, performance_metrics: Dict, health_data: Dict) -> Dict[str, Any]:
        """요약 정보 생성"""
        summary = {
            "total_plugins": 0,
            "active_plugins": 0,
            "inactive_plugins": 0,
            "error_plugins": 0,
            "avg_response_time": 0,
            "avg_cpu_usage": 0,
            "avg_memory_usage": 0,
            "health_score": 0
        }
        
        # 플러그인 상태 분석
        if "plugins" in plugin_status:
            plugins = plugin_status["plugins"]
            summary["total_plugins"] = len(plugins)
            
            for plugin in plugins:
                status = plugin.get("status", "unknown")
                if status == "active":
                    summary["active_plugins"] += 1
                elif status == "inactive":
                    summary["inactive_plugins"] += 1
                elif status == "error":
                    summary["error_plugins"] += 1
        
        # 성능 메트릭 분석
        if "metrics" in performance_metrics:
            metrics = performance_metrics["metrics"]
            
            response_times = []
            cpu_usage = []
            memory_usage = []
            
            for metric in metrics:
                if "response_time" in metric:
                    response_times.append(metric["response_time"])
                if "cpu_usage" in metric:
                    cpu_usage.append(metric["cpu_usage"])
                if "memory_usage" in metric:
                    memory_usage.append(metric["memory_usage"])
            
            if response_times:
                summary["avg_response_time"] = sum(response_times) / len(response_times)
            if cpu_usage:
                summary["avg_cpu_usage"] = sum(cpu_usage) / len(cpu_usage)
            if memory_usage:
                summary["avg_memory_usage"] = sum(memory_usage) / len(memory_usage)
        
        # 헬스 점수 계산
        if summary["total_plugins"] > 0:
            health_score = (
                (summary["active_plugins"] / summary["total_plugins"]) * 0.6 +
                (1 - summary["avg_cpu_usage"] / 100) * 0.2 +
                (1 - summary["avg_memory_usage"] / 100) * 0.2
            ) * 100
            summary["health_score"] = round(health_score, 2)
        
        return summary
    
    def save_report(self, filename: str = None) -> str:
        """리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plugin_monitoring_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"리포트 저장됨: {filename}")
        return filename
    
    def print_summary(self):
        """요약 정보 출력"""
        if not self.report_data:
            logger.warning("리포트 데이터가 없습니다. generate_report()를 먼저 실행하세요.")
            return
        
        summary = self.report_data.get("summary", {})
        
        print("\n=== 플러그인 모니터링 리포트 요약 ===")
        print(f"생성 시간: {self.report_data['report_info']['generated_at']}")
        print(f"총 플러그인 수: {summary.get('total_plugins', 0)}")
        print(f"활성 플러그인: {summary.get('active_plugins', 0)}")
        print(f"비활성 플러그인: {summary.get('inactive_plugins', 0)}")
        print(f"오류 플러그인: {summary.get('error_plugins', 0)}")
        print(f"평균 응답 시간: {summary.get('avg_response_time', 0):.3f}초")
        print(f"평균 CPU 사용률: {summary.get('avg_cpu_usage', 0):.2f}%")
        print(f"평균 메모리 사용률: {summary.get('avg_memory_usage', 0):.2f}%")
        print(f"헬스 점수: {summary.get('health_score', 0):.1f}/100")
        print("=" * 50)

def main():
    """메인 실행 함수"""
    print("플러그인 모니터링 리포트 생성기 시작")
    
    # 리포트 생성기 인스턴스 생성
    generator = PluginMonitoringReportGenerator()
    
    # 리포트 생성
    report = generator.generate_report()
    
    # 요약 출력
    generator.print_summary()
    
    # 리포트 저장
    filename = generator.save_report()
    
    print(f"\n리포트가 {filename}에 저장되었습니다.")
    print("플러그인 모니터링 리포트 생성 완료")

if __name__ == "__main__":
    main() 