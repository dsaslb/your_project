#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스테이징 환경 배포 스크립트
플러그인 시스템을 스테이징 환경에 자동으로 배포합니다.
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
import paramiko
import docker
from fabric import Connection

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StagingDeployer:
    def __init__(self, config_file: str = "deploy_config.yaml"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.deployment_log = []

    def load_config(self) -> Dict[str, Any]:
        """배포 설정 로드"""
        if not self.config_file.exists():
            logger.error(f"배포 설정 파일이 없습니다: {self.config_file}")
            sys.exit(1)

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 필수 설정 검증
            required_keys = ["staging", "database", "plugins", "monitoring"]
            if not isinstance(config, dict):  # pyright: ignore
                logger.error(
                    "설정 파일이 올바른 딕셔너리 형식이 아닙니다."
                )  # pyright: ignore
                sys.exit(1)
            for key in required_keys:
                if key not in config:  # pyright: ignore
                    logger.error(f"필수 설정이 없습니다: {key}")
                    sys.exit(1)

            return config  # pyright: ignore
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            sys.exit(1)

    def log_deployment(self, step: str, status: str, message: str = ""):
        """배포 로그 기록"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,
            "message": message,
        }
        self.deployment_log.append(log_entry)
        logger.info(f"[{step}] {status}: {message}")

    def check_prerequisites(self) -> bool:
        """배포 전제 조건 확인"""
        logger.info("배포 전제 조건 확인 중...")

        # 1. Git 상태 확인
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                self.log_deployment(
                    "prerequisites",
                    "warning",
                    "작업 디렉토리에 커밋되지 않은 변경사항이 있습니다",
                )
            else:
                self.log_deployment("prerequisites", "success", "Git 상태 정상")
        except subprocess.CalledProcessError as e:
            self.log_deployment("prerequisites", "error", f"Git 상태 확인 실패: {e}")
            return False

        # 2. Docker 확인
        try:
            docker_client = docker.from_env()
            docker_client.ping()
            self.log_deployment("prerequisites", "success", "Docker 연결 정상")
        except Exception as e:
            self.log_deployment("prerequisites", "error", f"Docker 연결 실패: {e}")
            return False

        # 3. 환경 변수 확인
        required_env_vars = [
            "STAGING_HOST",
            "STAGING_USER",
            "STAGING_SSH_KEY",
            "DATABASE_URL",
            "SECRET_KEY",
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log_deployment(
                "prerequisites",
                "error",
                f"필수 환경 변수 없음: {', '.join(missing_vars)}",
            )
            return False
        else:
            self.log_deployment("prerequisites", "success", "환경 변수 설정 완료")

        return True

    def backup_current_deployment(self) -> bool:
        """현재 배포 백업"""
        logger.info("현재 배포 백업 중...")

        try:
            # 백업 디렉토리 생성
            backup_dir = (
                Path("backups") / f"staging_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            backup_dir.mkdir(parents=True, exist_ok=True)

            # 현재 코드 백업
            subprocess.run(
                [
                    "git",
                    "archive",
                    "--format=tar",
                    "--output",
                    str(backup_dir / "code.tar"),
                    "HEAD",
                ],
                check=True,
            )

            # 설정 파일 백업
            config_backup = backup_dir / "config"
            config_backup.mkdir()

            config_files = ["config.py", "alembic.ini", "requirements.txt"]
            for config_file in config_files:
                if Path(config_file).exists():
                    subprocess.run(
                        ["cp", config_file, str(config_backup / config_file)],
                        check=True,
                    )

            # 데이터베이스 백업 (원격)
            self.backup_remote_database(backup_dir)

            self.log_deployment("backup", "success", f"백업 완료: {backup_dir}")
            return True

        except Exception as e:
            self.log_deployment("backup", "error", f"백업 실패: {e}")
            return False

    def backup_remote_database(self, backup_dir: Path):
        """원격 데이터베이스 백업"""
        try:
            host = os.getenv("STAGING_HOST")
            user = os.getenv("STAGING_USER")
            ssh_key = os.getenv("STAGING_SSH_KEY")

            with Connection(
                host=host, user=user, connect_kwargs={"key_filename": ssh_key}
            ) as conn:
                # PostgreSQL 백업
                if self.config["database"]["type"] == "postgresql":
                    backup_file = (
                        f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                    )
                    conn.run(
                        f"pg_dump {self.config['database']['name']} > /tmp/{backup_file}"
                    )
                    conn.get(f"/tmp/{backup_file}", str(backup_dir / backup_file))
                    conn.run(f"rm /tmp/{backup_file}")

                # SQLite 백업
                elif self.config["database"]["type"] == "sqlite":
                    db_path = self.config["database"]["path"]
                    backup_file = (
                        f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    )
                    conn.run(f"cp {db_path} /tmp/{backup_file}")
                    conn.get(f"/tmp/{backup_file}", str(backup_dir / backup_file))
                    conn.run(f"rm /tmp/{backup_file}")

        except Exception as e:
            logger.warning(f"데이터베이스 백업 실패: {e}")

    def build_docker_image(self) -> bool:
        """Docker 이미지 빌드"""
        logger.info("Docker 이미지 빌드 중...")

        try:
            # Dockerfile 확인
            dockerfile = Path("Dockerfile")
            if not dockerfile.exists():
                self.log_deployment("docker_build", "error", "Dockerfile이 없습니다")
                return False

            # 이미지 태그 생성
            image_tag = (
                f"plugin-system:staging-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )

            # Docker 빌드
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    image_tag,
                    "--build-arg",
                    f"ENVIRONMENT=staging",
                    "--build-arg",
                    f"BUILD_DATE={datetime.now().isoformat()}",
                    ".",
                ],
                check=True,
            )

            self.log_deployment(
                "docker_build", "success", f"이미지 빌드 완료: {image_tag}"
            )
            return True

        except subprocess.CalledProcessError as e:
            self.log_deployment("docker_build", "error", f"Docker 빌드 실패: {e}")
            return False

    def deploy_to_staging(self) -> bool:
        """스테이징 서버 배포"""
        logger.info("스테이징 서버 배포 중...")

        try:
            host = os.getenv("STAGING_HOST")
            user = os.getenv("STAGING_USER")
            ssh_key = os.getenv("STAGING_SSH_KEY")

            with Connection(
                host=host, user=user, connect_kwargs={"key_filename": ssh_key}
            ) as conn:
                # 1. 배포 디렉토리 준비
                deploy_dir = "/opt/plugin-system"
                conn.run(f"mkdir -p {deploy_dir}")

                # 2. 현재 애플리케이션 중지
                conn.run("sudo systemctl stop plugin-system || true")
                conn.run("docker stop plugin-system || true")
                conn.run("docker rm plugin-system || true")

                # 3. 코드 배포
                self.deploy_code(conn, deploy_dir)

                # 4. 환경 설정 배포
                self.deploy_environment(conn, deploy_dir)

                # 5. 데이터베이스 마이그레이션
                self.run_database_migration(conn, deploy_dir)

                # 6. 애플리케이션 시작
                self.start_application(conn, deploy_dir)

                # 7. 헬스 체크
                if not self.health_check(conn):
                    raise Exception("헬스 체크 실패")

                self.log_deployment("staging_deploy", "success", "스테이징 배포 완료")
                return True

        except Exception as e:
            self.log_deployment("staging_deploy", "error", f"스테이징 배포 실패: {e}")
            return False

    def deploy_code(self, conn: Connection, deploy_dir: str):
        """코드 배포"""
        # Git 아카이브 생성
        subprocess.run(
            ["git", "archive", "--format=tar", "--output", "deploy.tar", "HEAD"],
            check=True,
        )

        # 원격 서버로 전송
        conn.put("deploy.tar", f"{deploy_dir}/deploy.tar")

        # 압축 해제
        conn.run(f"cd {deploy_dir} && tar -xf deploy.tar")
        conn.run(f"rm {deploy_dir}/deploy.tar")

        # 로컬 파일 정리
        Path("deploy.tar").unlink()

    def deploy_environment(self, conn: Connection, deploy_dir: str):
        """환경 설정 배포"""
        # 환경 변수 파일 생성
        env_content = f"""
FLASK_ENV=staging
DATABASE_URL={os.getenv('DATABASE_URL')}
SECRET_KEY={os.getenv('SECRET_KEY')}
STAGING_MODE=true
LOG_LEVEL=INFO
        """.strip()

        with open("staging.env", "w") as f:
            f.write(env_content)

        # 원격 서버로 전송
        conn.put("staging.env", f"{deploy_dir}/.env")

        # 로컬 파일 정리
        Path("staging.env").unlink()

    def run_database_migration(self, conn: Connection, deploy_dir: str):
        """데이터베이스 마이그레이션 실행"""
        try:
            conn.run(f"cd {deploy_dir} && python -m alembic upgrade head")
            self.log_deployment(
                "migration", "success", "데이터베이스 마이그레이션 완료"
            )
        except Exception as e:
            self.log_deployment("migration", "warning", f"마이그레이션 실패: {e}")

    def start_application(self, conn: Connection, deploy_dir: str):
        """애플리케이션 시작"""
        # Docker Compose 파일 생성
        docker_compose = f"""
version: '3.8'
services:
  plugin-system:
    image: plugin-system:staging
    container_name: plugin-system
    restart: unless-stopped
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - {deploy_dir}/logs:/app/logs
      - {deploy_dir}/data:/app/data
    networks:
      - plugin-network

networks:
  plugin-network:
    driver: bridge
        """.strip()

        with open("docker-compose.staging.yml", "w") as f:
            f.write(docker_compose)

        # 원격 서버로 전송
        conn.put("docker-compose.staging.yml", f"{deploy_dir}/docker-compose.yml")

        # 컨테이너 시작
        conn.run(f"cd {deploy_dir} && docker-compose up -d")

        # 로컬 파일 정리
        Path("docker-compose.staging.yml").unlink()

    def health_check(self, conn: Connection) -> bool:
        """헬스 체크"""
        max_retries = 10
        retry_interval = 5

        for i in range(max_retries):
            try:
                result = conn.run("curl -f http://localhost:5000/health", hide=True)
                if result.return_code == 0:
                    self.log_deployment("health_check", "success", "헬스 체크 통과")
                    return True
            except Exception:
                pass

            if i < max_retries - 1:
                time.sleep(retry_interval)

        self.log_deployment("health_check", "error", "헬스 체크 실패")
        return False

    def deploy_plugins(self) -> bool:
        """플러그인 배포"""
        logger.info("플러그인 배포 중...")

        try:
            host = os.getenv("STAGING_HOST")
            user = os.getenv("STAGING_USER")
            ssh_key = os.getenv("STAGING_SSH_KEY")

            with Connection(
                host=host, user=user, connect_kwargs={"key_filename": ssh_key}
            ) as conn:
                # 플러그인 디렉토리 생성
                plugin_dir = "/opt/plugin-system/plugins"
                conn.run(f"mkdir -p {plugin_dir}")

                # 플러그인 파일 전송
                for plugin_path in Path("plugins").iterdir():
                    if plugin_path.is_dir():
                        plugin_name = plugin_path.name
                        logger.info(f"플러그인 배포 중: {plugin_name}")

                        # 플러그인 아카이브 생성
                        subprocess.run(
                            [
                                "tar",
                                "-czf",
                                f"{plugin_name}.tar.gz",
                                "-C",
                                "plugins",
                                plugin_name,
                            ],
                            check=True,
                        )

                        # 원격 서버로 전송
                        conn.put(
                            f"{plugin_name}.tar.gz",
                            f"{plugin_dir}/{plugin_name}.tar.gz",
                        )

                        # 압축 해제
                        conn.run(f"cd {plugin_dir} && tar -xzf {plugin_name}.tar.gz")
                        conn.run(f"rm {plugin_dir}/{plugin_name}.tar.gz")

                        # 로컬 파일 정리
                        Path(f"{plugin_name}.tar.gz").unlink()

                self.log_deployment("plugin_deploy", "success", "플러그인 배포 완료")
                return True

        except Exception as e:
            self.log_deployment("plugin_deploy", "error", f"플러그인 배포 실패: {e}")
            return False

    def setup_monitoring(self) -> bool:
        """모니터링 설정"""
        logger.info("모니터링 설정 중...")

        try:
            host = os.getenv("STAGING_HOST")
            user = os.getenv("STAGING_USER")
            ssh_key = os.getenv("STAGING_SSH_KEY")

            with Connection(
                host=host, user=user, connect_kwargs={"key_filename": ssh_key}
            ) as conn:
                # Grafana 설정
                if self.config["monitoring"].get("grafana", {}).get("enabled", False):
                    self.setup_grafana(conn)

                # Prometheus 설정
                if (
                    self.config["monitoring"]
                    .get("prometheus", {})
                    .get("enabled", False)
                ):
                    self.setup_prometheus(conn)

                # 로그 수집 설정
                self.setup_logging(conn)

                self.log_deployment("monitoring", "success", "모니터링 설정 완료")
                return True

        except Exception as e:
            self.log_deployment("monitoring", "error", f"모니터링 설정 실패: {e}")
            return False

    def setup_grafana(self, conn: Connection):
        """Grafana 설정"""
        grafana_config = self.config["monitoring"]["grafana"]

        # Grafana 컨테이너 실행
        docker_compose_grafana = f"""
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "{grafana_config.get('port', 3000)}:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD={grafana_config.get('admin_password', 'admin')}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

volumes:
  grafana-data:
        """.strip()

        conn.put(
            "docker-compose.grafana.yml",
            "/opt/plugin-system/docker-compose.grafana.yml",
        )
        conn.run(
            "cd /opt/plugin-system && docker-compose -f docker-compose.grafana.yml up -d"
        )

    def setup_prometheus(self, conn: Connection):
        """Prometheus 설정"""
        prometheus_config = self.config["monitoring"]["prometheus"]

        # Prometheus 설정 파일 생성
        prometheus_yml = f"""
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'plugin-system'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
        """.strip()

        with open("prometheus.yml", "w") as f:
            f.write(prometheus_yml)

        conn.put("prometheus.yml", "/opt/plugin-system/prometheus.yml")

        # Prometheus 컨테이너 실행
        docker_compose_prometheus = f"""
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "{prometheus_config.get('port', 9090)}:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

volumes:
  prometheus-data:
        """.strip()

        with open("docker-compose.prometheus.yml", "w") as f:
            f.write(docker_compose_prometheus)

        conn.put(
            "docker-compose.prometheus.yml",
            "/opt/plugin-system/docker-compose.prometheus.yml",
        )
        conn.run(
            "cd /opt/plugin-system && docker-compose -f docker-compose.prometheus.yml up -d"
        )

        # 로컬 파일 정리
        Path("prometheus.yml").unlink()
        Path("docker-compose.prometheus.yml").unlink()

    def setup_logging(self, conn: Connection):
        """로깅 설정"""
        # 로그 디렉토리 생성
        conn.run("mkdir -p /opt/plugin-system/logs")

        # 로그 로테이션 설정
        logrotate_config = """
/opt/plugin-system/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
        """.strip()

        with open("plugin-system-logrotate", "w") as f:
            f.write(logrotate_config)

        conn.put("plugin-system-logrotate", "/etc/logrotate.d/plugin-system")
        Path("plugin-system-logrotate").unlink()

    def run_deployment(self) -> bool:
        """전체 배포 프로세스 실행"""
        logger.info("스테이징 배포 시작")

        steps = [
            ("전제 조건 확인", self.check_prerequisites),
            ("현재 배포 백업", self.backup_current_deployment),
            ("Docker 이미지 빌드", self.build_docker_image),
            ("스테이징 서버 배포", self.deploy_to_staging),
            ("플러그인 배포", self.deploy_plugins),
            ("모니터링 설정", self.setup_monitoring),
        ]

        for step_name, step_func in steps:
            logger.info(f"단계 실행 중: {step_name}")
            if not step_func():
                logger.error(f"배포 실패: {step_name}")
                self.save_deployment_log()
                return False

        logger.info("스테이징 배포 완료")
        self.save_deployment_log()
        return True

    def save_deployment_log(self):
        """배포 로그 저장"""
        log_file = f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.deployment_log, f, indent=2, ensure_ascii=False)

        logger.info(f"배포 로그 저장됨: {log_file}")


def main():
    """메인 함수"""
    deployer = StagingDeployer()

    if deployer.run_deployment():
        logger.info("✅ 스테이징 배포가 성공적으로 완료되었습니다")
        sys.exit(0)
    else:
        logger.error("❌ 스테이징 배포가 실패했습니다")
        sys.exit(1)


if __name__ == "__main__":
    main()
