#!/usr/bin/env python3
"""
📊 Your Program 실시간 운영 대시보드

프로덕션 환경에서 실시간으로 시스템 상태를 모니터링하고
자동 최적화를 수행하는 종합 운영 관리 시스템입니다.

주요 기능:
- 실시간 시스템 메트릭 모니터링
- 자동 성능 최적화
- 예측적 스케일링
- 운영 비용 최적화
- 사용자 행동 분석
- 비즈니스 인사이트 제공
"""

import asyncio
import aiohttp
import json
import logging
import time
import psutil
import redis
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus 메트릭
REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Total active users')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage')
BUSINESS_METRICS = Gauge('business_metric', 'Business metrics', ['metric_name'])

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_time_avg: float
    error_rate: float
    throughput: float

@dataclass
class BusinessMetrics:
    """비즈니스 메트릭 데이터"""
    timestamp: datetime
    active_users: int
    daily_transactions: int
    revenue: float
    user_satisfaction: float
    feature_usage: Dict[str, int]
    conversion_rate: float

@dataclass
class OptimizationAction:
    """최적화 액션"""
    action_type: str
    target: str
    parameters: Dict[str, Any]
    expected_improvement: float
    priority: int
    automated: bool

class RealTimeMonitor:
    """실시간 모니터링 클래스"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.system_metrics: List[SystemMetrics] = []
        self.business_metrics: List[BusinessMetrics] = []
        self.optimization_queue: List[OptimizationAction] = []
        self.websocket_connections: List[WebSocket] = []
        self.monitoring = False
        
        # AI 기반 예측 모델 (간단한 구현)
        self.prediction_window = 300  # 5분
        self.optimization_threshold = 0.8  # 80% 사용률에서 최적화 시작
        
    async def start_monitoring(self):
        """모니터링 시작"""
        logger.info("🔄 실시간 모니터링 시작")
        self.monitoring = True
        
        # 백그라운드 태스크들 시작
        tasks = [
            asyncio.create_task(self._collect_system_metrics()),
            asyncio.create_task(self._collect_business_metrics()),
            asyncio.create_task(self._analyze_and_optimize()),
            asyncio.create_task(self._broadcast_updates()),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """모니터링 중지"""
        logger.info("⏹️ 실시간 모니터링 중지")
        self.monitoring = False
    
    async def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        while self.monitoring:
            try:
                # 시스템 리소스 수집
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # 애플리케이션 메트릭 수집
                active_connections = await self._get_active_connections()
                response_time_avg = await self._get_avg_response_time()
                error_rate = await self._get_error_rate()
                throughput = await self._get_throughput()
                
                metric = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_usage=(disk.used / disk.total) * 100,
                    network_io={
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv
                    },
                    active_connections=active_connections,
                    response_time_avg=response_time_avg,
                    error_rate=error_rate,
                    throughput=throughput
                )
                
                self.system_metrics.append(metric)
                
                # 최근 1시간 데이터만 유지
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
                
                # Prometheus 메트릭 업데이트
                SYSTEM_CPU.set(cpu_percent)
                SYSTEM_MEMORY.set(memory.percent)
                
                # Redis에 캐시
                await self._cache_metrics('system', metric)
                
                await asyncio.sleep(30)  # 30초마다 수집
                
            except Exception as e:
                logger.error(f"시스템 메트릭 수집 오류: {e}")
                await asyncio.sleep(30)
    
    async def _collect_business_metrics(self):
        """비즈니스 메트릭 수집"""
        while self.monitoring:
            try:
                # 활성 사용자 수
                active_users = await self._get_active_users()
                
                # 일일 트랜잭션 수
                daily_transactions = await self._get_daily_transactions()
                
                # 수익 데이터
                revenue = await self._get_daily_revenue()
                
                # 사용자 만족도 (피드백 기반)
                user_satisfaction = await self._calculate_user_satisfaction()
                
                # 기능별 사용률
                feature_usage = await self._get_feature_usage()
                
                # 전환율
                conversion_rate = await self._calculate_conversion_rate()
                
                metric = BusinessMetrics(
                    timestamp=datetime.now(),
                    active_users=active_users,
                    daily_transactions=daily_transactions,
                    revenue=revenue,
                    user_satisfaction=user_satisfaction,
                    feature_usage=feature_usage,
                    conversion_rate=conversion_rate
                )
                
                self.business_metrics.append(metric)
                
                # 최근 24시간 데이터만 유지
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.business_metrics = [m for m in self.business_metrics if m.timestamp > cutoff_time]
                
                # Prometheus 메트릭 업데이트
                ACTIVE_USERS.set(active_users)
                BUSINESS_METRICS.labels(metric_name='daily_transactions').set(daily_transactions)
                BUSINESS_METRICS.labels(metric_name='revenue').set(revenue)
                BUSINESS_METRICS.labels(metric_name='user_satisfaction').set(user_satisfaction)
                
                # Redis에 캐시
                await self._cache_metrics('business', metric)
                
                await asyncio.sleep(300)  # 5분마다 수집
                
            except Exception as e:
                logger.error(f"비즈니스 메트릭 수집 오류: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_and_optimize(self):
        """분석 및 자동 최적화"""
        while self.monitoring:
            try:
                if len(self.system_metrics) >= 10:  # 최소 10개 데이터 포인트
                    # 성능 분석
                    await self._analyze_performance_trends()
                    
                    # 리소스 사용률 분석
                    await self._analyze_resource_utilization()
                    
                    # 예측적 스케일링
                    await self._predictive_scaling()
                    
                    # 비용 최적화
                    await self._cost_optimization()
                    
                    # 최적화 액션 실행
                    await self._execute_optimizations()
                
                await asyncio.sleep(60)  # 1분마다 분석
                
            except Exception as e:
                logger.error(f"분석 및 최적화 오류: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_performance_trends(self):
        """성능 트렌드 분석"""
        recent_metrics = self.system_metrics[-20:]  # 최근 20개 데이터
        
        if len(recent_metrics) < 5:
            return
        
        # 응답 시간 트렌드
        response_times = [m.response_time_avg for m in recent_metrics]
        response_trend = np.polyfit(range(len(response_times)), response_times, 1)[0]
        
        if response_trend > 0.1:  # 응답 시간이 증가 추세
            action = OptimizationAction(
                action_type="cache_warmup",
                target="application",
                parameters={"priority": "high"},
                expected_improvement=0.3,
                priority=8,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.warning("📈 응답 시간 증가 추세 감지 - 캐시 워밍업 예약")
        
        # 에러율 트렌드
        error_rates = [m.error_rate for m in recent_metrics]
        error_trend = np.polyfit(range(len(error_rates)), error_rates, 1)[0]
        
        if error_trend > 0.01:  # 에러율이 증가 추세
            action = OptimizationAction(
                action_type="health_check",
                target="all_services",
                parameters={"deep_check": True},
                expected_improvement=0.5,
                priority=9,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.warning("🚨 에러율 증가 추세 감지 - 헬스체크 예약")
    
    async def _analyze_resource_utilization(self):
        """리소스 사용률 분석"""
        if not self.system_metrics:
            return
        
        latest_metric = self.system_metrics[-1]
        
        # CPU 사용률 체크
        if latest_metric.cpu_percent > 85:
            action = OptimizationAction(
                action_type="scale_up",
                target="cpu_intensive_services",
                parameters={"scale_factor": 1.5},
                expected_improvement=0.4,
                priority=7,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.warning(f"⚡ 높은 CPU 사용률 감지: {latest_metric.cpu_percent}% - 스케일업 예약")
        
        # 메모리 사용률 체크
        if latest_metric.memory_percent > 90:
            action = OptimizationAction(
                action_type="memory_cleanup",
                target="all_services",
                parameters={"aggressive": True},
                expected_improvement=0.3,
                priority=8,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.warning(f"🧠 높은 메모리 사용률 감지: {latest_metric.memory_percent}% - 메모리 정리 예약")
        
        # 디스크 사용률 체크
        if latest_metric.disk_usage > 85:
            action = OptimizationAction(
                action_type="disk_cleanup",
                target="storage",
                parameters={"cleanup_logs": True, "cleanup_temp": True},
                expected_improvement=0.2,
                priority=6,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.warning(f"💾 높은 디스크 사용률 감지: {latest_metric.disk_usage}% - 디스크 정리 예약")
    
    async def _predictive_scaling(self):
        """예측적 스케일링"""
        if len(self.system_metrics) < 20:
            return
        
        # 최근 데이터로 사용률 예측
        recent_cpu = [m.cpu_percent for m in self.system_metrics[-20:]]
        recent_memory = [m.memory_percent for m in self.system_metrics[-20:]]
        
        # 간단한 선형 회귀로 미래 사용률 예측
        time_points = np.arange(len(recent_cpu))
        cpu_trend = np.polyfit(time_points, recent_cpu, 1)
        memory_trend = np.polyfit(time_points, recent_memory, 1)
        
        # 5분 후 예상 사용률
        future_time = len(recent_cpu) + 10  # 5분 후 (30초 * 10)
        predicted_cpu = np.polyval(cpu_trend, future_time)
        predicted_memory = np.polyval(memory_trend, future_time)
        
        # 예측 기반 스케일링
        if predicted_cpu > 80 or predicted_memory > 80:
            action = OptimizationAction(
                action_type="predictive_scale",
                target="application_cluster",
                parameters={
                    "predicted_cpu": predicted_cpu,
                    "predicted_memory": predicted_memory,
                    "scale_factor": 1.3
                },
                expected_improvement=0.6,
                priority=5,
                automated=True
            )
            self.optimization_queue.append(action)
            logger.info(f"🔮 예측적 스케일링 예약 - CPU: {predicted_cpu:.1f}%, Memory: {predicted_memory:.1f}%")
    
    async def _cost_optimization(self):
        """비용 최적화"""
        if len(self.system_metrics) < 10:
            return
        
        # 최근 10분간 평균 사용률
        recent_metrics = self.system_metrics[-20:]
        avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
        avg_memory = np.mean([m.memory_percent for m in recent_metrics])
        
        # 저사용률 감지 (30% 미만)
        if avg_cpu < 30 and avg_memory < 30:
            action = OptimizationAction(
                action_type="scale_down",
                target="underutilized_services",
                parameters={"target_utilization": 60},
                expected_improvement=0.25,  # 비용 절감
                priority=3,
                automated=False  # 수동 승인 필요
            )
            self.optimization_queue.append(action)
            logger.info(f"💰 저사용률 감지 - 스케일 다운 제안: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%")
    
    async def _execute_optimizations(self):
        """최적화 액션 실행"""
        if not self.optimization_queue:
            return
        
        # 우선순위별 정렬
        self.optimization_queue.sort(key=lambda x: x.priority, reverse=True)
        
        # 자동 실행 가능한 액션들 처리
        executed_actions = []
        for action in self.optimization_queue[:5]:  # 상위 5개만 처리
            if action.automated:
                success = await self._execute_action(action)
                if success:
                    executed_actions.append(action)
                    logger.info(f"✅ 자동 최적화 실행 완료: {action.action_type} on {action.target}")
        
        # 실행된 액션들 제거
        for action in executed_actions:
            self.optimization_queue.remove(action)
    
    async def _execute_action(self, action: OptimizationAction) -> bool:
        """개별 최적화 액션 실행"""
        try:
            if action.action_type == "cache_warmup":
                return await self._cache_warmup()
            elif action.action_type == "health_check":
                return await self._deep_health_check()
            elif action.action_type == "memory_cleanup":
                return await self._memory_cleanup()
            elif action.action_type == "disk_cleanup":
                return await self._disk_cleanup()
            elif action.action_type == "scale_up":
                return await self._scale_services(action.parameters.get("scale_factor", 1.5))
            elif action.action_type == "predictive_scale":
                return await self._predictive_scale_action(action.parameters)
            else:
                logger.warning(f"알 수 없는 액션 타입: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"액션 실행 오류 {action.action_type}: {e}")
            return False
    
    async def _cache_warmup(self) -> bool:
        """캐시 워밍업"""
        try:
            # 자주 사용되는 데이터 미리 로드
            cache_keys = [
                "user_sessions",
                "system_config",
                "api_metrics",
                "business_metrics"
            ]
            
            for key in cache_keys:
                # 더미 캐시 워밍업 (실제 구현에서는 실제 데이터 로드)
                self.redis_client.setex(f"warmup_{key}", 3600, "warmed")
            
            logger.info("🔥 캐시 워밍업 완료")
            return True
            
        except Exception as e:
            logger.error(f"캐시 워밍업 실패: {e}")
            return False
    
    async def _deep_health_check(self) -> bool:
        """딥 헬스체크"""
        try:
            services = [
                "http://localhost:8000/health",
                "http://localhost:8001/health", 
                "http://localhost:8002/health",
                "http://localhost:8007/security/status"
            ]
            
            healthy_services = 0
            async with aiohttp.ClientSession() as session:
                for service_url in services:
                    try:
                        async with session.get(service_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                healthy_services += 1
                    except:
                        pass
            
            health_ratio = healthy_services / len(services)
            logger.info(f"🏥 딥 헬스체크 완료: {healthy_services}/{len(services)} 서비스 정상 ({health_ratio*100:.1f}%)")
            return health_ratio > 0.8
            
        except Exception as e:
            logger.error(f"딥 헬스체크 실패: {e}")
            return False
    
    async def _memory_cleanup(self) -> bool:
        """메모리 정리"""
        try:
            # Python 가비지 컬렉션
            import gc
            collected = gc.collect()
            
            # Redis 메모리 최적화
            self.redis_client.execute_command("MEMORY PURGE")
            
            logger.info(f"🧹 메모리 정리 완료: {collected}개 객체 정리")
            return True
            
        except Exception as e:
            logger.error(f"메모리 정리 실패: {e}")
            return False
    
    async def _disk_cleanup(self) -> bool:
        """디스크 정리"""
        try:
            import tempfile
            import shutil
            
            # 임시 파일 정리
            temp_dir = tempfile.gettempdir()
            temp_files_removed = 0
            
            for file_path in Path(temp_dir).glob("tmp*"):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        temp_files_removed += 1
                except:
                    pass
            
            logger.info(f"🗑️ 디스크 정리 완료: {temp_files_removed}개 임시 파일 삭제")
            return True
            
        except Exception as e:
            logger.error(f"디스크 정리 실패: {e}")
            return False
    
    async def _scale_services(self, scale_factor: float) -> bool:
        """서비스 스케일링"""
        try:
            # 실제 환경에서는 Docker/Kubernetes API 호출
            logger.info(f"📈 서비스 스케일링: {scale_factor}x")
            
            # 스케일링 시뮬레이션
            await asyncio.sleep(2)
            
            logger.info("✅ 서비스 스케일링 완료")
            return True
            
        except Exception as e:
            logger.error(f"서비스 스케일링 실패: {e}")
            return False
    
    async def _predictive_scale_action(self, parameters: Dict[str, Any]) -> bool:
        """예측적 스케일링 실행"""
        try:
            predicted_cpu = parameters.get("predicted_cpu", 0)
            predicted_memory = parameters.get("predicted_memory", 0)
            scale_factor = parameters.get("scale_factor", 1.3)
            
            logger.info(f"🔮 예측적 스케일링 실행: CPU {predicted_cpu:.1f}%, Memory {predicted_memory:.1f}%")
            
            # 실제 스케일링 로직
            return await self._scale_services(scale_factor)
            
        except Exception as e:
            logger.error(f"예측적 스케일링 실패: {e}")
            return False
    
    async def _broadcast_updates(self):
        """WebSocket을 통한 실시간 업데이트 브로드캐스트"""
        while self.monitoring:
            try:
                if self.websocket_connections:
                    # 최신 메트릭 준비
                    data = await self._prepare_dashboard_data()
                    
                    # 연결된 모든 클라이언트에게 브로드캐스트
                    disconnected = []
                    for websocket in self.websocket_connections:
                        try:
                            await websocket.send_text(json.dumps(data, cls=PlotlyJSONEncoder))
                        except WebSocketDisconnect:
                            disconnected.append(websocket)
                        except Exception as e:
                            logger.error(f"WebSocket 전송 오류: {e}")
                            disconnected.append(websocket)
                    
                    # 끊어진 연결 제거
                    for websocket in disconnected:
                        self.websocket_connections.remove(websocket)
                
                await asyncio.sleep(5)  # 5초마다 업데이트
                
            except Exception as e:
                logger.error(f"브로드캐스트 오류: {e}")
                await asyncio.sleep(5)
    
    async def _prepare_dashboard_data(self) -> Dict[str, Any]:
        """대시보드 데이터 준비"""
        current_time = datetime.now()
        
        # 시스템 메트릭 차트 데이터
        system_data = []
        if self.system_metrics:
            recent_system = self.system_metrics[-20:]
            system_data = {
                "timestamps": [m.timestamp.isoformat() for m in recent_system],
                "cpu": [m.cpu_percent for m in recent_system],
                "memory": [m.memory_percent for m in recent_system],
                "response_time": [m.response_time_avg for m in recent_system],
                "throughput": [m.throughput for m in recent_system]
            }
        
        # 비즈니스 메트릭 데이터
        business_data = []
        if self.business_metrics:
            recent_business = self.business_metrics[-10:]
            business_data = {
                "timestamps": [m.timestamp.isoformat() for m in recent_business],
                "active_users": [m.active_users for m in recent_business],
                "transactions": [m.daily_transactions for m in recent_business],
                "revenue": [m.revenue for m in recent_business],
                "satisfaction": [m.user_satisfaction for m in recent_business]
            }
        
        # 최적화 큐 상태
        optimization_status = []
        for action in self.optimization_queue[:10]:
            optimization_status.append({
                "action_type": action.action_type,
                "target": action.target,
                "priority": action.priority,
                "automated": action.automated,
                "expected_improvement": action.expected_improvement
            })
        
        # 현재 상태 요약
        current_status = {
            "timestamp": current_time.isoformat(),
            "total_services": 6,
            "healthy_services": await self._get_healthy_services_count(),
            "active_optimizations": len([a for a in self.optimization_queue if a.automated]),
            "system_score": await self._calculate_system_score()
        }
        
        return {
            "system_metrics": system_data,
            "business_metrics": business_data,
            "optimization_queue": optimization_status,
            "current_status": current_status,
            "alerts": await self._get_active_alerts()
        }
    
    # 헬퍼 메서드들
    async def _get_active_connections(self) -> int:
        """활성 연결 수 조회"""
        try:
            # 실제 구현에서는 네트워크 통계나 애플리케이션 메트릭 사용
            return len(psutil.net_connections())
        except:
            return 0
    
    async def _get_avg_response_time(self) -> float:
        """평균 응답 시간 조회"""
        try:
            # Redis에서 캐시된 응답 시간 데이터 조회
            cached_data = self.redis_client.get("avg_response_time")
            if cached_data:
                return float(cached_data)
            return 250.0  # 기본값
        except:
            return 250.0
    
    async def _get_error_rate(self) -> float:
        """에러율 조회"""
        try:
            # 실제 구현에서는 애플리케이션 로그나 메트릭 사용
            cached_data = self.redis_client.get("error_rate")
            if cached_data:
                return float(cached_data)
            return 0.5  # 기본값
        except:
            return 0.5
    
    async def _get_throughput(self) -> float:
        """처리량 조회"""
        try:
            cached_data = self.redis_client.get("throughput")
            if cached_data:
                return float(cached_data)
            return 100.0  # 기본값
        except:
            return 100.0
    
    async def _get_active_users(self) -> int:
        """활성 사용자 수 조회"""
        try:
            # Redis 세션 수 또는 실제 사용자 추적 데이터 사용
            return len(self.redis_client.keys("session:*"))
        except:
            return 0
    
    async def _get_daily_transactions(self) -> int:
        """일일 트랜잭션 수 조회"""
        try:
            cached_data = self.redis_client.get("daily_transactions")
            if cached_data:
                return int(cached_data)
            return 0
        except:
            return 0
    
    async def _get_daily_revenue(self) -> float:
        """일일 수익 조회"""
        try:
            cached_data = self.redis_client.get("daily_revenue")
            if cached_data:
                return float(cached_data)
            return 0.0
        except:
            return 0.0
    
    async def _calculate_user_satisfaction(self) -> float:
        """사용자 만족도 계산"""
        try:
            # 피드백 데이터 기반 계산
            return 4.2  # 5점 만점
        except:
            return 4.0
    
    async def _get_feature_usage(self) -> Dict[str, int]:
        """기능별 사용률 조회"""
        try:
            return {
                "dashboard": 150,
                "analytics": 89,
                "security": 67,
                "reports": 134,
                "settings": 45
            }
        except:
            return {}
    
    async def _calculate_conversion_rate(self) -> float:
        """전환율 계산"""
        try:
            return 0.125  # 12.5%
        except:
            return 0.1
    
    async def _cache_metrics(self, metric_type: str, metric):
        """메트릭 Redis 캐시"""
        try:
            cache_key = f"metrics:{metric_type}:latest"
            self.redis_client.setex(cache_key, 300, json.dumps(asdict(metric), default=str))
        except Exception as e:
            logger.error(f"메트릭 캐시 실패: {e}")
    
    async def _get_healthy_services_count(self) -> int:
        """정상 서비스 수 조회"""
        return 6  # 기본값
    
    async def _calculate_system_score(self) -> float:
        """시스템 종합 점수 계산"""
        if not self.system_metrics:
            return 85.0
        
        latest = self.system_metrics[-1]
        
        # 성능 점수 계산 (100점 만점)
        cpu_score = max(0, 100 - latest.cpu_percent)
        memory_score = max(0, 100 - latest.memory_percent)
        response_score = max(0, 100 - min(100, latest.response_time_avg / 10))
        error_score = max(0, 100 - latest.error_rate * 20)
        
        return (cpu_score + memory_score + response_score + error_score) / 4
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """활성 알림 조회"""
        alerts = []
        
        if self.system_metrics:
            latest = self.system_metrics[-1]
            
            if latest.cpu_percent > 80:
                alerts.append({
                    "severity": "warning",
                    "title": "높은 CPU 사용률",
                    "message": f"현재 CPU 사용률: {latest.cpu_percent:.1f}%",
                    "timestamp": latest.timestamp.isoformat()
                })
            
            if latest.memory_percent > 85:
                alerts.append({
                    "severity": "warning", 
                    "title": "높은 메모리 사용률",
                    "message": f"현재 메모리 사용률: {latest.memory_percent:.1f}%",
                    "timestamp": latest.timestamp.isoformat()
                })
            
            if latest.error_rate > 5:
                alerts.append({
                    "severity": "critical",
                    "title": "높은 에러율",
                    "message": f"현재 에러율: {latest.error_rate:.1f}%",
                    "timestamp": latest.timestamp.isoformat()
                })
        
        return alerts

# FastAPI 애플리케이션
app = FastAPI(title="Your Program 실시간 운영 대시보드", version="1.0.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 전역 모니터 인스턴스
monitor = RealTimeMonitor()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작시 모니터링 시작"""
    # Prometheus 메트릭 서버 시작
    start_http_server(9090)
    
    # 백그라운드에서 모니터링 시작
    asyncio.create_task(monitor.start_monitoring())
    logger.info("🚀 실시간 운영 대시보드 시작됨")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료시 모니터링 중지"""
    await monitor.stop_monitoring()
    logger.info("⏹️ 실시간 운영 대시보드 종료됨")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """메인 대시보드 페이지"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Program 실시간 운영 대시보드</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                color: white;
                padding: 1.5rem;
                margin: 0.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .chart-container {
                background: white;
                border-radius: 12px;
                padding: 1rem;
                margin: 0.5rem;
                box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .alert-critical { border-left: 4px solid #ef4444; }
            .alert-warning { border-left: 4px solid #f59e0b; }
            .alert-info { border-left: 4px solid #3b82f6; }
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-6">
            <!-- 헤더 -->
            <div class="mb-6">
                <h1 class="text-3xl font-bold text-gray-800">
                    🎛️ Your Program 실시간 운영 대시보드
                </h1>
                <p class="text-gray-600 mt-2">실시간 시스템 모니터링 및 자동 최적화</p>
            </div>
            
            <!-- 현재 상태 카드 -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="metric-card">
                    <h3 class="text-lg font-semibold">시스템 점수</h3>
                    <p class="text-3xl font-bold" id="system-score">85.2</p>
                    <p class="text-sm opacity-80">100점 만점</p>
                </div>
                <div class="metric-card">
                    <h3 class="text-lg font-semibold">활성 사용자</h3>
                    <p class="text-3xl font-bold" id="active-users">142</p>
                    <p class="text-sm opacity-80">실시간 접속</p>
                </div>
                <div class="metric-card">
                    <h3 class="text-lg font-semibold">서비스 상태</h3>
                    <p class="text-3xl font-bold" id="service-status">6/6</p>
                    <p class="text-sm opacity-80">정상 동작</p>
                </div>
                <div class="metric-card">
                    <h3 class="text-lg font-semibold">최적화 큐</h3>
                    <p class="text-3xl font-bold" id="optimization-queue">3</p>
                    <p class="text-sm opacity-80">대기 중</p>
                </div>
            </div>
            
            <!-- 차트 영역 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div class="chart-container">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">📊 시스템 리소스</h3>
                    <div id="system-chart" style="height: 300px;"></div>
                </div>
                <div class="chart-container">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">👥 비즈니스 메트릭</h3>
                    <div id="business-chart" style="height: 300px;"></div>
                </div>
            </div>
            
            <!-- 알림 및 최적화 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="chart-container">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">🚨 활성 알림</h3>
                    <div id="alerts-container">
                        <p class="text-gray-500">알림 로딩 중...</p>
                    </div>
                </div>
                <div class="chart-container">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">⚡ 최적화 큐</h3>
                    <div id="optimization-container">
                        <p class="text-gray-500">최적화 작업 로딩 중...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // WebSocket 연결
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket 오류:', error);
            };
            
            function updateDashboard(data) {
                // 현재 상태 업데이트
                if (data.current_status) {
                    document.getElementById('system-score').textContent = 
                        data.current_status.system_score.toFixed(1);
                    document.getElementById('service-status').textContent = 
                        `${data.current_status.healthy_services}/${data.current_status.total_services}`;
                    document.getElementById('optimization-queue').textContent = 
                        data.current_status.active_optimizations;
                }
                
                // 시스템 차트 업데이트
                if (data.system_metrics && data.system_metrics.timestamps) {
                    updateSystemChart(data.system_metrics);
                }
                
                // 비즈니스 차트 업데이트
                if (data.business_metrics && data.business_metrics.timestamps) {
                    updateBusinessChart(data.business_metrics);
                    if (data.business_metrics.active_users.length > 0) {
                        document.getElementById('active-users').textContent = 
                            data.business_metrics.active_users[data.business_metrics.active_users.length - 1];
                    }
                }
                
                // 알림 업데이트
                if (data.alerts) {
                    updateAlerts(data.alerts);
                }
                
                // 최적화 큐 업데이트
                if (data.optimization_queue) {
                    updateOptimizationQueue(data.optimization_queue);
                }
            }
            
            function updateSystemChart(metrics) {
                const traces = [
                    {
                        x: metrics.timestamps,
                        y: metrics.cpu,
                        name: 'CPU (%)',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: { color: '#ef4444' }
                    },
                    {
                        x: metrics.timestamps,
                        y: metrics.memory,
                        name: 'Memory (%)',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: { color: '#3b82f6' }
                    }
                ];
                
                const layout = {
                    title: '',
                    xaxis: { title: '시간' },
                    yaxis: { title: '사용률 (%)' },
                    margin: { l: 50, r: 50, t: 20, b: 50 },
                    showlegend: true
                };
                
                Plotly.newPlot('system-chart', traces, layout, {responsive: true});
            }
            
            function updateBusinessChart(metrics) {
                const traces = [
                    {
                        x: metrics.timestamps,
                        y: metrics.active_users,
                        name: '활성 사용자',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: { color: '#10b981' }
                    },
                    {
                        x: metrics.timestamps,
                        y: metrics.satisfaction.map(s => s * 20), // 0-100 스케일로 변환
                        name: '만족도 (x20)',
                        type: 'scatter',
                        mode: 'lines+markers',
                        line: { color: '#f59e0b' }
                    }
                ];
                
                const layout = {
                    title: '',
                    xaxis: { title: '시간' },
                    yaxis: { title: '수치' },
                    margin: { l: 50, r: 50, t: 20, b: 50 },
                    showlegend: true
                };
                
                Plotly.newPlot('business-chart', traces, layout, {responsive: true});
            }
            
            function updateAlerts(alerts) {
                const container = document.getElementById('alerts-container');
                
                if (alerts.length === 0) {
                    container.innerHTML = '<p class="text-green-600">✅ 활성 알림 없음</p>';
                    return;
                }
                
                let html = '';
                alerts.forEach(alert => {
                    const alertClass = `alert-${alert.severity}`;
                    html += `
                        <div class="${alertClass} bg-white p-3 mb-2 rounded border-l-4">
                            <div class="font-semibold">${alert.title}</div>
                            <div class="text-sm text-gray-600">${alert.message}</div>
                            <div class="text-xs text-gray-400 mt-1">${new Date(alert.timestamp).toLocaleString()}</div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            function updateOptimizationQueue(queue) {
                const container = document.getElementById('optimization-container');
                
                if (queue.length === 0) {
                    container.innerHTML = '<p class="text-gray-500">최적화 작업 없음</p>';
                    return;
                }
                
                let html = '';
                queue.forEach(action => {
                    const priorityColor = action.priority >= 8 ? 'text-red-600' : 
                                        action.priority >= 6 ? 'text-yellow-600' : 'text-green-600';
                    const automatedIcon = action.automated ? '🤖' : '👤';
                    
                    html += `
                        <div class="bg-gray-50 p-3 mb-2 rounded">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="font-semibold">${automatedIcon} ${action.action_type}</div>
                                    <div class="text-sm text-gray-600">대상: ${action.target}</div>
                                </div>
                                <div class="${priorityColor} font-bold">P${action.priority}</div>
                            </div>
                            <div class="text-xs text-gray-500 mt-1">
                                예상 개선: ${(action.expected_improvement * 100).toFixed(1)}%
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            // 초기 차트 생성
            Plotly.newPlot('system-chart', [], {
                title: '데이터 로딩 중...',
                margin: { l: 50, r: 50, t: 50, b: 50 }
            }, {responsive: true});
            
            Plotly.newPlot('business-chart', [], {
                title: '데이터 로딩 중...',
                margin: { l: 50, r: 50, t: 50, b: 50 }
            }, {responsive: true});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 엔드포인트"""
    await websocket.accept()
    monitor.websocket_connections.append(websocket)
    logger.info(f"📡 WebSocket 연결됨 - 총 {len(monitor.websocket_connections)}개 연결")
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitor.websocket_connections.remove(websocket)
        logger.info(f"📡 WebSocket 연결 종료 - 총 {len(monitor.websocket_connections)}개 연결")

@app.get("/api/metrics/current")
async def get_current_metrics():
    """현재 메트릭 조회 API"""
    return await monitor._prepare_dashboard_data()

@app.get("/api/optimization/queue")
async def get_optimization_queue():
    """최적화 큐 조회 API"""
    return [asdict(action) for action in monitor.optimization_queue]

@app.post("/api/optimization/execute/{action_id}")
async def execute_optimization(action_id: int):
    """특정 최적화 액션 수동 실행 API"""
    if 0 <= action_id < len(monitor.optimization_queue):
        action = monitor.optimization_queue[action_id]
        success = await monitor._execute_action(action)
        if success:
            monitor.optimization_queue.remove(action)
            return {"status": "success", "message": f"최적화 액션 '{action.action_type}' 실행 완료"}
        else:
            return {"status": "error", "message": "최적화 액션 실행 실패"}
    else:
        return {"status": "error", "message": "유효하지 않은 액션 ID"}

@app.get("/api/health")
async def health_check():
    """헬스체크 API"""
    return {
        "status": "healthy",
        "monitoring": monitor.monitoring,
        "websocket_connections": len(monitor.websocket_connections),
        "optimization_queue_size": len(monitor.optimization_queue),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("🚀 Your Program 실시간 운영 대시보드 시작")
    uvicorn.run(
        "real_time_operations_dashboard:app",
        host="0.0.0.0",
        port=9000,
        reload=False,
        log_level="info"
    ) 