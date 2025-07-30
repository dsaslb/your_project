#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
프로덕션 환경 준비 상태 체크 스크립트
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

class ProductionChecker:
    """프로덕션 준비 상태 체크"""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        
    def check(self, name: str, condition: bool, message: str = ""):
        """체크 수행"""
        if condition:
            print(f"✅ {name}")
            self.passed += 1
        else:
            print(f"❌ {name}" + (f" - {message}" if message else ""))
            self.failed += 1
        self.checks.append((name, condition, message))
        
    def check_environment_files(self):
        """환경 설정 파일 확인"""
        print("\n🔧 환경 설정 파일 확인")
        print("=" * 50)
        
        env_files = [
            "config/production.env",
            "config/development.env",
            "docker-compose.production.yml",
            "nginx/nginx.conf"
        ]
        
        for file in env_files:
            exists = Path(file).exists()
            self.check(f"{file} 존재", exists, f"파일이 없습니다: {file}")
            
    def check_docker_setup(self):
        """Docker 설정 확인"""
        print("\n🐳 Docker 설정 확인")
        print("=" * 50)
        
        try:
            # Docker 설치 확인
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            self.check("Docker 설치", result.returncode == 0)
            
            # Docker Compose 설치 확인
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True)
            self.check("Docker Compose 설치", result.returncode == 0)
            
        except FileNotFoundError:
            self.check("Docker 설치", False, "Docker가 시스템에 설치되지 않았습니다")
            
    def check_ssl_certificates(self):
        """SSL 인증서 확인"""
        print("\n🔒 SSL 인증서 확인")
        print("=" * 50)
        
        ssl_files = [
            "nginx/ssl/cert.pem",
            "nginx/ssl/key.pem"
        ]
        
        for file in ssl_files:
            exists = Path(file).exists()
            self.check(f"SSL 인증서: {file}", exists, 
                      "프로덕션 배포 전 SSL 인증서를 설정해주세요")
            
    def check_security_settings(self):
        """보안 설정 확인"""
        print("\n🛡️ 보안 설정 확인")
        print("=" * 50)
        
        # 환경 변수 확인
        from dotenv import load_dotenv
        load_dotenv('config/production.env')
        
        secret_key = os.getenv('SECRET_KEY')
        jwt_key = os.getenv('JWT_SECRET_KEY')
        
        self.check("SECRET_KEY 설정", secret_key and len(secret_key) > 20,
                  "강력한 SECRET_KEY를 설정해주세요")
        self.check("JWT_SECRET_KEY 설정", jwt_key and len(jwt_key) > 20,
                  "강력한 JWT_SECRET_KEY를 설정해주세요")
        
        # 기본값 체크
        default_secrets = [
            "your-super-strong-secret-key-change-this",
            "your-jwt-secret-key-change-this",
            "dev-secret-key"
        ]
        
        secure_key = secret_key not in default_secrets if secret_key else False
        self.check("SECRET_KEY 보안성", secure_key,
                  "기본값에서 변경해주세요")
                  
    def check_database_connection(self):
        """데이터베이스 연결 확인"""
        print("\n🗄️ 데이터베이스 연결 확인")
        print("=" * 50)
        
        # PostgreSQL 컨테이너 상태 확인
        try:
            result = subprocess.run([
                "docker-compose", "-f", "docker-compose.production.yml", 
                "ps", "postgres"
            ], capture_output=True, text=True)
            
            postgres_running = "Up" in result.stdout
            self.check("PostgreSQL 컨테이너", postgres_running,
                      "PostgreSQL 컨테이너를 시작해주세요")
                      
        except Exception as e:
            self.check("PostgreSQL 확인", False, str(e))
            
    def check_application_health(self):
        """애플리케이션 상태 확인"""
        print("\n🏥 애플리케이션 헬스체크")
        print("=" * 50)
        
        health_endpoints = [
            ("http://localhost/health", "메인 애플리케이션"),
            ("http://localhost:9090", "Prometheus 모니터링"),
            ("http://localhost:3001", "Grafana 대시보드")
        ]
        
        for url, name in health_endpoints:
            try:
                response = requests.get(url, timeout=5)
                self.check(f"{name} 접근", response.status_code == 200)
            except requests.RequestException:
                self.check(f"{name} 접근", False, 
                          f"서비스가 실행되지 않았거나 접근할 수 없습니다: {url}")
                          
    def check_monitoring_setup(self):
        """모니터링 설정 확인"""
        print("\n📊 모니터링 설정 확인")
        print("=" * 50)
        
        monitoring_files = [
            "monitoring/prometheus.yml",
            "grafana/dashboards",
            "monitoring/filebeat.yml"
        ]
        
        for item in monitoring_files:
            path = Path(item)
            exists = path.exists()
            self.check(f"모니터링 설정: {item}", exists)
            
    def run_all_checks(self):
        """모든 체크 실행"""
        print("🚀 Your Program 프로덕션 준비 상태 점검")
        print("=" * 60)
        
        self.check_environment_files()
        self.check_docker_setup()
        self.check_ssl_certificates()
        self.check_security_settings()
        self.check_database_connection()
        self.check_application_health()
        self.check_monitoring_setup()
        
        # 결과 요약
        print("\n📋 점검 결과 요약")
        print("=" * 50)
        print(f"✅ 통과: {self.passed}개")
        print(f"❌ 실패: {self.failed}개")
        print(f"📊 성공률: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed == 0:
            print("\n🎉 모든 점검을 통과했습니다! 프로덕션 배포 준비가 완료되었습니다.")
            return True
        else:
            print(f"\n⚠️  {self.failed}개의 문제를 해결한 후 다시 점검해주세요.")
            return False

if __name__ == "__main__":
    checker = ProductionChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)