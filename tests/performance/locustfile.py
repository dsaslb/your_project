#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플러그인 시스템 성능 테스트 - Locust
API 엔드포인트, 플러그인 로드, 동시 사용자 시뮬레이션을 테스트합니다.
"""

import time
import random
import json
from locust import HttpUser, task, between, events
from locust.exception import StopUser

class PluginSystemUser(HttpUser):
    """플러그인 시스템 사용자 시뮬레이션"""
    
    wait_time = between(1, 3)  # 요청 간 대기 시간
    
    def on_start(self):
        """사용자 시작 시 로그인"""
        try:
            # 관리자 로그인
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.client.post("/auth/login", data=login_data)
            if response.status_code == 200:
                self.log("관리자 로그인 성공")
            else:
                self.log(f"로그인 실패: {response.status_code}")
                
        except Exception as e:
            self.log(f"로그인 중 오류: {e}")
    
    @task(3)
    def get_dashboard(self):
        """대시보드 조회"""
        with self.client.get("/api/dashboard", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"대시보드 조회 실패: {response.status_code}")
    
    @task(2)
    def get_plugins_list(self):
        """플러그인 목록 조회"""
        with self.client.get("/api/plugins/list", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    response.success()
                else:
                    response.failure("플러그인 목록 응답 오류")
            else:
                response.failure(f"플러그인 목록 조회 실패: {response.status_code}")
    
    @task(2)
    def get_plugin_status(self):
        """플러그인 상태 조회"""
        with self.client.get("/api/plugins/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 상태 조회 실패: {response.status_code}")
    
    @task(1)
    def get_plugin_settings(self):
        """플러그인 설정 조회"""
        # 랜덤 플러그인 선택
        plugins = ["core_management", "restaurant_management", "marketplace"]
        plugin_name = random.choice(plugins)
        
        with self.client.get(f"/api/plugin-settings/{plugin_name}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 설정 조회 실패: {response.status_code}")
    
    @task(1)
    def update_plugin_settings(self):
        """플러그인 설정 업데이트"""
        plugins = ["core_management", "restaurant_management"]
        plugin_name = random.choice(plugins)
        
        settings_data = {
            "settings": {
                "enabled": random.choice([True, False]),
                "debug_mode": random.choice([True, False]),
                "log_level": random.choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
                "config": {
                    "max_connections": random.randint(50, 200),
                    "timeout": random.randint(10, 60)
                }
            }
        }
        
        with self.client.post(
            f"/api/plugin-settings/{plugin_name}",
            json=settings_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 설정 업데이트 실패: {response.status_code}")
    
    @task(1)
    def get_plugin_monitoring(self):
        """플러그인 모니터링 데이터 조회"""
        with self.client.get("/api/plugin-monitoring/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 모니터링 조회 실패: {response.status_code}")
    
    @task(1)
    def get_realtime_alerts(self):
        """실시간 알림 조회"""
        with self.client.get("/api/enhanced-alerts/stream", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"실시간 알림 조회 실패: {response.status_code}")
    
    @task(1)
    def get_marketplace_plugins(self):
        """마켓플레이스 플러그인 조회"""
        with self.client.get("/api/marketplace/plugins", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"마켓플레이스 조회 실패: {response.status_code}")

class PluginLoadTester(HttpUser):
    """플러그인 로드 테스트 사용자"""
    
    wait_time = between(5, 10)  # 플러그인 로드는 시간이 걸리므로 대기 시간 증가
    
    @task(1)
    def load_plugin(self):
        """플러그인 로드 테스트"""
        plugins = ["core_management", "restaurant_management", "marketplace"]
        plugin_name = random.choice(plugins)
        
        with self.client.post(
            f"/api/plugins/{plugin_name}/reload",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 로드 실패: {response.status_code}")
    
    @task(1)
    def enable_plugin(self):
        """플러그인 활성화 테스트"""
        plugins = ["core_management", "restaurant_management"]
        plugin_name = random.choice(plugins)
        
        with self.client.post(
            f"/api/plugins/{plugin_name}/enable",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 활성화 실패: {response.status_code}")
    
    @task(1)
    def disable_plugin(self):
        """플러그인 비활성화 테스트"""
        plugins = ["core_management", "restaurant_management"]
        plugin_name = random.choice(plugins)
        
        with self.client.post(
            f"/api/plugins/{plugin_name}/disable",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"플러그인 비활성화 실패: {response.status_code}")

class PluginStressTester(HttpUser):
    """플러그인 스트레스 테스트 사용자"""
    
    wait_time = between(0.1, 0.5)  # 빠른 요청으로 스트레스 테스트
    
    @task(5)
    def rapid_api_calls(self):
        """빠른 API 호출"""
        endpoints = [
            "/api/plugins/list",
            "/api/plugins/status",
            "/api/dashboard",
            "/api/plugin-monitoring/metrics"
        ]
        
        endpoint = random.choice(endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"빠른 API 호출 실패: {response.status_code}")
    
    @task(3)
    def concurrent_settings_updates(self):
        """동시 설정 업데이트"""
        plugins = ["core_management", "restaurant_management"]
        plugin_name = random.choice(plugins)
        
        settings_data = {
            "settings": {
                "enabled": random.choice([True, False]),
                "debug_mode": random.choice([True, False]),
                "log_level": random.choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
                "config": {
                    "max_connections": random.randint(10, 500),
                    "timeout": random.randint(1, 120)
                }
            }
        }
        
        with self.client.post(
            f"/api/plugin-settings/{plugin_name}",
            json=settings_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"동시 설정 업데이트 실패: {response.status_code}")

class PluginIntegrationTester(HttpUser):
    """플러그인 통합 테스트 사용자"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """사용자 시작 시 로그인"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.client.post("/auth/login", data=login_data)
            if response.status_code == 200:
                self.log("관리자 로그인 성공")
            else:
                self.log(f"로그인 실패: {response.status_code}")
                
        except Exception as e:
            self.log(f"로그인 중 오류: {e}")
    
    @task(1)
    def complete_plugin_workflow(self):
        """완전한 플러그인 워크플로우 테스트"""
        try:
            # 1. 플러그인 목록 조회
            response = self.client.get("/api/plugins/list")
            if response.status_code != 200:
                self.log("플러그인 목록 조회 실패")
                return
            
            # 2. 플러그인 설정 조회
            plugin_name = "core_management"
            response = self.client.get(f"/api/plugin-settings/{plugin_name}")
            if response.status_code != 200:
                self.log("플러그인 설정 조회 실패")
                return
            
            # 3. 설정 업데이트
            settings_data = {
                "settings": {
                    "enabled": True,
                    "debug_mode": False,
                    "log_level": "INFO",
                    "config": {
                        "max_connections": 100,
                        "timeout": 30
                    }
                }
            }
            
            response = self.client.post(
                f"/api/plugin-settings/{plugin_name}",
                json=settings_data
            )
            if response.status_code != 200:
                self.log("플러그인 설정 업데이트 실패")
                return
            
            # 4. 플러그인 재로드
            response = self.client.post(f"/api/plugins/{plugin_name}/reload")
            if response.status_code != 200:
                self.log("플러그인 재로드 실패")
                return
            
            # 5. 모니터링 데이터 확인
            response = self.client.get("/api/plugin-monitoring/metrics")
            if response.status_code != 200:
                self.log("모니터링 데이터 조회 실패")
                return
            
            self.log("완전한 플러그인 워크플로우 성공")
            
        except Exception as e:
            self.log(f"플러그인 워크플로우 실패: {e}")

