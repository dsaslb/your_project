#!/usr/bin/env python3
"""
플러그인 모니터링 시스템 배포 자동화 스크립트
CI/CD 파이프라인에서 사용되는 자동 배포 스크립트입니다.
"""

import json
import time
import subprocess
import requests
import sys
from datetime import datetime

class PluginMonitoringDeployer:
    def __init__(self, environment="staging"):
        self.environment = environment
        self.deployment_log = {
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "steps": [],
            "status": "pending"
        }
        
        # 환경별 설정
        self.configs = {
            "staging": {
                "base_url": "https://staging.yourprogram.com",
                "docker_registry": "your-registry.com",
                "namespace": "your-program-system-staging"
            },
            "production": {
                "base_url": "https://yourprogram.com",
                "docker_registry": "your-registry.com",
                "namespace": "your-program-system"
            }
        }
        
        self.config = self.configs.get(environment, self.configs["staging"])
    
    def log_step(self, step_name, status, details=None, error=None):
        """배포 단계 로깅"""
        step = {
            "name": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if error:
            step["error"] = str(error)
        
        self.deployment_log["steps"].append(step)
        print(f"[{status.upper()}] {step_name}")
        
        if details:
            print(f"  Details: {details}")
        if error:
            print(f"  Error: {error}")
    
    def run_command(self, command, cwd=None, timeout=300):
        """명령어 실행"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def build_docker_images(self):
        """Docker 이미지 빌드"""
        try:
            # 백엔드 이미지 빌드
            success, output = self.run_command(
                f"docker build -f Dockerfile.backend -t {self.config['docker_registry']}/your-program-backend:plugin-monitoring-{self.environment} ."
            )
            
            if not success:
                self.log_step("Build Backend Image", "FAILED", error=output)
                return False
            
            self.log_step("Build Backend Image", "PASSED", "Backend image built successfully")
            
            # 프론트엔드 이미지 빌드
            success, output = self.run_command(
                f"docker build -f frontend/Dockerfile -t {self.config['docker_registry']}/your-program-frontend:plugin-monitoring-{self.environment} ./frontend"
            )
            
            if not success:
                self.log_step("Build Frontend Image", "FAILED", error=output)
                return False
            
            self.log_step("Build Frontend Image", "PASSED", "Frontend image built successfully")
            
            return True
            
        except Exception as e:
            self.log_step("Build Docker Images", "FAILED", error=str(e))
            return False
    
    def push_docker_images(self):
        """Docker 이미지 푸시"""
        try:
            # 백엔드 이미지 푸시
            success, output = self.run_command(
                f"docker push {self.config['docker_registry']}/your-program-backend:plugin-monitoring-{self.environment}"
            )
            
            if not success:
                self.log_step("Push Backend Image", "FAILED", error=output)
                return False
            
            self.log_step("Push Backend Image", "PASSED", "Backend image pushed successfully")
            
            # 프론트엔드 이미지 푸시
            success, output = self.run_command(
                f"docker push {self.config['docker_registry']}/your-program-frontend:plugin-monitoring-{self.environment}"
            )
            
            if not success:
                self.log_step("Push Frontend Image", "FAILED", error=output)
                return False
            
            self.log_step("Push Frontend Image", "PASSED", "Frontend image pushed successfully")
            
            return True
            
        except Exception as e:
            self.log_step("Push Docker Images", "FAILED", error=str(e))
            return False
    
    def deploy_to_kubernetes(self):
        """Kubernetes 배포"""
        try:
            # 네임스페이스 확인/생성
            success, output = self.run_command(
                f"kubectl get namespace {self.config['namespace']} || kubectl create namespace {self.config['namespace']}"
            )
            
            if not success:
                self.log_step("Create Namespace", "FAILED", error=output)
                return False
            
            self.log_step("Create Namespace", "PASSED", f"Namespace {self.config['namespace']} ready")
            
            # 시크릿 적용
            success, output = self.run_command(
                f"kubectl apply -f kubernetes/secrets/ -n {self.config['namespace']}"
            )
            
            if not success:
                self.log_step("Apply Secrets", "FAILED", error=output)
                return False
            
            self.log_step("Apply Secrets", "PASSED", "Secrets applied successfully")
            
            # 플러그인 모니터링 배포
            success, output = self.run_command(
                f"kubectl apply -f kubernetes/deployments/plugin-monitoring-deployment.yaml -n {self.config['namespace']}"
            )
            
            if not success:
                self.log_step("Deploy Plugin Monitoring", "FAILED", error=output)
                return False
            
            self.log_step("Deploy Plugin Monitoring", "PASSED", "Plugin monitoring deployed successfully")
            
            # 서비스 적용
            success, output = self.run_command(
                f"kubectl apply -f kubernetes/services/ -n {self.config['namespace']}"
            )
            
            if not success:
                self.log_step("Apply Services", "FAILED", error=output)
                return False
            
            self.log_step("Apply Services", "PASSED", "Services applied successfully")
            
            return True
            
        except Exception as e:
            self.log_step("Deploy to Kubernetes", "FAILED", error=str(e))
            return False
    
    def wait_for_deployment(self, timeout=600):
        """배포 완료 대기"""
        try:
            print("Waiting for deployment to be ready...")
            
            for i in range(timeout // 10):
                success, output = self.run_command(
                    f"kubectl get pods -n {self.config['namespace']} -l app=plugin-monitoring -o jsonpath='{{.items[*].status.phase}}'"
                )
                
                if success and "Running" in output:
                    self.log_step("Wait for Deployment", "PASSED", "Deployment is ready")
                    return True
                
                time.sleep(10)
                if i % 6 == 0:  # 1분마다 상태 출력
                    print(f"Still waiting... ({i*10}/{timeout}s)")
            
            self.log_step("Wait for Deployment", "FAILED", "Deployment timeout")
            return False
            
        except Exception as e:
            self.log_step("Wait for Deployment", "FAILED", error=str(e))
            return False
    
    def run_health_checks(self):
        """헬스 체크 실행"""
        try:
            # 플러그인 모니터링 헬스 체크
            response = requests.get(f"{self.config['base_url']}/api/admin/plugin-monitoring/health", timeout=30)
            
            if response.status_code == 200:
                self.log_step("Health Check", "PASSED", "Plugin monitoring health check passed")
            else:
                self.log_step("Health Check", "FAILED", f"Health check failed: {response.status_code}")
                return False
            
            # API 엔드포인트 체크
            endpoints = [
                "/api/admin/plugin-monitoring/status",
                "/api/admin/plugin-monitoring/metrics",
                "/api/admin/plugin-monitoring/dashboard"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{self.config['base_url']}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    self.log_step(f"API Check: {endpoint}", "PASSED", "API endpoint accessible")
                else:
                    self.log_step(f"API Check: {endpoint}", "FAILED", f"API failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_step("Health Checks", "FAILED", error=str(e))
            return False
    
    def run_smoke_tests(self):
        """스모크 테스트 실행"""
        try:
            # 플러그인 모니터링 시작 테스트
            response = requests.post(f"{self.config['base_url']}/api/admin/plugin-monitoring/start", timeout=30)
            
            if response.status_code == 200:
                self.log_step("Smoke Test: Start Monitoring", "PASSED", "Monitoring started successfully")
            else:
                self.log_step("Smoke Test: Start Monitoring", "FAILED", f"Start failed: {response.status_code}")
                return False
            
            # 잠시 대기
            time.sleep(5)
            
            # 모니터링 중지 테스트
            response = requests.post(f"{self.config['base_url']}/api/admin/plugin-monitoring/stop", timeout=30)
            
            if response.status_code == 200:
                self.log_step("Smoke Test: Stop Monitoring", "PASSED", "Monitoring stopped successfully")
            else:
                self.log_step("Smoke Test: Stop Monitoring", "FAILED", f"Stop failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_step("Smoke Tests", "FAILED", error=str(e))
            return False
    
    def rollback_deployment(self):
        """배포 롤백"""
        try:
            print("Rolling back deployment...")
            
            success, output = self.run_command(
                f"kubectl rollout undo deployment/plugin-monitoring-system -n {self.config['namespace']}"
            )
            
            if success:
                self.log_step("Rollback", "PASSED", "Deployment rolled back successfully")
                return True
            else:
                self.log_step("Rollback", "FAILED", error=output)
                return False
                
        except Exception as e:
            self.log_step("Rollback", "FAILED", error=str(e))
            return False
    
    def save_deployment_log(self):
        """배포 로그 저장"""
        try:
            log_file = f"deployment-log-{self.environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.deployment_log, f, indent=2, ensure_ascii=False)
            
            print(f"Deployment log saved to: {log_file}")
            return True
            
        except Exception as e:
            print(f"Failed to save deployment log: {e}")
            return False
    
    def deploy(self):
        """전체 배포 프로세스"""
        print(f"Starting plugin monitoring deployment to {self.environment}...")
        print("="*60)
        
        try:
            # 1. Docker 이미지 빌드
            if not self.build_docker_images():
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 2. Docker 이미지 푸시
            if not self.push_docker_images():
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 3. Kubernetes 배포
            if not self.deploy_to_kubernetes():
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 4. 배포 완료 대기
            if not self.wait_for_deployment():
                self.log_step("Rollback", "INFO", "Deployment failed, attempting rollback")
                self.rollback_deployment()
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 5. 헬스 체크
            if not self.run_health_checks():
                self.log_step("Rollback", "INFO", "Health checks failed, attempting rollback")
                self.rollback_deployment()
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 6. 스모크 테스트
            if not self.run_smoke_tests():
                self.log_step("Rollback", "INFO", "Smoke tests failed, attempting rollback")
                self.rollback_deployment()
                self.deployment_log["status"] = "FAILED"
                self.save_deployment_log()
                return False
            
            # 배포 성공
            self.deployment_log["status"] = "SUCCESS"
            self.save_deployment_log()
            
            print("\n" + "="*60)
            print("✅ Plugin monitoring deployment completed successfully!")
            print(f"Environment: {self.environment}")
            print(f"Base URL: {self.config['base_url']}")
            print("="*60)
            
            return True
            
        except Exception as e:
            self.log_step("Deployment Process", "FAILED", error=str(e))
            self.deployment_log["status"] = "FAILED"
            self.save_deployment_log()
            return False

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy plugin monitoring system")
    parser.add_argument("--environment", choices=["staging", "production"], default="staging",
                       help="Deployment environment")
    parser.add_argument("--skip-build", action="store_true", help="Skip Docker build step")
    parser.add_argument("--skip-push", action="store_true", help="Skip Docker push step")
    
    args = parser.parse_args()
    
    deployer = PluginMonitoringDeployer(args.environment)
    success = deployer.deploy()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 

