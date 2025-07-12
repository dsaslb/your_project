import json
import time
import subprocess
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import psutil
import requests


@dataclass
class TestResult:
    """테스트 결과"""
    test_id: str
    plugin_id: str
    test_type: str  # unit, integration, performance, security
    status: str  # passed, failed, error, skipped
    duration: float
    message: str
    details: Dict
    created_at: str

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    plugin_id: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    throughput: float
    error_rate: float
    timestamp: str

@dataclass
class Documentation:
    """문서화 정보"""
    plugin_id: str
    api_docs: Dict
    user_guide: str
    developer_guide: str
    changelog: List[Dict]
    examples: List[Dict]
    last_updated: str

class PluginTestingSystem:
    """플러그인 테스트/모니터링/문서화 시스템"""
    
    def __init__(self, test_dir: str = "plugin_tests"):
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(exist_ok=True)
        
        # 테스트 데이터 파일
        self.test_results_file = self.test_dir / "test_results.json"
        self.performance_file = self.test_dir / "performance.json"
        self.documentation_file = self.test_dir / "documentation.json"
        self.test_config_file = self.test_dir / "test_config.json"
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # 초기화
        self._init_testing_system()
    
    def _init_testing_system(self):
        """테스트 시스템 초기화"""
        # 테스트 결과 초기화
        if not self.test_results_file.exists():
            with open(self.test_results_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        
        # 성능 데이터 초기화
        if not self.performance_file.exists():
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        
        # 문서화 데이터 초기화
        if not self.documentation_file.exists():
            with open(self.documentation_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        
        # 테스트 설정 초기화
        if not self.test_config_file.exists():
            config = {
                "test_timeout": 30,
                "performance_threshold": {
                    "cpu_usage": 80.0,
                    "memory_usage": 80.0,
                    "response_time": 1000.0,
                    "error_rate": 5.0
                },
                "monitoring_interval": 60,
                "test_suites": {
                    "unit": ["pytest", "-v"],
                    "integration": ["pytest", "-v", "--integration"],
                    "performance": ["pytest", "-v", "--performance"],
                    "security": ["pytest", "-v", "--security"]
                }
            }
            with open(self.test_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    
    def run_plugin_tests(self, plugin_id: str, test_type: str = "all") -> Dict:
        """플러그인 테스트 실행"""
        try:
            config = self._load_test_config()
            test_suites = config.get("test_suites", {})
            timeout = config.get("test_timeout", 30)
            
            results = {
                "plugin_id": plugin_id,
                "test_type": test_type,
                "started_at": datetime.now().isoformat(),
                "results": []
            }
            
            if test_type == "all":
                test_types = list(test_suites.keys())
            else:
                test_types = [test_type] if test_type in test_suites else []
            
            for test_type_name in test_types:
                test_result = self._run_single_test(plugin_id, test_type_name, test_suites[test_type_name], timeout)
                results["results"].append(test_result)
            
            results["completed_at"] = datetime.now().isoformat()
            results["total_tests"] = len(results["results"])
            results["passed_tests"] = len([r for r in results["results"] if r["status"] == "passed"])
            results["failed_tests"] = len([r for r in results["results"] if r["status"] == "failed"])
            
            # 결과 저장
            self._save_test_result(results)
            
            return results
            
        except Exception as e:
            return {
                "plugin_id": plugin_id,
                "test_type": test_type,
                "status": "error",
                "message": f"테스트 실행 실패: {e}",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
    
    def _run_single_test(self, plugin_id: str, test_type: str, test_command: List[str], timeout: int) -> Dict:
        """단일 테스트 실행"""
        test_id = f"{plugin_id}_{test_type}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # 플러그인 테스트 디렉토리 확인
            plugin_test_dir = Path("plugins") / plugin_id / "tests"
            if not plugin_test_dir.exists():
                return {
                    "test_id": test_id,
                    "plugin_id": plugin_id,
                    "test_type": test_type,
                    "status": "skipped",
                    "duration": 0,
                    "message": "테스트 디렉토리가 없습니다",
                    "details": {},
                    "created_at": datetime.now().isoformat()
                }
            
            # 테스트 실행
            cmd = test_command + [str(plugin_test_dir)]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=plugin_test_dir.parent
            )
            
            duration = time.time() - start_time
            
            # 결과 파싱
            if process.returncode == 0:
                status = "passed"
                message = "테스트 통과"
            else:
                status = "failed"
                message = f"테스트 실패 (exit code: {process.returncode})"
            
            return {
                "test_id": test_id,
                "plugin_id": plugin_id,
                "test_type": test_type,
                "status": status,
                "duration": duration,
                "message": message,
                "details": {
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "return_code": process.returncode
                },
                "created_at": datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                "test_id": test_id,
                "plugin_id": plugin_id,
                "test_type": test_type,
                "status": "error",
                "duration": duration,
                "message": "테스트 시간 초과",
                "details": {},
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_id": test_id,
                "plugin_id": plugin_id,
                "test_type": test_type,
                "status": "error",
                "duration": duration,
                "message": f"테스트 실행 오류: {e}",
                "details": {},
                "created_at": datetime.now().isoformat()
            }
    
    def start_performance_monitoring(self, plugin_id: Optional[str] = None):
        """성능 모니터링 시작"""
        if self.monitoring_active:
            return False
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(plugin_id,),
            daemon=True
        )
        self.monitoring_thread.start()
        return True
    
    def stop_performance_monitoring(self):
        """성능 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_worker(self, plugin_id: Optional[str] = None):
        """모니터링 워커 스레드"""
        config = self._load_test_config()
        interval = config.get("monitoring_interval", 60)
        threshold = config.get("performance_threshold", {})
        
        while self.monitoring_active:
            try:
                # 성능 메트릭 수집
                metrics = self._collect_performance_metrics(plugin_id)
                
                # 임계값 확인 및 알림
                alerts = self._check_performance_thresholds(metrics, threshold)
                if alerts:
                    self._send_performance_alerts(alerts)
                
                # 메트릭 저장
                self._save_performance_metrics(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                time.sleep(interval)
    
    def _collect_performance_metrics(self, plugin_id: Optional[str] = None) -> List[Dict]:
        """성능 메트릭 수집"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        # 시스템 전체 메트릭
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 플러그인별 메트릭 (실제 구현에서는 더 정교한 수집 필요)
        if plugin_id:
            # 특정 플러그인 메트릭
            plugin_metrics = {
                "plugin_id": plugin_id,
                "cpu_usage": float(str(cpu_usage)) * 0.1,  # 플러그인별 CPU 사용량 추정
                "memory_usage": float(str(memory_usage)) * 0.1,  # 플러그인별 메모리 사용량 추정
                "response_time": self._measure_plugin_response_time(plugin_id),
                "throughput": self._measure_plugin_throughput(plugin_id),
                "error_rate": self._measure_plugin_error_rate(plugin_id),
                "timestamp": timestamp
            }
            metrics.append(plugin_metrics)
        else:
            # 모든 플러그인 메트릭
            plugin_ids = self._get_active_plugin_ids()
            for pid in plugin_ids:
                plugin_metrics = {
                    "plugin_id": pid,
                    "cpu_usage": float(str(cpu_usage)) * 0.1,
                    "memory_usage": float(str(memory_usage)) * 0.1,
                    "response_time": self._measure_plugin_response_time(pid),
                    "throughput": self._measure_plugin_throughput(pid),
                    "error_rate": self._measure_plugin_error_rate(pid),
                    "timestamp": timestamp
                }
                metrics.append(plugin_metrics)
        
        return metrics
    
    def _measure_plugin_response_time(self, plugin_id: str) -> float:
        """플러그인 응답 시간 측정"""
        try:
            # 플러그인 API 엔드포인트 테스트
            start_time = time.time()
            response = requests.get(f"http://localhost:5000/api/plugins/{plugin_id}/status", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                return (end_time - start_time) * 1000  # ms로 변환
            else:
                return 9999.0  # 오류 시 높은 값 반환
        except:
            return 9999.0
    
    def _measure_plugin_throughput(self, plugin_id: str) -> float:
        """플러그인 처리량 측정"""
        # 실제 구현에서는 더 정교한 측정 필요
        return 100.0  # 요청/초
    
    def _measure_plugin_error_rate(self, plugin_id: str) -> float:
        """플러그인 오류율 측정"""
        # 실제 구현에서는 더 정교한 측정 필요
        return 0.1  # 0.1%
    
    def _get_active_plugin_ids(self) -> List[str]:
        """활성 플러그인 ID 목록 조회"""
        # 실제 구현에서는 플러그인 매니저에서 조회
        return ["your_program_management"]
    
    def _check_performance_thresholds(self, metrics: List[Dict], threshold: Dict) -> List[Dict]:
        """성능 임계값 확인"""
        alerts = []
        
        for metric in metrics:
            if metric["cpu_usage"] > threshold.get("cpu_usage", 80.0):
                alerts.append({
                    "plugin_id": metric["plugin_id"],
                    "type": "cpu_high",
                    "value": metric["cpu_usage"],
                    "threshold": threshold.get("cpu_usage", 80.0),
                    "timestamp": metric["timestamp"]
                })
            
            if metric["memory_usage"] > threshold.get("memory_usage", 80.0):
                alerts.append({
                    "plugin_id": metric["plugin_id"],
                    "type": "memory_high",
                    "value": metric["memory_usage"],
                    "threshold": threshold.get("memory_usage", 80.0),
                    "timestamp": metric["timestamp"]
                })
            
            if metric["response_time"] > threshold.get("response_time", 1000.0):
                alerts.append({
                    "plugin_id": metric["plugin_id"],
                    "type": "response_slow",
                    "value": metric["response_time"],
                    "threshold": threshold.get("response_time", 1000.0),
                    "timestamp": metric["timestamp"]
                })
            
            if metric["error_rate"] > threshold.get("error_rate", 5.0):
                alerts.append({
                    "plugin_id": metric["plugin_id"],
                    "type": "error_high",
                    "value": metric["error_rate"],
                    "threshold": threshold.get("error_rate", 5.0),
                    "timestamp": metric["timestamp"]
                })
        
        return alerts
    
    def _send_performance_alerts(self, alerts: List[Dict]):
        """성능 알림 발송"""
        for alert in alerts:
            print(f"성능 알림: {alert['plugin_id']} - {alert['type']} (값: {alert['value']}, 임계값: {alert['threshold']})")
            # 실제 구현에서는 이메일, 슬랙 등으로 알림 발송
    
    def generate_plugin_documentation(self, plugin_id: str) -> Dict:
        """플러그인 문서 자동 생성"""
        try:
            plugin_dir = Path("plugins") / plugin_id
            if not plugin_dir.exists():
                return {"error": "플러그인을 찾을 수 없습니다"}
            
            # 플러그인 매니페스트 읽기
            manifest_file = plugin_dir / "config" / "plugin.json"
            if not manifest_file.exists():
                return {"error": "플러그인 매니페스트를 찾을 수 없습니다"}
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # API 문서 생성
            api_docs = self._generate_api_documentation(plugin_id, plugin_dir)
            
            # 사용자 가이드 생성
            user_guide = self._generate_user_guide(manifest, plugin_dir)
            
            # 개발자 가이드 생성
            developer_guide = self._generate_developer_guide(manifest, plugin_dir)
            
            # 변경 이력 생성
            changelog = self._generate_changelog(plugin_id)
            
            # 예제 생성
            examples = self._generate_examples(plugin_id, plugin_dir)
            
            documentation = {
                "plugin_id": plugin_id,
                "api_docs": api_docs,
                "user_guide": user_guide,
                "developer_guide": developer_guide,
                "changelog": changelog,
                "examples": examples,
                "last_updated": datetime.now().isoformat()
            }
            
            # 문서 저장
            self._save_documentation(plugin_id, documentation)
            
            return documentation
            
        except Exception as e:
            return {"error": f"문서 생성 실패: {e}"}
    
    def _generate_api_documentation(self, plugin_id: str, plugin_dir: Path) -> Dict:
        """API 문서 생성"""
        api_docs = {
            "endpoints": [],
            "models": [],
            "examples": []
        }
        
        # 백엔드 파일 분석
        backend_dir = plugin_dir / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.glob("*.py"):
                # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 라우트 찾기
                if "@bp.route" in content or "@app.route" in content:
                    api_docs["endpoints"].append({
                        "file": py_file.name,
                        "routes": self._extract_routes(content)
                    })
        
        return api_docs
    
    def _extract_routes(self, content: str) -> List[Dict]:
        """코드에서 라우트 추출"""
        routes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '@bp.route' in line or '@app.route' in line:
                # 간단한 라우트 추출
                route_info = {
                    "line": i + 1,
                    "route": line.strip(),
                    "method": "GET"  # 기본값
                }
                routes.append(route_info)
        
        return routes
    
    def _generate_user_guide(self, manifest: Dict, plugin_dir: Path) -> str:
        """사용자 가이드 생성"""
        guide = f"""# {manifest.get('name', 'Unknown Plugin')} 사용자 가이드

## 개요
{manifest.get('description', '설명이 없습니다.')}

## 설치
1. 플러그인을 다운로드합니다.
2. 플러그인 디렉토리에 설치합니다.
3. 플러그인을 활성화합니다.

## 설정
플러그인 설정은 관리자 패널에서 할 수 있습니다.

## 사용법
자세한 사용법은 플러그인 문서를 참조하세요.
"""
        return guide
    
    def _generate_developer_guide(self, manifest: Dict, plugin_dir: Path) -> str:
        """개발자 가이드 생성"""
        guide = f"""# {manifest.get('name', 'Unknown Plugin')} 개발자 가이드

## 구조
```
{plugin_dir.name}/
├── backend/          # 백엔드 코드
├── config/           # 설정 파일
├── templates/        # 템플릿 파일
└── static/          # 정적 파일
```

## 의존성
{', '.join(manifest.get('dependencies', []))}

## 권한
{', '.join(manifest.get('permissions', []))}

## API
플러그인 API는 백엔드 디렉토리의 Python 파일에 정의되어 있습니다.
"""
        return guide
    
    def _generate_changelog(self, plugin_id: str) -> List[Dict]:
        """변경 이력 생성"""
        # 실제 구현에서는 Git 히스토리나 릴리즈 정보에서 생성
        return [
            {
                "version": "1.0.0",
                "date": datetime.now().isoformat(),
                "changes": ["초기 버전"]
            }
        ]
    
    def _generate_examples(self, plugin_id: str, plugin_dir: Path) -> List[Dict]:
        """예제 생성"""
        examples = []
        
        # 예제 파일 찾기
        example_files = list(plugin_dir.glob("**/example*.py")) + list(plugin_dir.glob("**/demo*.py"))
        
        for example_file in example_files:
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            examples.append({
                "file": example_file.name,
                "description": f"{example_file.name} 예제",
                "code": content
            })
        
        return examples
    
    def get_test_results(self, plugin_id: Optional[str] = None, test_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """테스트 결과 조회"""
        try:
            results = self._load_test_results()
            
            # 필터링
            if plugin_id:
                results = [r for r in results if r.get('plugin_id') == plugin_id]
            if test_type:
                results = [r for r in results if r.get('test_type') == test_type]
            
            # 최신 순으로 정렬
            results.sort(key=lambda x: x.get('started_at', ''), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            print(f"테스트 결과 조회 실패: {e}")
            return []
    
    def get_performance_metrics(self, plugin_id: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """성능 메트릭 조회"""
        try:
            metrics = self._load_performance_metrics()
            
            # 시간 필터링
            cutoff_time = datetime.now() - timedelta(hours=hours)
            metrics = [m for m in metrics if datetime.fromisoformat(m['timestamp']) > cutoff_time]
            
            # 플러그인 필터링
            if plugin_id:
                metrics = [m for m in metrics if m.get('plugin_id') == plugin_id]
            
            return metrics
            
        except Exception as e:
            print(f"성능 메트릭 조회 실패: {e}")
            return []
    
    def get_documentation(self, plugin_id: str) -> Optional[Dict]:
        """문서 조회"""
        try:
            docs = self._load_documentation()
            return docs.get(plugin_id)
        except Exception as e:
            print(f"문서 조회 실패: {e}")
            return None
    
    def _load_test_config(self) -> Dict:
        """테스트 설정 로드"""
        try:
            with open(self.test_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _load_test_results(self) -> List[Dict]:
        """테스트 결과 로드"""
        try:
            with open(self.test_results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_test_result(self, result: Dict):
        """테스트 결과 저장"""
        try:
            results = self._load_test_results()
            results.append(result)
            
            with open(self.test_results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"테스트 결과 저장 실패: {e}")
    
    def _load_performance_metrics(self) -> List[Dict]:
        """성능 메트릭 로드"""
        try:
            with open(self.performance_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_performance_metrics(self, metrics: List[Dict]):
        """성능 메트릭 저장"""
        try:
            all_metrics = self._load_performance_metrics()
            all_metrics.extend(metrics)
            
            # 최근 7일 데이터만 유지
            cutoff_time = datetime.now() - timedelta(days=7)
            all_metrics = [m for m in all_metrics if datetime.fromisoformat(m['timestamp']) > cutoff_time]
            
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                json.dump(all_metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"성능 메트릭 저장 실패: {e}")
    
    def _load_documentation(self) -> Dict:
        """문서 로드"""
        try:
            with open(self.documentation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_documentation(self, plugin_id: str, documentation: Dict):
        """문서 저장"""
        try:
            docs = self._load_documentation()
            docs[plugin_id] = documentation
            
            with open(self.documentation_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"문서 저장 실패: {e}") 
