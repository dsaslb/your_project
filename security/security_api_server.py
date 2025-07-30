"""
보안 API 서버

고급 보안 모니터링 시스템의 REST API 제공
"""

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uvicorn
import logging
from contextlib import asynccontextmanager

from security.advanced_security_monitor import get_security_monitor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response 모델
class MonitorRequestModel(BaseModel):
    """요청 모니터링 모델"""
    source_ip: str
    path: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    body: str = ""
    
class AuthenticationModel(BaseModel):
    """인증 모니터링 모델"""
    username: str
    source_ip: str
    success: bool
    timestamp: Optional[datetime] = None
    
class ThreatIntelligenceModel(BaseModel):
    """위협 인텔리전스 모델"""
    threat_id: str
    threat_type: str
    indicators: List[str]
    severity: str = Field(..., regex="^(critical|high|medium|low)$")
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    
class SecurityEventResponse(BaseModel):
    """보안 이벤트 응답 모델"""
    event_id: str
    event_type: str
    severity: str
    source_ip: str
    target: str
    description: str
    timestamp: str
    
class MonitorResponse(BaseModel):
    """모니터링 응답 모델"""
    action: str
    reason: Optional[str] = None
    severity: Optional[str] = None
    monitored: bool = True
    threats: Optional[List[Dict]] = None
    anomaly: Optional[Dict] = None

# 앱 생명주기 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    # 시작 시
    logger.info("Security API Server starting...")
    security_monitor = get_security_monitor()
    yield
    # 종료 시
    logger.info("Security API Server shutting down...")

# FastAPI 앱 생성
app = FastAPI(
    title="Security Monitoring API",
    description="고급 보안 모니터링 시스템 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host 미들웨어
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 의존성
async def get_monitor():
    """보안 모니터 인스턴스 반환"""
    return get_security_monitor()

# API 엔드포인트
@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "security_monitoring",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/monitor/request", response_model=MonitorResponse)
async def monitor_request(
    request_data: MonitorRequestModel,
    monitor = Depends(get_monitor)
):
    """HTTP 요청 모니터링"""
    try:
        result = await monitor.monitor_request(request_data.dict())
        return MonitorResponse(**result)
    except Exception as e:
        logger.error(f"Error monitoring request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor/authentication", response_model=MonitorResponse)
async def monitor_authentication(
    auth_data: AuthenticationModel,
    monitor = Depends(get_monitor)
):
    """인증 시도 모니터링"""
    try:
        result = await monitor.monitor_authentication(auth_data.dict())
        return MonitorResponse(**result)
    except Exception as e:
        logger.error(f"Error monitoring authentication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/recent", response_model=List[SecurityEventResponse])
async def get_recent_events(
    limit: int = 20,
    severity: Optional[str] = None,
    monitor = Depends(get_monitor)
):
    """최근 보안 이벤트 조회"""
    try:
        dashboard_data = await monitor.get_security_dashboard_data()
        events = dashboard_data.get('recent_events', [])
        
        # 심각도 필터링
        if severity:
            events = [e for e in events if e['severity'] == severity]
        
        # 제한 적용
        events = events[:limit]
        
        return [SecurityEventResponse(**event) for event in events]
    except Exception as e:
        logger.error(f"Error getting recent events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_dashboard_data(monitor = Depends(get_monitor)):
    """보안 대시보드 데이터 조회"""
    try:
        data = await monitor.get_security_dashboard_data()
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threats/intelligence")
async def get_threat_intelligence(monitor = Depends(get_monitor)):
    """위협 인텔리전스 조회"""
    try:
        threats = await monitor.get_threat_intelligence()
        return {
            "status": "success",
            "threats": threats,
            "count": len(threats),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/threats/intelligence")
async def update_threat_intelligence(
    threat_data: ThreatIntelligenceModel,
    background_tasks: BackgroundTasks,
    monitor = Depends(get_monitor)
):
    """위협 인텔리전스 업데이트"""
    try:
        # 백그라운드에서 업데이트
        background_tasks.add_task(
            monitor.update_threat_intelligence,
            threat_data.dict()
        )
        
        return {
            "status": "accepted",
            "message": "Threat intelligence update scheduled",
            "threat_id": threat_data.threat_id
        }
    except Exception as e:
        logger.error(f"Error updating threat intelligence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blocked-ips")
async def get_blocked_ips(monitor = Depends(get_monitor)):
    """차단된 IP 목록 조회"""
    try:
        blocked_ips = list(monitor.blocked_ips)
        return {
            "status": "success",
            "blocked_ips": blocked_ips,
            "count": len(blocked_ips),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting blocked IPs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/blocked-ips/{ip}")
async def unblock_ip(ip: str, monitor = Depends(get_monitor)):
    """IP 차단 해제"""
    try:
        if ip in monitor.blocked_ips:
            monitor.blocked_ips.remove(ip)
            return {
                "status": "success",
                "message": f"IP {ip} unblocked",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"IP {ip} not found in blocked list")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unblocking IP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_security_metrics(monitor = Depends(get_monitor)):
    """보안 메트릭 조회"""
    try:
        dashboard_data = await monitor.get_security_dashboard_data()
        
        return {
            "status": "success",
            "metrics": {
                "total_events_24h": dashboard_data.get('total_events_24h', 0),
                "active_threats": dashboard_data.get('active_threats', 0),
                "blocked_ips_count": len(monitor.blocked_ips),
                "event_types": dashboard_data.get('event_types', {}),
                "severity_distribution": dashboard_data.get('severity_distribution', {})
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 실시간 모니터링 미들웨어
@app.middleware("http")
async def security_monitoring_middleware(request: Request, call_next):
    """모든 요청에 대한 보안 모니터링"""
    monitor = get_security_monitor()
    
    # 요청 정보 수집
    client_host = request.client.host if request.client else "unknown"
    
    # 모니터링 데이터 구성
    monitor_data = {
        "source_ip": client_host,
        "path": str(request.url.path),
        "method": request.method,
        "headers": dict(request.headers),
        "body": ""  # 본문은 성능상 생략
    }
    
    # 보안 모니터링 수행
    result = await monitor.monitor_request(monitor_data)
    
    # 차단 처리
    if result.get('action') == 'block':
        raise HTTPException(
            status_code=403,
            detail=result.get('reason', 'Request blocked by security policy')
        )
    
    # 요청 처리 계속
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(
        "security_api_server:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )