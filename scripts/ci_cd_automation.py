#!/usr/bin/env python3
"""
CI/CD 자동화 시스템
- 릴리즈·테스트·배포 자동화
- 운영환경 분리, 배포 이력 대시보드 구축
- 자동화된 개발·운영 프로세스
- AI 기반 배포 최적화 및 실시간 모니터링
"""

import os
import sys
import json
import logging
import subprocess
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import git
from pathlib import Path
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import random

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/app/logs/ci_cd.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class Environment(Enum):
    """환경 유형"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStatus(Enum):
    """배포 상태"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class AIDeploymentOptimizer:
    """AI 기반 배포 최적화기"""

    def __init__(self):
        self.deployment_history = []
        self.performance_metrics = {}
        self.optimization_model = None
        self._load_deployment_data()

    def _load_deployment_data(self):
        """배포 이력 데이터 로드"""
        try:
            # 실제로는 데이터베이스에서 로드
            # 여기서는 샘플 데이터 생성
            self.deployment_history = [
                {
                    "timestamp": datetime.utcnow() - timedelta(hours=i),
                    "environment": "production",
                    "deployment_time": random.randint(60, 300),
                    "success_rate": random.uniform(0.8, 1.0),
                    "error_count": random.randint(0, 5),
                    "performance_impact": random.uniform(-0.1, 0.2),
                    "rollback_needed": random.choice([True, False]),
                }
                for i in range(100)
            ]
        except Exception as e:
            logger.error(f"배포 데이터 로드 오류: {e}")

    def predict_deployment_success(self, deployment_config: Dict) -> Dict:
        """배포 성공 확률 예측"""
        try:
            if len(self.deployment_history) < 10:
                return {"prediction": "insufficient_data", "confidence": 0}

            # 특성 추출
            features = self._extract_deployment_features(deployment_config)

            # 간단한 규칙 기반 예측 (실제로는 ML 모델 사용)
            risk_score = self._calculate_risk_score(features)
            success_probability = max(0, 1 - risk_score)

            # 신뢰도 계산
            confidence = self._calculate_prediction_confidence(features)

            return {
                "success_probability": success_probability,
                "risk_score": risk_score,
                "confidence": confidence,
                "recommendations": self._generate_deployment_recommendations(features),
            }

        except Exception as e:
            logger.error(f"배포 성공 예측 오류: {e}")
            return {"prediction": "error", "confidence": 0}

    def _extract_deployment_features(self, config: Dict) -> Dict:
        """배포 특성 추출"""
        return {
            "environment": config.get("environment", "production"),
            "deployment_time": config.get("estimated_time", 120),
            "changes_count": config.get("changes_count", 0),
            "database_migrations": config.get("database_migrations", False),
            "breaking_changes": config.get("breaking_changes", False),
            "time_of_day": datetime.utcnow().hour,
            "day_of_week": datetime.utcnow().weekday(),
        }

    def _calculate_risk_score(self, features: Dict) -> float:
        """위험도 점수 계산"""
        risk_score = 0.0

        # 환경별 위험도
        env_risk = {"development": 0.1, "staging": 0.3, "production": 0.8}
        risk_score += env_risk.get(features["environment"], 0.5)

        # 배포 시간 위험도
        if features["deployment_time"] > 300:  # 5분 초과
            risk_score += 0.2

        # 변경사항 위험도
        if features["changes_count"] > 50:
            risk_score += 0.1

        # 데이터베이스 마이그레이션 위험도
        if features["database_migrations"]:
            risk_score += 0.3

        # 호환성 변경 위험도
        if features["breaking_changes"]:
            risk_score += 0.4

        # 시간대 위험도 (업무 시간 외 배포 권장)
        if 9 <= features["time_of_day"] <= 18:
            risk_score += 0.1

        return min(1.0, risk_score)

    def _calculate_prediction_confidence(self, features: Dict) -> float:
        """예측 신뢰도 계산"""
        # 데이터 품질 및 특성 다양성 기반 신뢰도
        confidence = 0.7  # 기본 신뢰도

        # 데이터 양에 따른 조정
        if len(self.deployment_history) > 50:
            confidence += 0.2

        # 특성 다양성에 따른 조정
        if features["environment"] in ["development", "staging", "production"]:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_deployment_recommendations(self, features: Dict) -> List[str]:
        """배포 권고사항 생성"""
        recommendations = []

        if features["environment"] == "production":
            recommendations.append(
                "프로덕션 배포 전 스테이징 환경에서 충분한 테스트 수행"
            )

        if features["deployment_time"] > 300:
            recommendations.append(
                "배포 시간이 길어질 것으로 예상됩니다. 점진적 배포 고려"
            )

        if features["database_migrations"]:
            recommendations.append(
                "데이터베이스 마이그레이션이 포함되어 있습니다. 백업 필수"
            )

        if features["breaking_changes"]:
            recommendations.append(
                "호환성 변경사항이 포함되어 있습니다. 사용자 알림 필요"
            )

        if 9 <= features["time_of_day"] <= 18:
            recommendations.append(
                "업무 시간 중 배포입니다. 사용자 영향 최소화 방안 검토"
            )

        if not recommendations:
            recommendations.append("현재 배포 설정이 적절합니다.")

        return recommendations

    def optimize_deployment_schedule(self, deployments: List[Dict]) -> Dict:
        """배포 일정 최적화"""
        try:
            if not deployments:
                return {"error": "최적화할 배포가 없습니다."}

            # 배포 우선순위 계산
            prioritized_deployments = []
            for deployment in deployments:
                priority_score = self._calculate_deployment_priority(deployment)
                prioritized_deployments.append(
                    {**deployment, "priority_score": priority_score}
                )

            # 우선순위별 정렬
            prioritized_deployments.sort(
                key=lambda x: x["priority_score"], reverse=True
            )

            # 최적 일정 생성
            optimal_schedule = self._generate_optimal_schedule(prioritized_deployments)

            return {
                "optimal_schedule": optimal_schedule,
                "total_deployments": len(deployments),
                "estimated_total_time": sum(
                    d["estimated_time"] for d in optimal_schedule
                ),
            }

        except Exception as e:
            logger.error(f"배포 일정 최적화 오류: {e}")
            return {"error": str(e)}

    def _calculate_deployment_priority(self, deployment: Dict) -> float:
        """배포 우선순위 계산"""
        priority = 0.0

        # 환경별 우선순위
        env_priority = {"development": 1.0, "staging": 2.0, "production": 3.0}
        priority += env_priority.get(deployment.get("environment", "development"), 1.0)

        # 긴급도
        if deployment.get("urgent", False):
            priority += 2.0

        # 보안 패치
        if deployment.get("security_patch", False):
            priority += 1.5

        # 버그 수정
        if deployment.get("bug_fix", False):
            priority += 1.0

        return priority

    def _generate_optimal_schedule(
        self, prioritized_deployments: List[Dict]
    ) -> List[Dict]:
        """최적 일정 생성"""
        schedule = []
        current_time = datetime.utcnow()

        for deployment in prioritized_deployments:
            # 환경별 배포 간격 설정
            if deployment["environment"] == "production":
                # 프로덕션 배포는 업무 시간 외에 배치
                if 9 <= current_time.hour <= 18:
                    current_time = current_time.replace(
                        hour=22, minute=0, second=0, microsecond=0
                    )
                    if current_time < datetime.utcnow():
                        current_time += timedelta(days=1)

            scheduled_deployment = {
                **deployment,
                "scheduled_time": current_time.isoformat(),
                "estimated_duration": deployment.get("estimated_time", 120),
            }

            schedule.append(scheduled_deployment)

            # 다음 배포 시간 계산
            current_time += timedelta(
                minutes=deployment.get("estimated_time", 120) + 30
            )

        return schedule


