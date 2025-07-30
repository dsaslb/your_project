#!/usr/bin/env python3
"""
🔍 Your Program 프로덕션 준비도 점검 스크립트

이 스크립트는 프로덕션 배포 전 시스템의 모든 구성 요소를 점검하여
안전한 배포가 가능한지 확인합니다.

사용법:
    python scripts/production_readiness_check.py
    python scripts/production_readiness_check.py --detailed
    python scripts/production_readiness_check.py --fix-issues
"""

import asyncio
import logging
import sys
import json
import time
import subprocess
import psutil
import redis
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import argparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('production_check.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CheckResult:
    """점검 결과 데이터 클래스"""
    component: str
    status: str  # 'pass', 'warning', 'fail'
    score: int  # 0-100
    message: str
    details: Dict[str, Any]
    recommendations: List[str]

class ProductionReadinessChecker:
    """프로덕션 준비도 점검 클래스"""
    
    def __init__(self, config_path: str = "config/production.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.results: List[CheckResult] = []
        self.overall_score = 0
        
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        default_config = {
            "services": {
                "api_gateway": {"port": 8000, "health_endpoint": "/health"},
                "ai_ml": {"port": 8001, "health_endpoint": "/health"},
                "data_analysis": {"port": 8002, "health_endpoint": "/health"},
                "blockchain": {"port": 8003, "health_endpoint": "/health"},
                "iot": {"port": 8004, "health_endpoint": "/health"},
                "security": {"port": 8007, "health_endpoint": "/security/status"}
            },
            "databases": {
                "postgresql": {"host": "localhost", "port": 5432, "dbname": "yourprogram"},
                "redis": {"host": "localhost", "port": 6379, "db": 0}
            },
            "thresholds": {
                "cpu_max": 80,
                "memory_max": 85,
                "disk_max": 90,
                "response_time_max": 2000,
                "error_rate_max": 1.0
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본 설정과 병합
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패, 기본 설정 사용: {e}")
        
        return default_config
    
    async def run_all_checks(self, detailed: bool = False) -> Dict[str, Any]:
        """모든 점검 항목 실행"""
        logger.info("🔍 Your Program 프로덕션 준비도 점검 시작")
        
        checks = [
            ("시스템 리소스", self.check_system_resources),
            ("서비스 상태", self.check_services),
            ("데이터베이스", self.check_databases),
            ("보안 설정", self.check_security),
            ("성능 지표", self.check_performance),
            ("모니터링", self.check_monitoring),
            ("백업 시스템", self.check_backup_system),
            ("네트워크", self.check_network),
            ("문서화", self.check_documentation),
            ("환경 설정", self.check_environment)
        ]
        
        for name, check_func in checks:
            try:
                logger.info(f"📋 {name} 점검 중...")
                result = await check_func(detailed)
                self.results.append(result)
                
                # 상태별 이모지
                status_emoji = {"pass": "✅", "warning": "⚠️", "fail": "❌"}
                emoji = status_emoji.get(result.status, "❓")
                
                logger.info(f"{emoji} {name}: {result.message} (점수: {result.score}/100)")
                
            except Exception as e:
                logger.error(f"❌ {name} 점검 실패: {e}")
                self.results.append(CheckResult(
                    component=name,
                    status="fail",
                    score=0,
                    message=f"점검 실패: {str(e)}",
                    details={"error": str(e)},
                    recommendations=[f"{name} 점검 스크립트 수정 필요"]
                ))
        
        # 전체 점수 계산
        self.calculate_overall_score()
        
        return self.generate_report()
    
    async def check_system_resources(self, detailed: bool = False) -> CheckResult:
        """시스템 리소스 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        details["cpu_usage"] = cpu_percent
        
        if cpu_percent > self.config["thresholds"]["cpu_max"]:
            issues.append(f"CPU 사용률 높음: {cpu_percent}%")
            recommendations.append("CPU 사용률이 높습니다. 불필요한 프로세스를 종료하거나 서버 자원을 확장하세요.")
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        details["memory_usage"] = memory.percent
        details["memory_available"] = f"{memory.available / (1024**3):.1f}GB"
        
        if memory.percent > self.config["thresholds"]["memory_max"]:
            issues.append(f"메모리 사용률 높음: {memory.percent}%")
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수를 확인하거나 RAM을 확장하세요.")
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        details["disk_usage"] = disk_percent
        details["disk_free"] = f"{disk.free / (1024**3):.1f}GB"
        
        if disk_percent > self.config["thresholds"]["disk_max"]:
            issues.append(f"디스크 사용률 높음: {disk_percent:.1f}%")
            recommendations.append("디스크 공간이 부족합니다. 불필요한 파일을 삭제하거나 디스크를 확장하세요.")
        
        # 네트워크 연결
        connections = len(psutil.net_connections())
        details["network_connections"] = connections
        
        # 시스템 부하
        load_avg = psutil.getloadavg()
        details["load_average"] = {"1min": load_avg[0], "5min": load_avg[1], "15min": load_avg[2]}
        
        # 점수 계산
        score = 100
        if issues:
            score = max(0, 100 - len(issues) * 20)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"시스템 리소스 정상" if not issues else f"{len(issues)}개 이슈 발견"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="시스템 리소스",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_services(self, detailed: bool = False) -> CheckResult:
        """서비스 상태 점검"""
        details = {}
        recommendations = []
        issues = []
        service_statuses = {}
        
        for service_name, service_config in self.config["services"].items():
            try:
                url = f"http://localhost:{service_config['port']}{service_config['health_endpoint']}"
                
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    service_statuses[service_name] = {
                        "status": "healthy",
                        "response_time": response_time,
                        "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    }
                    
                    if response_time > self.config["thresholds"]["response_time_max"]:
                        issues.append(f"{service_name} 응답 시간 느림: {response_time:.0f}ms")
                        recommendations.append(f"{service_name} 서비스 성능을 최적화하세요.")
                else:
                    service_statuses[service_name] = {
                        "status": "unhealthy",
                        "response_time": response_time,
                        "error": f"HTTP {response.status_code}"
                    }
                    issues.append(f"{service_name} 서비스 비정상: HTTP {response.status_code}")
                    recommendations.append(f"{service_name} 서비스를 재시작하고 로그를 확인하세요.")
                    
            except requests.exceptions.ConnectionError:
                service_statuses[service_name] = {
                    "status": "offline",
                    "error": "Connection refused"
                }
                issues.append(f"{service_name} 서비스 오프라인")
                recommendations.append(f"{service_name} 서비스를 시작하세요.")
                
            except Exception as e:
                service_statuses[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                issues.append(f"{service_name} 점검 실패: {str(e)}")
                recommendations.append(f"{service_name} 서비스 설정을 확인하세요.")
        
        details["services"] = service_statuses
        details["total_services"] = len(self.config["services"])
        details["healthy_services"] = len([s for s in service_statuses.values() if s["status"] == "healthy"])
        
        # 점수 계산
        healthy_ratio = details["healthy_services"] / details["total_services"]
        score = int(healthy_ratio * 100)
        
        if issues:
            score = max(0, score - len(issues) * 10)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"{details['healthy_services']}/{details['total_services']} 서비스 정상"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="서비스 상태",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_databases(self, detailed: bool = False) -> CheckResult:
        """데이터베이스 상태 점검"""
        details = {}
        recommendations = []
        issues = []
        db_statuses = {}
        
        # PostgreSQL 점검
        try:
            import psycopg2
            pg_config = self.config["databases"]["postgresql"]
            
            conn = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                dbname=pg_config["dbname"],
                user=pg_config.get("user", "postgres"),
                password=pg_config.get("password", ""),
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # 연결 수 확인
            cursor.execute("SELECT count(*) FROM pg_stat_activity;")
            connection_count = cursor.fetchone()[0]
            
            # 데이터베이스 크기 확인
            cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{pg_config['dbname']}'));")
            db_size = cursor.fetchone()[0]
            
            # 테이블 수 확인
            cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            
            db_statuses["postgresql"] = {
                "status": "connected",
                "connections": connection_count,
                "database_size": db_size,
                "table_count": table_count
            }
            
            if connection_count > 100:
                issues.append(f"PostgreSQL 연결 수 많음: {connection_count}")
                recommendations.append("PostgreSQL 연결 풀 설정을 확인하고 최적화하세요.")
            
            conn.close()
            
        except Exception as e:
            db_statuses["postgresql"] = {
                "status": "error",
                "error": str(e)
            }
            issues.append(f"PostgreSQL 연결 실패: {str(e)}")
            recommendations.append("PostgreSQL 서비스 상태와 연결 설정을 확인하세요.")
        
        # Redis 점검
        try:
            redis_config = self.config["databases"]["redis"]
            r = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                socket_timeout=10
            )
            
            # Redis 정보 확인
            info = r.info()
            
            db_statuses["redis"] = {
                "status": "connected",
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime": info.get("uptime_in_seconds")
            }
            
            if info.get("connected_clients", 0) > 1000:
                issues.append(f"Redis 클라이언트 수 많음: {info.get('connected_clients')}")
                recommendations.append("Redis 연결 관리를 최적화하세요.")
            
        except Exception as e:
            db_statuses["redis"] = {
                "status": "error",
                "error": str(e)
            }
            issues.append(f"Redis 연결 실패: {str(e)}")
            recommendations.append("Redis 서비스 상태와 연결 설정을 확인하세요.")
        
        details["databases"] = db_statuses
        
        # 점수 계산
        connected_dbs = len([db for db in db_statuses.values() if db["status"] == "connected"])
        total_dbs = len(db_statuses)
        
        if total_dbs > 0:
            score = int((connected_dbs / total_dbs) * 100)
        else:
            score = 0
        
        if issues:
            score = max(0, score - len(issues) * 15)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"{connected_dbs}/{total_dbs} 데이터베이스 연결 정상"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="데이터베이스",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_security(self, detailed: bool = False) -> CheckResult:
        """보안 설정 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 보안 파일 존재 확인
        security_files = {
            "SSL 인증서": Path("/etc/ssl/certs/yourprogram.crt"),
            "개인키": Path("/etc/ssl/private/yourprogram.key"),
            "보안 정책": Path("docs/SECURITY_POLICY.md"),
            "방화벽 규칙": Path("/etc/ufw/user.rules")
        }
        
        file_status = {}
        for name, path in security_files.items():
            if path.exists():
                file_status[name] = "존재"
                if name == "SSL 인증서":
                    # SSL 인증서 만료일 확인 (실제 환경에서는 openssl 명령 사용)
                    details["ssl_cert_status"] = "유효"
            else:
                file_status[name] = "없음"
                if name in ["SSL 인증서", "개인키"]:
                    issues.append(f"{name} 파일이 없습니다")
                    recommendations.append(f"{name}를 생성하고 적절한 위치에 배치하세요.")
        
        details["security_files"] = file_status
        
        # 보안 모니터링 서비스 확인
        try:
            response = requests.get("http://localhost:8007/security/status", timeout=5)
            if response.status_code == 200:
                security_status = response.json()
                details["security_monitoring"] = {
                    "status": "active",
                    "threat_level": security_status.get("data", {}).get("threat_level", "unknown"),
                    "active_threats": security_status.get("data", {}).get("active_threats", 0)
                }
                
                if security_status.get("data", {}).get("active_threats", 0) > 0:
                    issues.append("활성 보안 위협 탐지됨")
                    recommendations.append("보안 위협을 즉시 조사하고 대응하세요.")
            else:
                details["security_monitoring"] = {"status": "error", "code": response.status_code}
                issues.append("보안 모니터링 서비스 오류")
                recommendations.append("보안 모니터링 서비스를 재시작하세요.")
        except:
            details["security_monitoring"] = {"status": "offline"}
            issues.append("보안 모니터링 서비스 오프라인")
            recommendations.append("보안 모니터링 서비스를 시작하세요.")
        
        # 방화벽 상태 확인
        try:
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=10)
            if "Status: active" in result.stdout:
                details["firewall"] = "활성"
            else:
                details["firewall"] = "비활성"
                issues.append("방화벽이 비활성화됨")
                recommendations.append("방화벽을 활성화하세요: sudo ufw enable")
        except:
            details["firewall"] = "확인 불가"
            issues.append("방화벽 상태 확인 실패")
            recommendations.append("방화벽 설정을 확인하세요.")
        
        # 점수 계산
        score = 100
        if issues:
            score = max(0, 100 - len(issues) * 20)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = "보안 설정 정상" if not issues else f"{len(issues)}개 보안 이슈 발견"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="보안 설정",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_performance(self, detailed: bool = False) -> CheckResult:
        """성능 지표 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # API 성능 테스트
        api_tests = [
            ("API Gateway Health", "http://localhost:8000/health"),
            ("API Gateway Metrics", "http://localhost:8000/metrics"),
            ("Security Status", "http://localhost:8007/security/status")
        ]
        
        performance_results = {}
        total_response_time = 0
        successful_tests = 0
        
        for test_name, url in api_tests:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                total_response_time += response_time
                
                if response.status_code == 200:
                    successful_tests += 1
                    status = "성공"
                    if response_time > self.config["thresholds"]["response_time_max"]:
                        issues.append(f"{test_name} 응답 시간 느림: {response_time:.0f}ms")
                else:
                    status = f"HTTP {response.status_code}"
                    issues.append(f"{test_name} 실패: HTTP {response.status_code}")
                
                performance_results[test_name] = {
                    "status": status,
                    "response_time": response_time
                }
                
            except Exception as e:
                performance_results[test_name] = {
                    "status": "오류",
                    "error": str(e)
                }
                issues.append(f"{test_name} 테스트 실패: {str(e)}")
        
        if successful_tests > 0:
            avg_response_time = total_response_time / successful_tests
            details["average_response_time"] = avg_response_time
        else:
            details["average_response_time"] = 0
            issues.append("모든 성능 테스트 실패")
        
        details["performance_tests"] = performance_results
        details["success_rate"] = (successful_tests / len(api_tests)) * 100
        
        # 점수 계산
        score = int(details["success_rate"])
        if issues:
            score = max(0, score - len(issues) * 10)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"성능 테스트 {details['success_rate']:.0f}% 성공"
        if details["average_response_time"] > 0:
            message += f", 평균 응답시간: {details['average_response_time']:.0f}ms"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="성능 지표",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_monitoring(self, detailed: bool = False) -> CheckResult:
        """모니터링 시스템 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 모니터링 대시보드 파일 확인
        dashboard_files = [
            "templates/integration_dashboard.html",
            "templates/performance_dashboard.html", 
            "templates/security_dashboard.html"
        ]
        
        existing_dashboards = []
        for dashboard in dashboard_files:
            if Path(dashboard).exists():
                existing_dashboards.append(dashboard)
            else:
                issues.append(f"대시보드 파일 없음: {dashboard}")
                recommendations.append(f"{dashboard} 파일을 생성하세요.")
        
        details["dashboard_files"] = {
            "total": len(dashboard_files),
            "existing": len(existing_dashboards),
            "files": existing_dashboards
        }
        
        # 로그 파일 확인
        log_directories = [
            Path("logs"),
            Path("/var/log/yourprogram")
        ]
        
        log_status = {}
        for log_dir in log_directories:
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                log_status[str(log_dir)] = {
                    "exists": True,
                    "file_count": len(log_files),
                    "files": [f.name for f in log_files[:5]]  # 최대 5개만 표시
                }
            else:
                log_status[str(log_dir)] = {"exists": False}
                issues.append(f"로그 디렉토리 없음: {log_dir}")
                recommendations.append(f"로그 디렉토리를 생성하세요: mkdir -p {log_dir}")
        
        details["log_directories"] = log_status
        
        # 모니터링 스크립트 확인
        monitoring_scripts = [
            "scripts/production_readiness_check.py",
            "monitoring/performance_monitor.py",
            "security/security_monitor.py"
        ]
        
        script_status = {}
        for script in monitoring_scripts:
            script_path = Path(script)
            if script_path.exists():
                script_status[script] = "존재"
            else:
                script_status[script] = "없음"
                issues.append(f"모니터링 스크립트 없음: {script}")
        
        details["monitoring_scripts"] = script_status
        
        # 점수 계산
        total_components = len(dashboard_files) + len(log_directories) + len(monitoring_scripts)
        working_components = len(existing_dashboards) + len([d for d in log_status.values() if d.get("exists")]) + len([s for s in script_status.values() if s == "존재"])
        
        score = int((working_components / total_components) * 100) if total_components > 0 else 0
        
        if issues:
            score = max(0, score - len(issues) * 10)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"모니터링 구성 요소 {working_components}/{total_components} 정상"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="모니터링",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_backup_system(self, detailed: bool = False) -> CheckResult:
        """백업 시스템 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 백업 디렉토리 확인
        backup_dirs = [
            Path("backups"),
            Path("/opt/backups"),
            Path("/backup")
        ]
        
        backup_status = {}
        active_backup_dir = None
        
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                backup_files = list(backup_dir.rglob("*.dump*")) + list(backup_dir.rglob("*.tar.gz")) + list(backup_dir.rglob("*.zip"))
                backup_status[str(backup_dir)] = {
                    "exists": True,
                    "file_count": len(backup_files),
                    "latest_backup": max([f.stat().st_mtime for f in backup_files]) if backup_files else 0
                }
                if backup_files:
                    active_backup_dir = backup_dir
            else:
                backup_status[str(backup_dir)] = {"exists": False}
        
        details["backup_directories"] = backup_status
        
        # 백업 스크립트 확인
        backup_scripts = [
            "scripts/backup_database.sh",
            "scripts/backup_system.sh"
        ]
        
        script_status = {}
        for script in backup_scripts:
            if Path(script).exists():
                script_status[script] = "존재"
            else:
                script_status[script] = "없음"
                issues.append(f"백업 스크립트 없음: {script}")
                recommendations.append(f"백업 스크립트를 생성하세요: {script}")
        
        details["backup_scripts"] = script_status
        
        # 최근 백업 확인
        if active_backup_dir:
            latest_backup_time = max([status.get("latest_backup", 0) for status in backup_status.values() if status.get("exists")])
            if latest_backup_time > 0:
                hours_since_backup = (time.time() - latest_backup_time) / 3600
                details["hours_since_last_backup"] = hours_since_backup
                
                if hours_since_backup > 24:
                    issues.append(f"마지막 백업이 {hours_since_backup:.1f}시간 전")
                    recommendations.append("백업을 정기적으로 실행하도록 cron job을 설정하세요.")
            else:
                issues.append("백업 파일을 찾을 수 없음")
                recommendations.append("초기 백업을 실행하세요.")
        else:
            issues.append("활성 백업 디렉토리 없음")
            recommendations.append("백업 디렉토리를 생성하고 백업을 설정하세요.")
        
        # 점수 계산
        score = 100
        if not active_backup_dir:
            score -= 50
        if issues:
            score = max(0, score - len(issues) * 15)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = "백업 시스템 정상" if not issues else f"백업 관련 {len(issues)}개 이슈"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="백업 시스템",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_network(self, detailed: bool = False) -> CheckResult:
        """네트워크 연결 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 포트 사용 현황 확인
        required_ports = [8000, 8001, 8002, 8003, 8004, 8007, 5432, 6379]
        port_status = {}
        
        for port in required_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    port_status[port] = "열림"
                else:
                    port_status[port] = "닫힘"
                    if port in [8000, 8001, 8002, 8007]:  # 핵심 서비스 포트
                        issues.append(f"핵심 서비스 포트 {port} 닫힘")
                        recommendations.append(f"포트 {port}에서 실행되는 서비스를 시작하세요.")
            except Exception as e:
                port_status[port] = f"오류: {str(e)}"
                issues.append(f"포트 {port} 점검 실패")
        
        details["port_status"] = port_status
        
        # 네트워크 인터페이스 확인
        network_interfaces = psutil.net_if_addrs()
        active_interfaces = {}
        
        for interface, addresses in network_interfaces.items():
            if interface != 'lo':  # loopback 제외
                ipv4_addresses = [addr.address for addr in addresses if addr.family == socket.AF_INET]
                if ipv4_addresses:
                    active_interfaces[interface] = ipv4_addresses[0]
        
        details["network_interfaces"] = active_interfaces
        
        # 외부 연결 테스트
        external_tests = [
            ("Google DNS", "8.8.8.8", 53),
            ("Cloudflare DNS", "1.1.1.1", 53)
        ]
        
        connectivity_status = {}
        for name, host, port in external_tests:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                connectivity_status[name] = "연결 가능" if result == 0 else "연결 실패"
                if result != 0:
                    issues.append(f"외부 연결 실패: {name}")
            except Exception as e:
                connectivity_status[name] = f"오류: {str(e)}"
                issues.append(f"외부 연결 테스트 실패: {name}")
        
        details["external_connectivity"] = connectivity_status
        
        # 점수 계산
        open_ports = len([status for status in port_status.values() if status == "열림"])
        total_ports = len(required_ports)
        port_score = (open_ports / total_ports) * 100
        
        connectivity_score = len([status for status in connectivity_status.values() if status == "연결 가능"]) / len(external_tests) * 100
        
        score = int((port_score + connectivity_score) / 2)
        
        if issues:
            score = max(0, score - len(issues) * 10)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"네트워크 연결 {score}% 정상"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="네트워크",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_documentation(self, detailed: bool = False) -> CheckResult:
        """문서화 상태 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 필수 문서 파일 확인
        required_docs = [
            "docs/SYSTEM_ADMINISTRATOR_GUIDE.md",
            "docs/USER_MANUAL.md", 
            "docs/SECURITY_POLICY.md",
            "docs/API_REFERENCE.md",
            "docs/DEPLOYMENT_GUIDE.md",
            "docs/TRAINING_MATERIALS.md",
            "FINAL_PROJECT_COMPLETION_REPORT.md",
            "README.md"
        ]
        
        doc_status = {}
        existing_docs = 0
        
        for doc in required_docs:
            doc_path = Path(doc)
            if doc_path.exists():
                doc_status[doc] = {
                    "exists": True,
                    "size": doc_path.stat().st_size,
                    "modified": datetime.fromtimestamp(doc_path.stat().st_mtime).strftime("%Y-%m-%d")
                }
                existing_docs += 1
            else:
                doc_status[doc] = {"exists": False}
                issues.append(f"필수 문서 없음: {doc}")
                recommendations.append(f"필수 문서를 작성하세요: {doc}")
        
        details["documentation"] = doc_status
        details["completion_rate"] = (existing_docs / len(required_docs)) * 100
        
        # 설정 파일 확인
        config_files = [
            "config/production.json",
            "config/config.py",
            ".env.production"
        ]
        
        config_status = {}
        for config_file in config_files:
            if Path(config_file).exists():
                config_status[config_file] = "존재"
            else:
                config_status[config_file] = "없음"
                if config_file == "config/production.json":
                    issues.append(f"중요 설정 파일 없음: {config_file}")
                    recommendations.append(f"프로덕션 설정 파일을 생성하세요: {config_file}")
        
        details["config_files"] = config_status
        
        # 점수 계산
        score = int(details["completion_rate"])
        
        if issues:
            score = max(0, score - len(issues) * 10)
        
        status = "pass"
        if score < 80:
            status = "fail"
        elif score < 95:
            status = "warning"
        
        message = f"문서화 {details['completion_rate']:.0f}% 완료"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="문서화",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    async def check_environment(self, detailed: bool = False) -> CheckResult:
        """환경 설정 점검"""
        details = {}
        recommendations = []
        issues = []
        
        # 환경 변수 확인
        import os
        required_env_vars = [
            "DATABASE_URL",
            "REDIS_URL", 
            "JWT_SECRET",
            "NODE_ENV"
        ]
        
        env_status = {}
        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                env_status[var] = "설정됨" if var != "JWT_SECRET" else "설정됨 (보안)"
            else:
                env_status[var] = "없음"
                issues.append(f"환경 변수 없음: {var}")
                recommendations.append(f"환경 변수를 설정하세요: {var}")
        
        details["environment_variables"] = env_status
        
        # Python 패키지 확인
        try:
            import pkg_resources
            
            required_packages = [
                "fastapi", "uvicorn", "psycopg2", "redis", "sqlalchemy",
                "prometheus_client", "requests", "psutil"
            ]
            
            package_status = {}
            for package in required_packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    package_status[package] = f"v{version}"
                except pkg_resources.DistributionNotFound:
                    package_status[package] = "없음"
                    issues.append(f"필수 패키지 없음: {package}")
                    recommendations.append(f"패키지를 설치하세요: pip install {package}")
            
            details["python_packages"] = package_status
            
        except Exception as e:
            details["python_packages"] = {"error": str(e)}
            issues.append("패키지 확인 실패")
        
        # 디렉토리 구조 확인
        required_dirs = [
            "logs", "config", "static", "templates", 
            "api", "security", "monitoring", "docs"
        ]
        
        dir_status = {}
        for directory in required_dirs:
            if Path(directory).exists():
                dir_status[directory] = "존재"
            else:
                dir_status[directory] = "없음"
                issues.append(f"디렉토리 없음: {directory}")
                recommendations.append(f"디렉토리를 생성하세요: mkdir -p {directory}")
        
        details["directory_structure"] = dir_status
        
        # 점수 계산
        total_checks = len(required_env_vars) + len(required_packages) + len(required_dirs)
        passed_checks = (
            len([v for v in env_status.values() if "설정됨" in v]) +
            len([v for v in package_status.values() if v != "없음"]) +
            len([v for v in dir_status.values() if v == "존재"])
        )
        
        score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 0
        
        if issues:
            score = max(0, score - len(issues) * 5)
        
        status = "pass"
        if score < 70:
            status = "fail"
        elif score < 90:
            status = "warning"
        
        message = f"환경 설정 {score}% 완료"
        
        if detailed:
            details["issues"] = issues
        
        return CheckResult(
            component="환경 설정",
            status=status,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )
    
    def calculate_overall_score(self):
        """전체 점수 계산"""
        if not self.results:
            self.overall_score = 0
            return
        
        # 가중치 적용
        weights = {
            "시스템 리소스": 1.2,
            "서비스 상태": 1.5,
            "데이터베이스": 1.3,
            "보안 설정": 1.4,
            "성능 지표": 1.1,
            "모니터링": 1.0,
            "백업 시스템": 1.0,
            "네트워크": 1.1,
            "문서화": 0.8,
            "환경 설정": 1.0
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        for result in self.results:
            weight = weights.get(result.component, 1.0)
            total_weighted_score += result.score * weight
            total_weight += weight
        
        self.overall_score = int(total_weighted_score / total_weight) if total_weight > 0 else 0
    
    def generate_report(self) -> Dict[str, Any]:
        """최종 보고서 생성"""
        # 상태별 통계
        status_counts = {"pass": 0, "warning": 0, "fail": 0}
        for result in self.results:
            status_counts[result.status] += 1
        
        # 전체 권장사항 수집
        all_recommendations = []
        critical_issues = []
        
        for result in self.results:
            all_recommendations.extend(result.recommendations)
            if result.status == "fail":
                critical_issues.append(f"{result.component}: {result.message}")
        
        # 준비도 평가
        if self.overall_score >= 90:
            readiness_status = "프로덕션 준비 완료"
            readiness_emoji = "🎉"
        elif self.overall_score >= 80:
            readiness_status = "거의 준비됨 (경미한 이슈 해결 필요)"
            readiness_emoji = "⚠️"
        elif self.overall_score >= 70:
            readiness_status = "추가 작업 필요"
            readiness_emoji = "🔧"
        else:
            readiness_status = "프로덕션 배포 불가 (중대한 이슈 해결 필요)"
            readiness_emoji = "❌"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_score": self.overall_score,
            "readiness_status": readiness_status,
            "readiness_emoji": readiness_emoji,
            "status_summary": status_counts,
            "critical_issues": critical_issues,
            "total_recommendations": len(all_recommendations),
            "unique_recommendations": list(set(all_recommendations)),
            "detailed_results": [
                {
                    "component": r.component,
                    "status": r.status,
                    "score": r.score,
                    "message": r.message,
                    "recommendations": r.recommendations
                }
                for r in self.results
            ]
        }
    
    def print_summary_report(self, report: Dict[str, Any]):
        """요약 보고서 출력"""
        print("\n" + "="*60)
        print(f"{report['readiness_emoji']} YOUR PROGRAM 프로덕션 준비도 점검 결과")
        print("="*60)
        print(f"📊 전체 점수: {report['overall_score']}/100")
        print(f"🎯 준비 상태: {report['readiness_status']}")
        print(f"📅 점검 시간: {report['timestamp']}")
        
        print(f"\n📋 구성 요소별 결과:")
        status_icons = {"pass": "✅", "warning": "⚠️", "fail": "❌"}
        
        for result in report['detailed_results']:
            icon = status_icons.get(result['status'], "❓")
            print(f"  {icon} {result['component']}: {result['message']} ({result['score']}/100)")
        
        print(f"\n📈 상태 요약:")
        summary = report['status_summary']
        print(f"  ✅ 정상: {summary['pass']}개")
        print(f"  ⚠️  주의: {summary['warning']}개") 
        print(f"  ❌ 실패: {summary['fail']}개")
        
        if report['critical_issues']:
            print(f"\n🚨 중요 이슈:")
            for issue in report['critical_issues']:
                print(f"  • {issue}")
        
        if report['unique_recommendations']:
            print(f"\n💡 권장사항 ({report['total_recommendations']}개):")
            for i, recommendation in enumerate(report['unique_recommendations'][:5], 1):
                print(f"  {i}. {recommendation}")
            
            if len(report['unique_recommendations']) > 5:
                print(f"  ... 외 {len(report['unique_recommendations']) - 5}개")
        
        print("\n" + "="*60)


async def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Your Program 프로덕션 준비도 점검")
    parser.add_argument("--detailed", action="store_true", help="상세 정보 포함")
    parser.add_argument("--fix-issues", action="store_true", help="발견된 이슈 자동 수정 시도")
    parser.add_argument("--config", default="config/production.json", help="설정 파일 경로")
    parser.add_argument("--output", help="결과를 JSON 파일로 저장")
    
    args = parser.parse_args()
    
    try:
        checker = ProductionReadinessChecker(args.config)
        report = await checker.run_all_checks(detailed=args.detailed)
        
        # 결과 출력
        checker.print_summary_report(report)
        
        # JSON 파일로 저장
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 상세 결과가 {args.output}에 저장되었습니다.")
        
        # 자동 수정 시도
        if args.fix_issues:
            print("\n🔧 이슈 자동 수정 시도 중...")
            # TODO: 자동 수정 로직 구현
            print("ℹ️  자동 수정 기능은 추후 구현 예정입니다.")
        
        # 종료 코드 설정
        if report['overall_score'] >= 80:
            sys.exit(0)  # 성공
        else:
            sys.exit(1)  # 실패
            
    except KeyboardInterrupt:
        print("\n\n⏹️  점검이 사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 점검 중 오류 발생: {e}")
        logger.exception("점검 실행 중 예외 발생")
        sys.exit(1)


if __name__ == "__main__":
    # Python 3.7+ 호환성
    try:
        asyncio.run(main())
    except AttributeError:
        # Python 3.6 이하에서는 asyncio.run이 없음
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main()) 