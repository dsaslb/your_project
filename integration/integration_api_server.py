"""
🔄 통합 API 서버

모든 시스템에 대한 중앙화된 API 접근을 제공하는 FastAPI 기반 서버입니다.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
import json
from datetime import datetime
import uvicorn

from system_integration_core import IntegrationManager, SystemStatus

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Your Program 통합 API 서버",
    description="모든 시스템에 대한 중앙화된 API 접근",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델
class ServiceRequest(BaseModel):
    service_name: str
    endpoint: str
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    systems: Dict[str, Dict[str, Any]]
    overall_health: float

class MetricsResponse(BaseModel):
    timestamp: str
    overall_health: float
    total_requests: int
    systems: Dict[str, Dict[str, Any]]

# 전역 변수
integration_manager: Optional[IntegrationManager] = None

# 설정
config = {
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 0,
    'database_url': 'postgresql://localhost/your_program',
    'api_gateway_url': 'http://localhost:8000',
    'ai_ml_url': 'http://localhost:8001',
    'data_analysis_url': 'http://localhost:8002',
    'blockchain_url': 'http://localhost:8003',
    'iot_url': 'http://localhost:8004',
    'security_url': 'http://localhost:8005',
    'mobile_backend_url': 'http://localhost:8006'
}

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    global integration_manager
    logger.info("Starting integration API server...")
    
    integration_manager = IntegrationManager(config)
    await integration_manager.start()
    
    logger.info("Integration API server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    global integration_manager
    logger.info("Shutting down integration API server...")
    
    if integration_manager:
        await integration_manager.stop()
    
    logger.info("Integration API server shutdown complete")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Your Program 통합 API 서버",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """시스템 헬스 체크"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        status = await integration_manager.get_status()
        
        return HealthCheckResponse(
            status="healthy" if status['integration_status'] == 'running' else "unhealthy",
            timestamp=datetime.now().isoformat(),
            systems={
                name: {
                    'status': sys_status.status,
                    'response_time': sys_status.response_time,
                    'last_check': sys_status.last_check.isoformat(),
                    'error_message': sys_status.error_message
                }
                for name, sys_status in status['systems'].items()
            },
            overall_health=status['metrics']['overall_health']
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """시스템 메트릭 조회"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        metrics = await integration_manager.core.get_system_metrics()
        
        return MetricsResponse(
            timestamp=metrics['timestamp'],
            overall_health=metrics['overall_health'],
            total_requests=metrics['total_requests'],
            systems=metrics['systems']
        )
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/route")
async def route_request(request: ServiceRequest):
    """서비스 요청 라우팅"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        result = await integration_manager.core.route_request(
            service_name=request.service_name,
            endpoint=request.endpoint,
            method=request.method,
            data=request.data
        )
        
        if result['success']:
            return JSONResponse(
                content=result,
                status_code=200
            )
        else:
            return JSONResponse(
                content=result,
                status_code=500
            )
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services")
async def list_services():
    """사용 가능한 서비스 목록"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    services = {}
    for name, config in integration_manager.core.integrated_services.items():
        services[name] = {
            'url': config['url'],
            'health_endpoint': config['health_endpoint'],
            'weight': config['weight']
        }
    
    return {
        'services': services,
        'total_count': len(services),
        'timestamp': datetime.now().isoformat()
    }

@app.get("/services/{service_name}/status")
async def get_service_status(service_name: str):
    """특정 서비스 상태 조회"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    if service_name not in integration_manager.core.system_status:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    status = integration_manager.core.system_status[service_name]
    
    return {
        'service_name': service_name,
        'status': status.status,
        'response_time': status.response_time,
        'last_check': status.last_check.isoformat(),
        'error_message': status.error_message,
        'timestamp': datetime.now().isoformat()
    }

@app.post("/services/{service_name}/health-check")
async def check_service_health(service_name: str, background_tasks: BackgroundTasks):
    """특정 서비스 헬스 체크 실행"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    if service_name not in integration_manager.core.integrated_services:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    try:
        # 백그라운드에서 헬스 체크 실행
        background_tasks.add_task(
            integration_manager.core.check_system_health, 
            service_name
        )
        
        return {
            'message': f"Health check initiated for {service_name}",
            'service_name': service_name,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check initiation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/{key}")
async def get_cached_data(key: str):
    """캐시된 데이터 조회"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        data = await integration_manager.core.get_cached_data(key)
        
        if data is None:
            raise HTTPException(status_code=404, detail=f"Cache key {key} not found")
        
        return {
            'key': key,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cache/{key}")
async def set_cached_data(key: str, data: Dict[str, Any], ttl: int = 3600):
    """데이터 캐시 저장"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        success = await integration_manager.core.cache_data(key, data, ttl)
        
        if success:
            return {
                'message': f"Data cached successfully with key {key}",
                'key': key,
                'ttl': ttl,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to cache data")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache storage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_integration_logs(limit: int = 100, event_type: Optional[str] = None):
    """통합 로그 조회"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        # PostgreSQL에서 로그 조회
        with integration_manager.core.db_engine.connect() as conn:
            query = """
                SELECT timestamp, event_type, details
                FROM integration_logs
                WHERE 1=1
            """
            params = {}
            
            if event_type:
                query += " AND event_type = :event_type"
                params['event_type'] = event_type
            
            query += " ORDER BY timestamp DESC LIMIT :limit"
            params['limit'] = limit
            
            result = conn.execute(text(query), params)
            logs = []
            
            for row in result:
                logs.append({
                    'timestamp': row[0],
                    'event_type': row[1],
                    'details': row[2]
                })
            
            return {
                'logs': logs,
                'total_count': len(logs),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Log retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logs")
async def create_integration_log(event_type: str, details: Dict[str, Any]):
    """통합 로그 생성"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not available")
    
    try:
        success = await integration_manager.core.log_integration_event(event_type, details)
        
        if success:
            return {
                'message': 'Log created successfully',
                'event_type': event_type,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create log")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Log creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error',
            'message': str(exc),
            'timestamp': datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "integration_api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 