class RealTimeDeploymentMonitor:
    """실시간 배포 모니터링"""

    def __init__(self):
        self.monitoring_config = {}
        self.alert_thresholds = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        self._setup_monitoring()

    def _setup_monitoring(self):
        """모니터링 설정"""
        self.monitoring_config = {
            "check_interval": 30,  # 30초마다 체크
            "health_check_timeout": 10,
            "max_retries": 3,
        }

        self.alert_thresholds = {
            "response_time": 2000,  # 2초
            "error_rate": 0.05,  # 5%
            "cpu_usage": 0.8,  # 80%
            "memory_usage": 0.85,  # 85%
        }

    def start_monitoring(self, environment: str):
        """모니터링 시작"""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, args=(environment,), daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"{environment} 환경 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("모니터링 중지")

    def _monitoring_loop(self, environment: str):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 환경 상태 체크
                health_status = self._check_environment_health(environment)

                # 임계값 체크 및 알림
                if health_status["status"] != "healthy":
                    self._send_deployment_alert(environment, health_status)

                # 대기
                time.sleep(self.monitoring_config["check_interval"])

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(self.monitoring_config["check_interval"])

    def _check_environment_health(self, environment: str) -> Dict:
        """환경 건강 상태 체크"""
        try:
            # 실제로는 환경별 엔드포인트 호출
            # 여기서는 샘플 데이터 반환
            health_data = {
                "response_time": random.randint(100, 3000),
                "error_rate": random.uniform(0, 0.1),
                "cpu_usage": random.uniform(0.3, 0.9),
                "memory_usage": random.uniform(0.4, 0.95),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # 상태 판단
            status = "healthy"
            alerts = []

            if health_data["response_time"] > self.alert_thresholds["response_time"]:
                status = "warning"
                alerts.append("응답 시간이 임계값을 초과했습니다.")

            if health_data["error_rate"] > self.alert_thresholds["error_rate"]:
                status = "critical"
                alerts.append("오류율이 임계값을 초과했습니다.")

            if health_data["cpu_usage"] > self.alert_thresholds["cpu_usage"]:
                status = "warning"
                alerts.append("CPU 사용률이 높습니다.")

            if health_data["memory_usage"] > self.alert_thresholds["memory_usage"]:
                status = "warning"
                alerts.append("메모리 사용률이 높습니다.")

            return {
                "environment": environment,
                "status": status,
                "health_data": health_data,
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"환경 건강 상태 체크 오류: {e}")
            return {"environment": environment, "status": "unknown", "error": str(e)}

    def _send_deployment_alert(self, environment: str, health_status: Dict):
        """배포 알림 발송"""
        try:
            # 실제로는 알림 시스템과 연동
            alert_message = (
                f"배포 모니터링 알림 - {environment} 환경: {health_status['status']}"
            )

            if health_status.get("alerts"):
                alert_message += f" - {'; '.join(health_status['alerts'])}"

            logger.warning(alert_message)

            # 여기서는 로그로만 처리, 실제로는 Notification 모델 사용
            # notification = Notification()
            # notification.title = f"배포 모니터링 알림 - {environment}"
            # notification.content = alert_message
            # notification.category = "DEPLOYMENT_ALERT"
            # notification.priority = "중요"
            # db.session.add(notification)
            # db.session.commit()

        except Exception as e:
            logger.error(f"배포 알림 발송 오류: {e}")


class CICDAutomation:
    """CI/CD 자동화 관리자"""

    def __init__(self):
        self.config = self._load_config()
        self.deployment_history = []
        self.current_deployment = None
        self.environments = {}
        self.ai_optimizer = AIDeploymentOptimizer()
        self.monitor = RealTimeDeploymentMonitor()

        # 환경별 설정
        self._setup_environments()

    def _load_config(self) -> Dict:
        """설정 파일 로드"""
        config_path = Path("/app/config/ci_cd_config.json")

        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            # 기본 설정
            return {
                "repository": {
                    "url": "https://github.com/your-org/your-program.git",
                    "branch": "main",
                    "credentials": {
                        "username": os.getenv("GIT_USERNAME"),
                        "token": os.getenv("GIT_TOKEN"),
                    },
                },
                "environments": {
                    "development": {
                        "url": "http://localhost:5000",
                        "database": "your_program_dev",
                        "auto_deploy": True,
                    },
                    "staging": {
                        "url": "https://staging.your-program.com",
                        "database": "your_program_staging",
                        "auto_deploy": False,
                    },
                    "production": {
                        "url": "https://your-program.com",
                        "database": "your_program_prod",
                        "auto_deploy": False,
                    },
                },
                "testing": {
                    "unit_tests": True,
                    "integration_tests": True,
                    "e2e_tests": False,
                    "coverage_threshold": 80,
                },
                "deployment": {
                    "timeout": 300,  # 5분
                    "health_check_interval": 30,
                    "rollback_enabled": True,
                    "backup_before_deploy": True,
                    "ai_optimization_enabled": True,
                    "real_time_monitoring": True,
                },
            }

    def _setup_environments(self):
        """환경별 설정"""
        self.environments = self.config["environments"]

    def trigger_ci_pipeline(self, branch: str = None, commit_hash: str = None) -> Dict:
        """CI 파이프라인 트리거"""
        try:
            logger.info(f"CI 파이프라인 시작: 브랜치={branch}, 커밋={commit_hash}")

            # 1. 코드 체크아웃
            checkout_result = self._checkout_code(branch, commit_hash)
            if not checkout_result["success"]:
                return checkout_result

            # 2. 의존성 설치
            install_result = self._install_dependencies()
            if not install_result["success"]:
                return install_result

            # 3. 코드 품질 검사
            quality_result = self._run_code_quality_checks()
            if not quality_result["success"]:
                return quality_result

            # 4. 단위 테스트
            unit_test_result = self._run_unit_tests()
            if not unit_test_result["success"]:
                return unit_test_result

            # 5. 통합 테스트
            integration_test_result = self._run_integration_tests()
            if not integration_test_result["success"]:
                return integration_test_result

            # 6. 빌드
            build_result = self._build_application()
            if not build_result["success"]:
                return build_result

            # 7. 아티팩트 생성
            artifact_result = self._create_artifacts()
            if not artifact_result["success"]:
                return artifact_result

            logger.info("CI 파이프라인 완료")

            return {
                "success": True,
                "message": "CI 파이프라인이 성공적으로 완료되었습니다.",
                "pipeline_id": f"ci_{int(time.time())}",
                "results": {
                    "checkout": checkout_result,
                    "install": install_result,
                    "quality": quality_result,
                    "unit_tests": unit_test_result,
                    "integration_tests": integration_test_result,
                    "build": build_result,
                    "artifacts": artifact_result,
                },
            }

        except Exception as e:
            logger.error(f"CI 파이프라인 오류: {e}")
            return {"success": False, "error": str(e)}

    def _checkout_code(self, branch: str = None, commit_hash: str = None) -> Dict:
        """코드 체크아웃"""
        try:
            repo_config = self.config["repository"]
            repo_path = Path("/app/source")

            if repo_path.exists():
                # 기존 저장소 업데이트
                repo = git.Repo(repo_path)
                repo.remotes.origin.fetch()

                if branch:
                    repo.git.checkout(branch)
                if commit_hash:
                    repo.git.checkout(commit_hash)
            else:
                # 새 저장소 클론
                repo_path.mkdir(parents=True, exist_ok=True)
                repo = git.Repo.clone_from(
                    repo_config["url"],
                    repo_path,
                    branch=branch or repo_config["branch"],
                )

                if commit_hash:
                    repo.git.checkout(commit_hash)

            return {
                "success": True,
                "message": "코드 체크아웃 완료",
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha,
            }

        except Exception as e:
            logger.error(f"코드 체크아웃 오류: {e}")
            return {"success": False, "error": str(e)}

    def _install_dependencies(self) -> Dict:
        """의존성 설치"""
        try:
            repo_path = Path("/app/source")
            requirements_file = repo_path / "requirements.txt"

            if requirements_file.exists():
                result = subprocess.run(
                    ["pip", "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                )

                if result.returncode == 0:
                    return {"success": True, "message": "의존성 설치 완료"}
                else:
                    return {
                        "success": False,
                        "error": f"의존성 설치 실패: {result.stderr}",
                    }
            else:
                return {"success": True, "message": "requirements.txt 파일이 없습니다."}

        except Exception as e:
            logger.error(f"의존성 설치 오류: {e}")
            return {"success": False, "error": str(e)}

    def _run_code_quality_checks(self) -> Dict:
        """코드 품질 검사"""
        try:
            repo_path = Path("/app/source")

            # flake8 검사
            flake8_result = subprocess.run(
                ["flake8", "."], capture_output=True, text=True, cwd=repo_path
            )

            # pylint 검사
            pylint_result = subprocess.run(
                ["pylint", "--rcfile=/app/config/pylintrc", "."],
                capture_output=True,
                text=True,
                cwd=repo_path,
            )

            # 검사 결과 분석
            flake8_issues = (
                len(flake8_result.stdout.splitlines()) if flake8_result.stdout else 0
            )
            pylint_score = self._extract_pylint_score(pylint_result.stdout)

            if flake8_issues == 0 and pylint_score >= 8.0:
                return {
                    "success": True,
                    "message": "코드 품질 검사 통과",
                    "flake8_issues": flake8_issues,
                    "pylint_score": pylint_score,
                }
            else:
                return {
                    "success": False,
                    "error": f"코드 품질 검사 실패: flake8 이슈 {flake8_issues}개, pylint 점수 {pylint_score}",
                    "flake8_issues": flake8_issues,
                    "pylint_score": pylint_score,
                }

        except Exception as e:
            logger.error(f"코드 품질 검사 오류: {e}")
            return {"success": False, "error": str(e)}

    def _extract_pylint_score(self, output: str) -> float:
        """pylint 점수 추출"""
        try:
            for line in output.splitlines():
                if "Your code has been rated at" in line:
                    score_str = line.split("at")[1].split("/")[0].strip()
                    return float(score_str)
            return 0.0
        except:
            return 0.0

    def _run_unit_tests(self) -> Dict:
        """단위 테스트 실행"""
        try:
            repo_path = Path("/app/source")
            tests_dir = repo_path / "tests"

            if not tests_dir.exists():
                return {"success": True, "message": "테스트 디렉토리가 없습니다."}

            # pytest 실행
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "--cov=app", "--cov-report=json"],
                capture_output=True,
                text=True,
                cwd=repo_path,
            )

            if result.returncode == 0:
                # 커버리지 분석
                coverage_data = self._analyze_coverage(repo_path / "coverage.json")

                return {
                    "success": True,
                    "message": "단위 테스트 통과",
                    "coverage": coverage_data,
                }
            else:
                return {"success": False, "error": f"단위 테스트 실패: {result.stderr}"}

        except Exception as e:
            logger.error(f"단위 테스트 오류: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_coverage(self, coverage_file: Path) -> Dict:
        """커버리지 분석"""
        try:
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get(
                    "percent_covered", 0
                )

                return {
                    "total_coverage": total_coverage,
                    "threshold_met": total_coverage
                    >= self.config["testing"]["coverage_threshold"],
                }
            else:
                return {"total_coverage": 0, "threshold_met": False}

        except Exception as e:
            logger.error(f"커버리지 분석 오류: {e}")
            return {"total_coverage": 0, "threshold_met": False}

    def _run_integration_tests(self) -> Dict:
        """통합 테스트 실행"""
        try:
            if not self.config["testing"]["integration_tests"]:
                return {
                    "success": True,
                    "message": "통합 테스트가 비활성화되어 있습니다.",
                }

            repo_path = Path("/app/source")
            integration_tests_dir = repo_path / "tests" / "integration"

            if not integration_tests_dir.exists():
                return {"success": True, "message": "통합 테스트 디렉토리가 없습니다."}

            # 통합 테스트 실행
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/integration/"],
                capture_output=True,
                text=True,
                cwd=repo_path,
            )

            if result.returncode == 0:
                return {"success": True, "message": "통합 테스트 통과"}
            else:
                return {"success": False, "error": f"통합 테스트 실패: {result.stderr}"}

        except Exception as e:
            logger.error(f"통합 테스트 오류: {e}")
            return {"success": False, "error": str(e)}

    def _build_application(self) -> Dict:
        """애플리케이션 빌드"""
        try:
            repo_path = Path("/app/source")

            # Docker 이미지 빌드
            dockerfile_path = repo_path / "Dockerfile"

            if dockerfile_path.exists():
                image_name = "your-program"
                tag = f"{image_name}:{int(time.time())}"

                result = subprocess.run(
                    ["docker", "build", "-t", tag, "."],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                )

                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Docker 이미지 빌드 완료",
                        "image_tag": tag,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Docker 빌드 실패: {result.stderr}",
                    }
            else:
                return {
                    "success": True,
                    "message": "Dockerfile이 없습니다. 빌드 단계를 건너뜁니다.",
                }

        except Exception as e:
            logger.error(f"애플리케이션 빌드 오류: {e}")
            return {"success": False, "error": str(e)}

    def _create_artifacts(self) -> Dict:
        """아티팩트 생성"""
        try:
            artifacts_dir = Path("/app/artifacts")
            artifacts_dir.mkdir(exist_ok=True)

            # 배포 패키지 생성
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            artifact_name = f"deployment_{timestamp}.tar.gz"
            artifact_path = artifacts_dir / artifact_name

            # 소스 코드 패키징
            repo_path = Path("/app/source")
            result = subprocess.run(
                ["tar", "-czf", str(artifact_path), "."],
                capture_output=True,
                text=True,
                cwd=repo_path,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "아티팩트 생성 완료",
                    "artifact_path": str(artifact_path),
                    "artifact_name": artifact_name,
                }
            else:
                return {
                    "success": False,
                    "error": f"아티팩트 생성 실패: {result.stderr}",
                }

        except Exception as e:
            logger.error(f"아티팩트 생성 오류: {e}")
            return {"success": False, "error": str(e)}

    def deploy_to_environment(
        self, environment: str, artifact_path: str = None
    ) -> Dict:
        """환경별 배포"""
        try:
            if environment not in self.environments:
                return {"success": False, "error": f"지원하지 않는 환경: {environment}"}

            env_config = self.environments[environment]

            # 배포 시작
            deployment_id = f"deploy_{environment}_{int(time.time())}"
            self.current_deployment = {
                "id": deployment_id,
                "environment": environment,
                "status": DeploymentStatus.IN_PROGRESS.value,
                "started_at": datetime.utcnow().isoformat(),
                "artifact_path": artifact_path,
            }

            logger.info(f"배포 시작: {deployment_id} -> {environment}")

            # 1. 배포 전 백업 (필요한 경우)
            if self.config["deployment"]["backup_before_deploy"]:
                backup_result = self._backup_environment(environment)
                if not backup_result["success"]:
                    return backup_result

            # 2. 배포 실행
            deploy_result = self._execute_deployment(environment, artifact_path)
            if not deploy_result["success"]:
                self._update_deployment_status(
                    DeploymentStatus.FAILED.value, deploy_result["error"]
                )
                return deploy_result

            # 3. 헬스 체크
            health_result = self._health_check_environment(environment)
            if not health_result["success"]:
                # 롤백 실행
                if self.config["deployment"]["rollback_enabled"]:
                    rollback_result = self._rollback_deployment(environment)
                    self._update_deployment_status(
                        DeploymentStatus.ROLLBACK.value,
                        rollback_result.get("message", ""),
                    )
                    return rollback_result
                else:
                    self._update_deployment_status(
                        DeploymentStatus.FAILED.value, "헬스 체크 실패"
                    )
                    return health_result

            # 배포 성공
            self._update_deployment_status(DeploymentStatus.SUCCESS.value, "배포 완료")

            return {
                "success": True,
                "message": f"{environment} 환경 배포 완료",
                "deployment_id": deployment_id,
                "environment": environment,
            }

        except Exception as e:
            logger.error(f"배포 오류 ({environment}): {e}")
            self._update_deployment_status(DeploymentStatus.FAILED.value, str(e))
            return {"success": False, "error": str(e)}

    def _backup_environment(self, environment: str) -> Dict:
        """환경 백업"""
        try:
            logger.info(f"{environment} 환경 백업 시작")

            # 데이터베이스 백업
            db_backup_result = self._backup_database(environment)

            # 파일 백업
            file_backup_result = self._backup_files(environment)

            return {
                "success": True,
                "message": f"{environment} 환경 백업 완료",
                "database_backup": db_backup_result,
                "file_backup": file_backup_result,
            }

        except Exception as e:
            logger.error(f"환경 백업 오류: {e}")
            return {"success": False, "error": str(e)}

    def _backup_database(self, environment: str) -> Dict:
        """데이터베이스 백업"""
        try:
            env_config = self.environments[environment]
            db_name = env_config["database"]

            backup_dir = Path(f"/app/backups/{environment}")
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"db_backup_{timestamp}.sql"

            # PostgreSQL 백업
            result = subprocess.run(
                [
                    "pg_dump",
                    "-h",
                    "localhost",
                    "-U",
                    "your_program",
                    "-d",
                    db_name,
                    "-f",
                    str(backup_file),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {"success": True, "backup_file": str(backup_file)}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"데이터베이스 백업 오류: {e}")
            return {"success": False, "error": str(e)}

    def _backup_files(self, environment: str) -> Dict:
        """파일 백업"""
        try:
            backup_dir = Path(f"/app/backups/{environment}")
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"files_backup_{timestamp}.tar.gz"

            # 애플리케이션 파일 백업
            app_dir = Path(f"/app/{environment}")
            if app_dir.exists():
                result = subprocess.run(
                    ["tar", "-czf", str(backup_file), str(app_dir)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return {"success": True, "backup_file": str(backup_file)}
                else:
                    return {"success": False, "error": result.stderr}
            else:
                return {"success": True, "message": "백업할 파일이 없습니다."}

        except Exception as e:
            logger.error(f"파일 백업 오류: {e}")
            return {"success": False, "error": str(e)}

    def _execute_deployment(self, environment: str, artifact_path: str = None) -> Dict:
        """배포 실행"""
        try:
            env_config = self.environments[environment]

            if artifact_path and Path(artifact_path).exists():
                # 아티팩트에서 배포
                return self._deploy_from_artifact(environment, artifact_path)
            else:
                # 직접 배포
                return self._deploy_direct(environment)

        except Exception as e:
            logger.error(f"배포 실행 오류: {e}")
            return {"success": False, "error": str(e)}

    def _deploy_from_artifact(self, environment: str, artifact_path: str) -> Dict:
        """아티팩트에서 배포"""
        try:
            # 아티팩트 압축 해제
            deploy_dir = Path(f"/app/{environment}")
            deploy_dir.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                ["tar", "-xzf", artifact_path, "-C", str(deploy_dir)],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"아티팩트 압축 해제 실패: {result.stderr}",
                }

            # 애플리케이션 재시작
            restart_result = self._restart_application(environment)

            return restart_result

        except Exception as e:
            logger.error(f"아티팩트 배포 오류: {e}")
            return {"success": False, "error": str(e)}

    def _deploy_direct(self, environment: str) -> Dict:
        """직접 배포"""
        try:
            # Docker Compose 배포
            compose_file = Path(f"/app/docker-compose.{environment}.yml")

            if compose_file.exists():
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d", "--build"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return {"success": True, "message": f"{environment} 환경 배포 완료"}
                else:
                    return {
                        "success": False,
                        "error": f"Docker Compose 배포 실패: {result.stderr}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Docker Compose 파일을 찾을 수 없습니다: {compose_file}",
                }

        except Exception as e:
            logger.error(f"직접 배포 오류: {e}")
            return {"success": False, "error": str(e)}

    def _restart_application(self, environment: str) -> Dict:
        """애플리케이션 재시작"""
        try:
            # 환경별 재시작 명령
            if environment == "development":
                # 개발 환경은 Flask 개발 서버 재시작
                return {"success": True, "message": "개발 환경 재시작 완료"}
            elif environment == "staging":
                # 스테이징 환경은 Docker 컨테이너 재시작
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-f",
                        "/app/docker-compose.staging.yml",
                        "restart",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return {"success": True, "message": "스테이징 환경 재시작 완료"}
                else:
                    return {
                        "success": False,
                        "error": f"스테이징 환경 재시작 실패: {result.stderr}",
                    }
            elif environment == "production":
                # 프로덕션 환경은 Kubernetes 배포 업데이트
                result = subprocess.run(
                    ["kubectl", "rollout", "restart", "deployment/your-program"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return {"success": True, "message": "프로덕션 환경 재시작 완료"}
                else:
                    return {
                        "success": False,
                        "error": f"프로덕션 환경 재시작 실패: {result.stderr}",
                    }

            return {"success": True, "message": f"{environment} 환경 재시작 완료"}

        except Exception as e:
            logger.error(f"애플리케이션 재시작 오류: {e}")
            return {"success": False, "error": str(e)}

    def _health_check_environment(self, environment: str) -> Dict:
        """환경 헬스 체크"""
        try:
            env_config = self.environments[environment]
            url = env_config["url"]

            # 헬스 체크 엔드포인트 호출
            health_url = f"{url}/api/health"

            timeout = self.config["deployment"]["timeout"]
            interval = self.config["deployment"]["health_check_interval"]
            max_attempts = timeout // interval

            for attempt in range(max_attempts):
                try:
                    response = requests.get(health_url, timeout=10)
                    if response.status_code == 200:
                        return {
                            "success": True,
                            "message": f"{environment} 환경 헬스 체크 통과",
                        }
                except requests.RequestException:
                    pass

                time.sleep(interval)

            return {
                "success": False,
                "error": f"{environment} 환경 헬스 체크 실패 (타임아웃)",
            }

        except Exception as e:
            logger.error(f"헬스 체크 오류: {e}")
            return {"success": False, "error": str(e)}

    def _rollback_deployment(self, environment: str) -> Dict:
        """배포 롤백"""
        try:
            logger.info(f"{environment} 환경 롤백 시작")

            # 최근 백업에서 복구
            backup_result = self._restore_latest_backup(environment)

            if backup_result["success"]:
                # 애플리케이션 재시작
                restart_result = self._restart_application(environment)

                if restart_result["success"]:
                    return {"success": True, "message": f"{environment} 환경 롤백 완료"}
                else:
                    return restart_result
            else:
                return backup_result

        except Exception as e:
            logger.error(f"롤백 오류: {e}")
            return {"success": False, "error": str(e)}

    def _restore_latest_backup(self, environment: str) -> Dict:
        """최근 백업 복구"""
        try:
            backup_dir = Path(f"/app/backups/{environment}")

            if not backup_dir.exists():
                return {"success": False, "error": "백업 디렉토리가 없습니다."}

            # 최근 백업 파일 찾기
            backup_files = list(backup_dir.glob("*.sql"))
            if not backup_files:
                return {"success": False, "error": "복구할 백업 파일이 없습니다."}

            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)

            # 데이터베이스 복구
            env_config = self.environments[environment]
            db_name = env_config["database"]

            result = subprocess.run(
                [
                    "psql",
                    "-h",
                    "localhost",
                    "-U",
                    "your_program",
                    "-d",
                    db_name,
                    "-f",
                    str(latest_backup),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"백업 복구 완료: {latest_backup.name}",
                }
            else:
                return {"success": False, "error": f"백업 복구 실패: {result.stderr}"}

        except Exception as e:
            logger.error(f"백업 복구 오류: {e}")
            return {"success": False, "error": str(e)}

    def _update_deployment_status(self, status: str, message: str = ""):
        """배포 상태 업데이트"""
        if self.current_deployment:
            self.current_deployment["status"] = status
            self.current_deployment["completed_at"] = datetime.utcnow().isoformat()
            self.current_deployment["message"] = message

            # 배포 이력에 추가
            self.deployment_history.append(self.current_deployment.copy())

            # 최근 100개만 유지
            if len(self.deployment_history) > 100:
                self.deployment_history = self.deployment_history[-100:]

    def get_deployment_history(
        self, environment: str = None, limit: int = 20
    ) -> List[Dict]:
        """배포 이력 조회"""
        try:
            history = self.deployment_history

            if environment:
                history = [
                    deploy for deploy in history if deploy["environment"] == environment
                ]

            # 최근 순으로 정렬
            history.sort(key=lambda x: x["started_at"], reverse=True)

            return history[:limit]

        except Exception as e:
            logger.error(f"배포 이력 조회 오류: {e}")
            return []

    def get_deployment_dashboard(self) -> Dict:
        """배포 대시보드 데이터"""
        try:
            # 환경별 최근 배포 상태
            environment_status = {}
            for env_name in self.environments.keys():
                recent_deployments = self.get_deployment_history(env_name, 1)
                if recent_deployments:
                    environment_status[env_name] = recent_deployments[0]
                else:
                    environment_status[env_name] = {
                        "status": "unknown",
                        "message": "배포 이력이 없습니다.",
                    }

            # 전체 통계
            total_deployments = len(self.deployment_history)
            successful_deployments = len(
                [
                    d
                    for d in self.deployment_history
                    if d["status"] == DeploymentStatus.SUCCESS.value
                ]
            )
            failed_deployments = len(
                [
                    d
                    for d in self.deployment_history
                    if d["status"] == DeploymentStatus.FAILED.value
                ]
            )

            return {
                "environment_status": environment_status,
                "statistics": {
                    "total_deployments": total_deployments,
                    "successful_deployments": successful_deployments,
                    "failed_deployments": failed_deployments,
                    "success_rate": (
                        (successful_deployments / total_deployments * 100)
                        if total_deployments > 0
                        else 0
                    ),
                },
                "recent_deployments": self.get_deployment_history(limit=10),
            }

        except Exception as e:
            logger.error(f"배포 대시보드 조회 오류: {e}")
            return {"error": str(e)}

    def deploy_with_ai_optimization(
        self, environment: str, deployment_config: Dict
    ) -> Dict:
        """AI 최적화 배포"""
        try:
            logger.info(f"AI 최적화 배포 시작: {environment}")

            # AI 예측 수행
            if self.config["deployment"].get("ai_optimization_enabled", False):
                prediction = self.ai_optimizer.predict_deployment_success(
                    deployment_config
                )

                if prediction.get("success_probability", 0) < 0.7:
                    logger.warning(
                        f"배포 성공 확률이 낮습니다: {prediction['success_probability']:.2f}"
                    )

                    # 권고사항 표시
                    for recommendation in prediction.get("recommendations", []):
                        logger.info(f"권고사항: {recommendation}")

                    # 사용자 확인 필요
                    if not deployment_config.get("force_deploy", False):
                        return {
                            "success": False,
                            "error": "배포 성공 확률이 낮습니다. force_deploy=true로 강제 배포하거나 권고사항을 검토하세요.",
                            "prediction": prediction,
                        }

            # 실제 배포 수행
            deployment_result = self.deploy_to_environment(
                environment, deployment_config.get("artifact_path")
            )

            # 실시간 모니터링 시작
            if self.config["deployment"].get("real_time_monitoring", False):
                self.monitor.start_monitoring(environment)

            # AI 예측 결과를 배포 결과에 추가
            if "prediction" in locals():
                deployment_result["ai_prediction"] = prediction

            return deployment_result

        except Exception as e:
            logger.error(f"AI 최적화 배포 오류: {e}")
            return {"success": False, "error": str(e)}

    def optimize_deployment_queue(self, deployments: List[Dict]) -> Dict:
        """배포 큐 최적화"""
        try:
            if not deployments:
                return {"error": "최적화할 배포가 없습니다."}

            # AI 기반 일정 최적화
            optimization_result = self.ai_optimizer.optimize_deployment_schedule(
                deployments
            )

            if "error" in optimization_result:
                return optimization_result

            logger.info(f"배포 일정 최적화 완료: {len(deployments)}개 배포")

            return {
                "success": True,
                "optimized_schedule": optimization_result["optimal_schedule"],
                "total_time_saved": self._calculate_time_savings(
                    deployments, optimization_result["optimal_schedule"]
                ),
            }

        except Exception as e:
            logger.error(f"배포 큐 최적화 오류: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_time_savings(
        self, original_deployments: List[Dict], optimized_schedule: List[Dict]
    ) -> int:
        """시간 절약 계산"""
        try:
            original_total = sum(
                d.get("estimated_time", 0) for d in original_deployments
            )
            optimized_total = sum(
                d.get("estimated_duration", 0) for d in optimized_schedule
            )

            return max(0, original_total - optimized_total)

        except Exception as e:
            logger.error(f"시간 절약 계산 오류: {e}")
            return 0


# 전역 CI/CD 자동화 인스턴스
ci_cd_manager = CICDAutomation()


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python ci_cd_automation.py <command> [options]")
        print("명령어:")
        print("  ci <branch> [commit] - CI 파이프라인 실행")
        print("  deploy <environment> [artifact] - 환경 배포")
        print("  history [environment] - 배포 이력 조회")
        print("  dashboard - 배포 대시보드 조회")
        return

    command = sys.argv[1]

    if command == "ci":
        branch = sys.argv[2] if len(sys.argv) > 2 else None
        commit = sys.argv[3] if len(sys.argv) > 3 else None

        result = ci_cd_manager.trigger_ci_pipeline(branch, commit)
        print(json.dumps(result, indent=2))

    elif command == "deploy":
        if len(sys.argv) < 3:
            print("환경을 지정해주세요.")
            return

        environment = sys.argv[2]
        artifact = sys.argv[3] if len(sys.argv) > 3 else None

        result = ci_cd_manager.deploy_to_environment(environment, artifact)
        print(json.dumps(result, indent=2))

    elif command == "history":
        environment = sys.argv[2] if len(sys.argv) > 2 else None

        history = ci_cd_manager.get_deployment_history(environment)
        print(json.dumps(history, indent=2))

    elif command == "dashboard":
        dashboard = ci_cd_manager.get_deployment_dashboard()
        print(json.dumps(dashboard, indent=2))

    else:
        print(f"알 수 없는 명령어: {command}")


if __name__ == "__main__":
    main()
