#!/usr/bin/env python3
"""
플러그인 디버깅 도구
플러그인 개발 및 문제 해결을 위한 디버깅 도구
"""

import json
import time
import logging
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
import cProfile
import pstats
import io
from collections import defaultdict, deque


class PluginDebugTools:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.logger = self._setup_logger()
        self.performance_data = defaultdict(deque)
        self.debug_mode = False
        self.profiler = None

    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger("plugin_debug")
        logger.setLevel(logging.DEBUG)

        # 파일 핸들러
        log_file = Path("logs") / "plugin_debug.log"
        log_file.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 포맷터
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def enable_debug_mode(self, plugin_id: str) -> bool:
        """플러그인 디버그 모드 활성화"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                self.logger.error(f"플러그인 {plugin_id}이 존재하지 않습니다.")
                return False

            config_path = plugin_path / "config" / "plugin.json"
            if not config_path.exists():
                self.logger.error(
                    f"플러그인 설정 파일이 존재하지 않습니다: {config_path}"
                )
                return False

            # 설정 파일 읽기
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 디버그 모드 활성화
            config["debug_mode"] = True
            config["debug_settings"] = {
                "log_level": "DEBUG",
                "performance_monitoring": True,
                "error_tracking": True,
                "memory_monitoring": True,
            }
            config["updated_at"] = datetime.utcnow().isoformat()

            # 설정 파일 저장
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.debug_mode = True
            self.logger.info(f"✅ {plugin_id} 플러그인 디버그 모드가 활성화되었습니다.")
            return True

        except Exception as e:
            self.logger.error(f"디버그 모드 활성화 중 오류: {e}")
            return False

    def disable_debug_mode(self, plugin_id: str) -> bool:
        """플러그인 디버그 모드 비활성화"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                self.logger.error(f"플러그인 {plugin_id}이 존재하지 않습니다.")
                return False

            config_path = plugin_path / "config" / "plugin.json"
            if not config_path.exists():
                self.logger.error(
                    f"플러그인 설정 파일이 존재하지 않습니다: {config_path}"
                )
                return False

            # 설정 파일 읽기
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 디버그 모드 비활성화
            config["debug_mode"] = False
            if "debug_settings" in config:
                del config["debug_settings"]
            config["updated_at"] = datetime.utcnow().isoformat()

            # 설정 파일 저장
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.debug_mode = False
            self.logger.info(
                f"✅ {plugin_id} 플러그인 디버그 모드가 비활성화되었습니다."
            )
            return True

        except Exception as e:
            self.logger.error(f"디버그 모드 비활성화 중 오류: {e}")
            return False

    def start_performance_monitoring(self, plugin_id: str) -> bool:
        """성능 모니터링 시작"""
        try:
            self.logger.info(f"🚀 {plugin_id} 플러그인 성능 모니터링 시작")

            # 프로파일러 시작
            self.profiler = cProfile.Profile()
            self.profiler.enable()

            # 모니터링 스레드 시작
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitor_performance, args=(plugin_id,), daemon=True
            )
            self.monitoring_thread.start()

            return True

        except Exception as e:
            self.logger.error(f"성능 모니터링 시작 중 오류: {e}")
            return False

    def stop_performance_monitoring(self) -> Dict[str, Any]:
        """성능 모니터링 중지 및 결과 반환"""
        try:
            if not self.profiler:
                return {"error": "프로파일러가 시작되지 않았습니다."}

            # 프로파일러 중지
            self.profiler.disable()

            # 모니터링 중지
            self.monitoring_active = False
            if hasattr(self, "monitoring_thread"):
                self.monitoring_thread.join(timeout=5)

            # 프로파일 결과 분석
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s).sort_stats("cumulative")
            ps.print_stats(20)  # 상위 20개 함수

            # 성능 데이터 수집
            performance_summary = {
                "profile_stats": s.getvalue(),
                "memory_usage": self._get_memory_usage(),
                "cpu_usage": self._get_cpu_usage(),
                "performance_data": dict(self.performance_data),
            }

            self.logger.info("✅ 성능 모니터링이 중지되었습니다.")
            return performance_summary

        except Exception as e:
            self.logger.error(f"성능 모니터링 중지 중 오류: {e}")
            return {"error": str(e)}

    def _monitor_performance(self, plugin_id: str):
        """성능 모니터링 스레드"""
        while self.monitoring_active:
            try:
                timestamp = datetime.utcnow()

                # 메모리 사용량
                memory_usage = self._get_memory_usage()
                self.performance_data["memory"].append(
                    {"timestamp": timestamp.isoformat(), "usage": memory_usage}
                )

                # CPU 사용량
                cpu_usage = self._get_cpu_usage()
                self.performance_data["cpu"].append(
                    {"timestamp": timestamp.isoformat(), "usage": cpu_usage}
                )

                # 로그 레벨 조정
                if len(self.performance_data["memory"]) > 100:
                    for key in self.performance_data:
                        if len(self.performance_data[key]) > 100:
                            self.performance_data[key].popleft()

                time.sleep(1)  # 1초마다 측정

            except Exception as e:
                self.logger.error(f"성능 모니터링 중 오류: {e}")
                break

    def _get_memory_usage(self) -> Dict[str, float]:
        """메모리 사용량 조회"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()

            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent(),
            }
        except Exception as e:
            self.logger.error(f"메모리 사용량 조회 중 오류: {e}")
            return {"rss": 0, "vms": 0, "percent": 0}

    def _get_cpu_usage(self) -> Dict[str, float]:
        """CPU 사용량 조회"""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=0.1)

            return {"percent": cpu_percent, "num_threads": process.num_threads()}
        except Exception as e:
            self.logger.error(f"CPU 사용량 조회 중 오류: {e}")
            return {"percent": 0, "num_threads": 0}

    def analyze_plugin_logs(self, plugin_id: str, hours: int = 24) -> Dict[str, Any]:
        """플러그인 로그 분석"""
        try:
            log_file = Path("logs") / "plugin_debug.log"
            if not log_file.exists():
                return {"error": "로그 파일이 존재하지 않습니다."}

            # 시간 범위 계산
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)

            log_entries = []
            error_count = 0
            warning_count = 0
            info_count = 0

            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        # 로그 라인 파싱
                        if plugin_id in line:
                            parts = line.split(" - ", 3)
                            if len(parts) >= 4:
                                timestamp_str = parts[0]
                                level = parts[2]
                                message = parts[3].strip()

                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )

                                if start_time <= timestamp <= end_time:
                                    log_entries.append(
                                        {
                                            "timestamp": timestamp.isoformat(),
                                            "level": level,
                                            "message": message,
                                        }
                                    )

                                    if level == "ERROR":
                                        error_count += 1
                                    elif level == "WARNING":
                                        warning_count += 1
                                    elif level == "INFO":
                                        info_count += 1
                    except Exception:
                        continue

            return {
                "plugin_id": plugin_id,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "total_entries": len(log_entries),
                "error_count": error_count,
                "warning_count": warning_count,
                "info_count": info_count,
                "recent_entries": log_entries[-50:],  # 최근 50개 항목
            }

        except Exception as e:
            self.logger.error(f"로그 분석 중 오류: {e}")
            return {"error": str(e)}

    def diagnose_plugin_health(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 상태 진단"""
        try:
            plugin_path = self.base_path / plugin_id
            if not plugin_path.exists():
                return {"error": f"플러그인 {plugin_id}이 존재하지 않습니다."}

            diagnosis = {
                "plugin_id": plugin_id,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {},
            }

            # 파일 구조 검사
            diagnosis["checks"]["file_structure"] = self._check_file_structure(
                plugin_path
            )

            # 설정 파일 검사
            diagnosis["checks"]["config"] = self._check_config_file(plugin_path)

            # 의존성 검사
            diagnosis["checks"]["dependencies"] = self._check_dependencies(plugin_path)

            # 코드 품질 검사
            diagnosis["checks"]["code_quality"] = self._check_code_quality(plugin_path)

            # 성능 검사
            diagnosis["checks"]["performance"] = self._check_performance(plugin_id)

            # 전체 상태 평가
            diagnosis["overall_health"] = self._evaluate_overall_health(
                diagnosis["checks"]
            )

            return diagnosis

        except Exception as e:
            self.logger.error(f"플러그인 진단 중 오류: {e}")
            return {"error": str(e)}

    def _check_file_structure(self, plugin_path: Path) -> Dict[str, Any]:
        """파일 구조 검사"""
        required_files = [
            "backend/main.py",
            "backend/__init__.py",
            "config/plugin.json",
            "config/requirements.txt",
        ]

        missing_files = []
        existing_files = []

        for file_path in required_files:
            full_path = plugin_path / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)

        return {
            "status": "healthy" if not missing_files else "warning",
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_required": len(required_files),
            "total_existing": len(existing_files),
        }

    def _check_config_file(self, plugin_path: Path) -> Dict[str, Any]:
        """설정 파일 검사"""
        config_path = plugin_path / "config" / "plugin.json"

        if not config_path.exists():
            return {"status": "error", "error": "설정 파일이 존재하지 않습니다."}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            required_fields = ["id", "name", "version", "description", "author"]
            missing_fields = []

            for field in required_fields:
                if field not in config:
                    missing_fields.append(field)

            return {
                "status": "healthy" if not missing_fields else "warning",
                "config": config,
                "missing_fields": missing_fields,
                "debug_mode": config.get("debug_mode", False),
            }

        except json.JSONDecodeError as e:
            return {"status": "error", "error": f"설정 파일 JSON 파싱 오류: {e}"}
        except Exception as e:
            return {"status": "error", "error": f"설정 파일 검사 중 오류: {e}"}

    def _check_dependencies(self, plugin_path: Path) -> Dict[str, Any]:
        """의존성 검사"""
        requirements_path = plugin_path / "config" / "requirements.txt"

        if not requirements_path.exists():
            return {
                "status": "warning",
                "error": "requirements.txt 파일이 존재하지 않습니다.",
            }

        try:
            with open(requirements_path, "r", encoding="utf-8") as f:
                requirements = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

            return {
                "status": "healthy",
                "requirements": requirements,
                "count": len(requirements),
            }

        except Exception as e:
            return {"status": "error", "error": f"의존성 검사 중 오류: {e}"}

    def _check_code_quality(self, plugin_path: Path) -> Dict[str, Any]:
        """코드 품질 검사"""
        main_py_path = plugin_path / "backend" / "main.py"

        if not main_py_path.exists():
            return {"status": "error", "error": "main.py 파일이 존재하지 않습니다."}

        try:
            with open(main_py_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 기본적인 코드 품질 검사
            issues = []

            if len(content) < 100:
                issues.append("코드가 너무 짧습니다.")

            if "class" not in content:
                issues.append("클래스 정의가 없습니다.")

            if "def" not in content:
                issues.append("함수 정의가 없습니다.")

            if "import" not in content:
                issues.append("import 문이 없습니다.")

            return {
                "status": "healthy" if not issues else "warning",
                "file_size": len(content),
                "issues": issues,
                "has_class": "class" in content,
                "has_functions": "def" in content,
                "has_imports": "import" in content,
            }

        except Exception as e:
            return {"status": "error", "error": f"코드 품질 검사 중 오류: {e}"}

    def _check_performance(self, plugin_id: str) -> Dict[str, Any]:
        """성능 검사"""
        try:
            # 최근 성능 데이터 확인
            if plugin_id in self.performance_data:
                memory_data = list(self.performance_data["memory"])
                cpu_data = list(self.performance_data["cpu"])

                if memory_data and cpu_data:
                    latest_memory = memory_data[-1]["usage"]
                    latest_cpu = cpu_data[-1]["usage"]

                    return {
                        "status": "healthy",
                        "memory_usage": latest_memory,
                        "cpu_usage": latest_cpu,
                        "has_performance_data": True,
                    }

            return {
                "status": "info",
                "message": "성능 데이터가 없습니다. 성능 모니터링을 시작해주세요.",
                "has_performance_data": False,
            }

        except Exception as e:
            return {"status": "error", "error": f"성능 검사 중 오류: {e}"}

    def _evaluate_overall_health(self, checks: Dict[str, Any]) -> str:
        """전체 상태 평가"""
        error_count = 0
        warning_count = 0

        for check_result in checks.values():
            if isinstance(check_result, dict) and "status" in check_result:
                if check_result["status"] == "error":
                    error_count += 1
                elif check_result["status"] == "warning":
                    warning_count += 1

        if error_count > 0:
            return "critical"
        elif warning_count > 0:
            return "warning"
        else:
            return "healthy"

    def generate_debug_report(self, plugin_id: str) -> str:
        """디버그 리포트 생성"""
        try:
            # 진단 실행
            diagnosis = self.diagnose_plugin_health(plugin_id)

            # 로그 분석
            log_analysis = self.analyze_plugin_logs(plugin_id)

            # 리포트 파일 생성
            report_path = (
                Path("logs")
                / f"debug_report_{plugin_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )

            report = {
                "plugin_id": plugin_id,
                "generated_at": datetime.utcnow().isoformat(),
                "diagnosis": diagnosis,
                "log_analysis": log_analysis,
                "performance_data": (
                    dict(self.performance_data)
                    if plugin_id in self.performance_data
                    else {}
                ),
            }

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📊 디버그 리포트가 생성되었습니다: {report_path}")
            return str(report_path)

        except Exception as e:
            self.logger.error(f"디버그 리포트 생성 중 오류: {e}")
            return ""


def main():
    """메인 함수"""
    debug_tools = PluginDebugTools()

    print("🔧 플러그인 디버깅 도구")
    print("=" * 50)

    while True:
        print("\n사용 가능한 기능:")
        print("1. 디버그 모드 활성화")
        print("2. 디버그 모드 비활성화")
        print("3. 성능 모니터링 시작")
        print("4. 성능 모니터링 중지")
        print("5. 로그 분석")
        print("6. 플러그인 상태 진단")
        print("7. 디버그 리포트 생성")
        print("0. 종료")

        choice = input("\n선택 (0-7): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            plugin_id = input("플러그인 ID: ").strip()
            debug_tools.enable_debug_mode(plugin_id)
        elif choice == "2":
            plugin_id = input("플러그인 ID: ").strip()
            debug_tools.disable_debug_mode(plugin_id)
        elif choice == "3":
            plugin_id = input("플러그인 ID: ").strip()
            debug_tools.start_performance_monitoring(plugin_id)
        elif choice == "4":
            result = debug_tools.stop_performance_monitoring()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "5":
            plugin_id = input("플러그인 ID: ").strip()
            hours = input("분석할 시간 (시간, 기본값: 24): ").strip()
            hours = int(hours) if hours.isdigit() else 24
            result = debug_tools.analyze_plugin_logs(plugin_id, hours)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "6":
            plugin_id = input("플러그인 ID: ").strip()
            result = debug_tools.diagnose_plugin_health(plugin_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "7":
            plugin_id = input("플러그인 ID: ").strip()
            report_path = debug_tools.generate_debug_report(plugin_id)
            if report_path:
                print(f"📊 리포트 생성 완료: {report_path}")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