# 성능 메트릭 수집
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """요청 성능 메트릭 수집"""
    if exception:
        print(f"요청 실패: {name} - {exception}")
    else:
        print(f"요청 성공: {name} - {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """테스트 시작 시 호출"""
    print("플러그인 시스템 성능 테스트 시작")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """테스트 종료 시 호출"""
    print("플러그인 시스템 성능 테스트 종료")
    
    # 성능 통계 출력
    stats = environment.stats
    print(f"\n=== 성능 테스트 결과 ===")
    print(f"총 요청 수: {stats.total.num_requests}")
    print(f"실패한 요청 수: {stats.total.num_failures}")
    print(f"평균 응답 시간: {stats.total.avg_response_time:.2f}ms")
    print(f"최대 응답 시간: {stats.total.max_response_time:.2f}ms")
    print(f"최소 응답 시간: {stats.total.min_response_time:.2f}ms")
    print(f"RPS (초당 요청 수): {stats.total.current_rps:.2f}")

# 사용자 클래스 가중치 설정
def get_user_classes():
    """사용자 클래스 및 가중치 반환"""
    return [
        (PluginSystemUser, 60),      # 60% - 일반 사용자
        (PluginLoadTester, 20),      # 20% - 플러그인 로드 테스트
        (PluginStressTester, 15),    # 15% - 스트레스 테스트
        (PluginIntegrationTester, 5) # 5% - 통합 테스트
    ] 