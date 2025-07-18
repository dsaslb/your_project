#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD 시스템 테스트 스크립트
전체 CI/CD 파이프라인의 각 단계를 테스트하고 검증합니다.
"""

import os
import sys
import json
import yaml
import subprocess
import requests
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import queue

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CICDSystemTester:
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        self.start_time = datetime.now()

    def log_test(
        self, test_name: str, success: bool, message: str = "", duration: float = 0
    ):
        """테스트 결과 로깅"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""

        result = f"[{timestamp}] {status} - {test_name}{duration_str}"
        if message:
            result += f": {message}"
        print(result)

        self.test_results[test_name] = {
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": timestamp,
        }

        if not success:
            self.errors.append(f"{test_name}: {message}")
        elif message and "warning" in message.lower():
            self.warnings.append(f"{test_name}: {message}")

    def test_prerequisites(self) -> bool:
        """전제 조건 테스트"""
        logger.info("전제 조건 테스트 시작")

        tests = [
            ("Git 설치 확인", self.check_git_installation),
            ("Docker 설치 확인", self.check_docker_installation),
            ("Python 버전 확인", self.check_python_version),
            ("Node.js 설치 확인", self.check_nodejs_installation),
            ("필수 파일 확인", self.check_required_files),
            ("환경 변수 확인", self.check_environment_variables),
            ("네트워크 연결 확인", self.check_network_connectivity),
        ]

        all_passed = True
        for test_name, test_func in tests:
            start_time = time.time()
            try:
                success = test_func()
                duration = time.time() - start_time
                self.log_test(test_name, success, duration=duration)
                if not success:
                    all_passed = False
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(test_name, False, str(e), duration)
                all_passed = False

        return all_passed

    def check_git_installation(self) -> bool:
        """Git 설치 확인"""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, check=True
            )
            return "git version" in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_docker_installation(self) -> bool:
        """Docker 설치 확인"""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            return "Docker version" in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_python_version(self) -> bool:
        """Python 버전 확인"""
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            version = result.stdout.strip()
            # Python 3.9 이상 확인
            if "Python 3." in version:
                version_num = version.split()[1]
                major, minor = map(int, version_num.split(".")[:2])
                return major == 3 and minor >= 9
            return False
        except Exception:
            return False

    def check_nodejs_installation(self) -> bool:
        """Node.js 설치 확인"""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=True
            )
            version = result.stdout.strip()
            # Node.js 16 이상 확인
            if version.startswith("v"):
                version_num = version[1:]
                major = int(version_num.split(".")[0])
                return major >= 16
            return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_required_files(self) -> bool:
        """필수 파일 확인"""
        required_files = [
            "app.py",
            "requirements.txt",
            "package.json",
            "deploy_config.yaml",
            ".github/workflows/plugin-ci-cd.yml",
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.log_test(
                "필수 파일 확인", False, f"누락된 파일: {', '.join(missing_files)}"
            )
            return False

        return True

    def check_environment_variables(self) -> bool:
        """환경 변수 확인"""
        required_vars = ["FLASK_ENV", "DATABASE_URL", "SECRET_KEY"]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log_test(
                "환경 변수 확인", False, f"누락된 환경 변수: {', '.join(missing_vars)}"
            )
            return False

        return True

    def check_network_connectivity(self) -> bool:
        """네트워크 연결 확인"""
        try:
            response = requests.get("https://httpbin.org/get", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def test_code_quality_checks(self) -> bool:
        """코드 품질 검사 테스트"""
        logger.info("코드 품질 검사 테스트 시작")

        tests = [
            ("Black 코드 포맷팅", self.test_black_formatting),
            ("isort 임포트 정렬", self.test_isort_sorting),
            ("Flake8 린팅", self.test_flake8_linting),
            ("MyPy 타입 검사", self.test_mypy_type_checking),
            ("Bandit 보안 검사", self.test_bandit_security),
            ("Safety 취약점 검사", self.test_safety_vulnerabilities),
        ]

        all_passed = True
        for test_name, test_func in tests:
            start_time = time.time()
            try:
                success = test_func()
                duration = time.time() - start_time
                self.log_test(test_name, success, duration=duration)
                if not success:
                    all_passed = False
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(test_name, False, str(e), duration)
                all_passed = False

        return all_passed

    def test_black_formatting(self) -> bool:
        """Black 코드 포맷팅 테스트"""
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", "."], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_isort_sorting(self) -> bool:
        """isort 임포트 정렬 테스트"""
        try:
            result = subprocess.run(
                ["isort", "--check-only", "--diff", "."], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_flake8_linting(self) -> bool:
        """Flake8 린팅 테스트"""
        try:
            result = subprocess.run(
                [
                    "flake8",
                    ".",
                    "--count",
                    "--select=E9,F63,F7,F82",
                    "--show-source",
                    "--statistics",
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_mypy_type_checking(self) -> bool:
        """MyPy 타입 검사 테스트"""
        try:
            result = subprocess.run(
                [
                    "mypy",
                    "api/",
                    "core/",
                    "--ignore-missing-imports",
                    "--no-strict-optional",
                ],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def test_bandit_security(self) -> bool:
        """Bandit 보안 검사 테스트"""
        try:
            result = subprocess.run(
                ["bandit", "-r", "api/", "core/", "-f", "json"],
                capture_output=True,
                text=True,
            )
            # Bandit은 이슈가 발견되어도 0을 반환하므로 결과를 파싱해서 확인
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    issues = len(data.get("results", []))
                    return issues == 0
                except json.JSONDecodeError:
                    return True
            return False
        except FileNotFoundError:
            return False

    def test_safety_vulnerabilities(self) -> bool:
        """Safety 취약점 검사 테스트"""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"], capture_output=True, text=True
            )
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    vulnerabilities = len(data.get("vulnerabilities", []))
                    return vulnerabilities == 0
                except json.JSONDecodeError:
                    return True
            return False
        except FileNotFoundError:
            return False

    def test_unit_tests(self) -> bool:
        """단위 테스트 실행"""
        logger.info("단위 테스트 실행")

        try:
            # 테스트 환경 설정
            os.environ["FLASK_ENV"] = "testing"
            os.environ["DATABASE_URL"] = "sqlite:///test.db"
            os.environ["SECRET_KEY"] = "test-secret-key"

            # pytest 실행
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short", "--cov=api", "--cov=core"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            success = result.returncode == 0
            coverage_match = None

            # 커버리지 정보 추출
            for line in result.stdout.split("\n"):
                if "TOTAL" in line and "%" in line:
                    coverage_match = line
                    break

            message = (
                f"테스트 완료 - 커버리지: {coverage_match}"
                if coverage_match
                else "테스트 완료"
            )
            self.log_test("단위 테스트", success, message)

            return success

        except subprocess.TimeoutExpired:
            self.log_test("단위 테스트", False, "테스트 시간 초과")
            return False
        except Exception as e:
            self.log_test("단위 테스트", False, str(e))
            return False

    def test_integration_tests(self) -> bool:
        """통합 테스트 실행"""
        logger.info("통합 테스트 실행")

        try:
            # 서버 시작
            server_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 서버 시작 대기
            time.sleep(10)

            # 헬스 체크
            try:
                response = requests.get("http://localhost:5000/health", timeout=10)
                if response.status_code != 200:
                    raise Exception("서버 헬스 체크 실패")
            except Exception as e:
                server_process.terminate()
                self.log_test("통합 테스트", False, f"서버 시작 실패: {e}")
                return False

            # API 테스트
            api_tests = [
                ("플러그인 목록 API", "GET", "/api/plugins/list"),
                ("플러그인 상태 API", "GET", "/api/plugins/status"),
                ("대시보드 API", "GET", "/api/dashboard"),
                ("플러그인 설정 API", "GET", "/api/plugin-settings/core_management"),
            ]

            all_passed = True
            for test_name, method, endpoint in api_tests:
                try:
                    if method == "GET":
                        response = requests.get(
                            f"http://localhost:5000{endpoint}", timeout=10
                        )
                    else:
                        response = requests.post(
                            f"http://localhost:5000{endpoint}", timeout=10
                        )

                    if response.status_code == 200:
                        self.log_test(f"API 테스트 - {test_name}", True)
                    else:
                        self.log_test(
                            f"API 테스트 - {test_name}",
                            False,
                            f"상태 코드: {response.status_code}",
                        )
                        all_passed = False

                except Exception as e:
                    self.log_test(f"API 테스트 - {test_name}", False, str(e))
                    all_passed = False

            # 서버 종료
            server_process.terminate()
            server_process.wait()

            return all_passed

        except Exception as e:
            self.log_test("통합 테스트", False, str(e))
            return False

    def test_performance_tests(self) -> bool:
        """성능 테스트 실행"""
        logger.info("성능 테스트 실행")

        try:
            # Locust 성능 테스트
            locust_process = subprocess.Popen(
                [
                    "locust",
                    "-f",
                    "tests/performance/locustfile.py",
                    "--headless",
                    "--users",
                    "5",
                    "--spawn-rate",
                    "1",
                    "--run-time",
                    "30s",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 테스트 완료 대기
            stdout, stderr = locust_process.communicate(timeout=60)

            success = locust_process.returncode == 0
            message = "성능 테스트 완료"

            # 성능 메트릭 추출
            output = stdout.decode() + stderr.decode()
            if "RPS" in output:
                for line in output.split("\n"):
                    if "RPS" in line:
                        message += f" - {line.strip()}"
                        break

            self.log_test("성능 테스트", success, message)
            return success

        except subprocess.TimeoutExpired:
            self.log_test("성능 테스트", False, "성능 테스트 시간 초과")
            return False
        except Exception as e:
            self.log_test("성능 테스트", False, str(e))
            return False

    def test_plugin_validation(self) -> bool:
        """플러그인 검증 테스트"""
        logger.info("플러그인 검증 테스트")

        try:
            result = subprocess.run(
                [sys.executable, "scripts/validate_plugins.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            success = result.returncode == 0
            message = "플러그인 검증 완료"

            # 검증 결과 추출
            if "성공률" in result.stdout:
                for line in result.stdout.split("\n"):
                    if "성공률" in line:
                        message += f" - {line.strip()}"
                        break

            self.log_test("플러그인 검증", success, message)
            return success

        except subprocess.TimeoutExpired:
            self.log_test("플러그인 검증", False, "검증 시간 초과")
            return False
        except Exception as e:
            self.log_test("플러그인 검증", False, str(e))
            return False

    def test_docker_build(self) -> bool:
        """Docker 빌드 테스트"""
        logger.info("Docker 빌드 테스트")

        try:
            # Dockerfile 확인
            if not Path("Dockerfile").exists():
                self.log_test("Docker 빌드", False, "Dockerfile이 없습니다")
                return False

            # Docker 빌드
            result = subprocess.run(
                ["docker", "build", "-t", "plugin-system:test", "."],
                capture_output=True,
                text=True,
                timeout=300,
            )

            success = result.returncode == 0
            message = "Docker 이미지 빌드 완료"

            if success:
                # 테스트 이미지 정리
                subprocess.run(
                    ["docker", "rmi", "plugin-system:test"], capture_output=True
                )

            self.log_test("Docker 빌드", success, message)
            return success

        except subprocess.TimeoutExpired:
            self.log_test("Docker 빌드", False, "빌드 시간 초과")
            return False
        except Exception as e:
            self.log_test("Docker 빌드", False, str(e))
            return False

    def test_deployment_simulation(self) -> bool:
        """배포 시뮬레이션 테스트"""
        logger.info("배포 시뮬레이션 테스트")

        try:
            # 배포 설정 파일 확인
            if not Path("deploy_config.yaml").exists():
                self.log_test("배포 시뮬레이션", False, "배포 설정 파일이 없습니다")
                return False

            # 배포 스크립트 확인
            if not Path("scripts/deploy_staging.py").exists():
                self.log_test("배포 시뮬레이션", False, "배포 스크립트가 없습니다")
                return False

            # 배포 설정 파싱 테스트
            with open("deploy_config.yaml", "r") as f:
                config = yaml.safe_load(f)

            required_sections = [
                "staging",
                "production",
                "database",
                "plugins",
                "monitoring",
            ]
            # config가 None이거나 dict가 아닐 경우를 안전하게 처리합니다.
            if not isinstance(config, dict):  # pyright: ignore
                self.log_test(
                    "배포 시뮬레이션",
                    False,
                    "배포 설정 파일이 올바른 YAML 객체가 아닙니다",
                )
                return False
            missing_sections = [
                section for section in required_sections if section not in config
            ]  # pyright: ignore

            if missing_sections:
                self.log_test(
                    "배포 시뮬레이션",
                    False,
                    f"누락된 설정 섹션: {', '.join(missing_sections)}",
                )
                return False

            self.log_test("배포 시뮬레이션", True, "배포 설정 검증 완료")
            return True

        except Exception as e:
            self.log_test("배포 시뮬레이션", False, str(e))
            return False

    def test_report_generation(self) -> bool:
        """리포트 생성 테스트"""
        logger.info("리포트 생성 테스트")

        try:
            # 리포트 생성 스크립트 확인
            if not Path("scripts/generate_ci_report.py").exists():
                self.log_test("리포트 생성", False, "리포트 생성 스크립트가 없습니다")
                return False

            # 테스트 데이터 생성
            test_artifacts_dir = Path("test_artifacts")
            test_artifacts_dir.mkdir(exist_ok=True)

            # 가짜 테스트 결과 생성
            fake_coverage = {
                "summary": {
                    "total_plugins": 3,
                    "valid_plugins": 3,
                    "test_coverage": 85.5,
                    "security_issues": 0,
                    "performance_score": 92.0,
                    "deployment_status": "success",
                }
            }

            with open(test_artifacts_dir / "fake_report.json", "w") as f:
                json.dump(fake_coverage, f)

            # 리포트 생성 테스트
            result = subprocess.run(
                [sys.executable, "scripts/generate_ci_report.py"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            success = result.returncode == 0
            message = "리포트 생성 완료"

            # 생성된 리포트 확인
            if Path("ci-report.html").exists():
                message += " - HTML 리포트 생성됨"

            # 테스트 데이터 정리
            import shutil

            shutil.rmtree(test_artifacts_dir, ignore_errors=True)

            self.log_test("리포트 생성", success, message)
            return success

        except subprocess.TimeoutExpired:
            self.log_test("리포트 생성", False, "리포트 생성 시간 초과")
            return False
        except Exception as e:
            self.log_test("리포트 생성", False, str(e))
            return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 CI/CD 시스템 테스트 시작")
        print("=" * 60)

        test_suites = [
            ("전제 조건 테스트", self.test_prerequisites),
            ("코드 품질 검사", self.test_code_quality_checks),
            ("단위 테스트", self.test_unit_tests),
            ("통합 테스트", self.test_integration_tests),
            ("성능 테스트", self.test_performance_tests),
            ("플러그인 검증", self.test_plugin_validation),
            ("Docker 빌드", self.test_docker_build),
            ("배포 시뮬레이션", self.test_deployment_simulation),
            ("리포트 생성", self.test_report_generation),
        ]

        total_tests = 0
        passed_tests = 0

        for suite_name, suite_func in test_suites:
            print(f"\n📋 {suite_name}")
            print("-" * 40)

            try:
                success = suite_func()
                if success:
                    passed_tests += 1
                total_tests += 1

            except Exception as e:
                print(f"❌ {suite_name} 실행 중 오류: {e}")
                self.errors.append(f"{suite_name}: {e}")

        # 최종 결과 출력
        print("\n" + "=" * 60)
        print("📊 CI/CD 시스템 테스트 결과")
        print("=" * 60)

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print(f"총 테스트: {total_tests}")
        print(f"통과: {passed_tests}")
        print(f"실패: {total_tests - passed_tests}")
        print(
            f"성공률: {(passed_tests / total_tests * 100):.1f}%"
            if total_tests > 0
            else "0%"
        )
        print(f"소요 시간: {duration:.2f}초")

        if self.errors:
            print(f"\n❌ 오류 목록:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  경고 목록:")
            for warning in self.warnings:
                print(f"  - {warning}")

        # 상세 결과 저장
        self.save_detailed_results()

        return passed_tests == total_tests

    def save_detailed_results(self):
        """상세 결과 저장"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(
                    1 for result in self.test_results.values() if result["success"]
                ),
                "failed_tests": sum(
                    1 for result in self.test_results.values() if not result["success"]
                ),
                "duration": (datetime.now() - self.start_time).total_seconds(),
            },
            "results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        report_file = (
            f"cicd_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 상세 리포트 저장됨: {report_file}")


def main():
    """메인 함수"""
    tester = CICDSystemTester()

    success = tester.run_all_tests()

    if success:
        print("\n🎉 CI/CD 시스템 테스트가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ CI/CD 시스템 테스트에 실패한 항목이 있습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
