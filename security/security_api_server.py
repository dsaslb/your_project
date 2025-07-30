from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
import json
from datetime import datetime, timedelta
import uvicorn
from pathlib import Path

from security_monitor import SecurityMonitor, SecurityEvent, SecurityAlert

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic 모델들
class SecurityEventRequest(BaseModel):
    event_type: str
    source_ip: str
    target: str
    payload: str
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None

class SecurityConfigUpdate(BaseModel):
    detection_enabled: Optional[bool] = None
    alert_threshold: Optional[int] = None
    monitoring_interval: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    ip_blacklist: Optional[List[str]] = None

class SecurityResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# FastAPI 앱 생성
app = FastAPI(
    title="Your Program 보안 API 서버",
    description="실시간 보안 모니터링 및 위협 탐지 API",
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

# 전역 보안 모니터 인스턴스
security_monitor = None

async def get_security_monitor() -> SecurityMonitor:
    """보안 모니터 인스턴스 반환"""
    global security_monitor
    if security_monitor is None:
        config = {
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'db_path': 'security_events.db',
            'detection_enabled': True,
            'alert_threshold': 5,
            'monitoring_interval': 10
        }
        security_monitor = SecurityMonitor(config)
        await security_monitor.start_monitoring()
    return security_monitor

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    logger.info("보안 API 서버 시작 중...")
    await get_security_monitor()
    logger.info("보안 API 서버 시작 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리"""
    logger.info("보안 API 서버 종료 중...")
    if security_monitor:
        await security_monitor.stop_monitoring()
    logger.info("보안 API 서버 종료 완료")

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "security-api"
    }

@app.get("/security/status")
async def get_security_status(monitor: SecurityMonitor = Depends(get_security_monitor)):
    """보안 시스템 상태 조회"""
    try:
        # 최근 이벤트 통계
        recent_events = await monitor.get_recent_events(limit=1000)
        
        # 위협 유형별 통계
        threat_stats = {}
        for event in recent_events:
            threat_type = event.get('threat_type', 'unknown')
            threat_stats[threat_type] = threat_stats.get(threat_type, 0) + 1
        
        # 심각도별 통계
        severity_stats = {}
        for event in recent_events:
            severity = event.get('severity', 'low')
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
        
        # 최근 알림
        recent_alerts = monitor.security_alerts[-10:] if monitor.security_alerts else []
        
        return {
            "status": "active" if monitor.is_monitoring else "inactive",
            "monitoring_since": monitor.start_time.isoformat() if hasattr(monitor, 'start_time') else None,
            "total_events": len(recent_events),
            "threat_statistics": threat_stats,
            "severity_statistics": severity_stats,
            "recent_alerts": len(recent_alerts),
            "system_health": "healthy"
        }
    except Exception as e:
        logger.error(f"보안 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/events")
async def get_security_events(
    limit: int = Query(100, ge=1, le=1000),
    threat_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 이벤트 조회"""
    try:
        events = await monitor.get_recent_events(limit=limit)
        
        # 필터링
        if threat_type:
            events = [e for e in events if e.get('threat_type') == threat_type]
        
        if severity:
            events = [e for e in events if e.get('severity') == severity]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            events = [e for e in events if datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            events = [e for e in events if datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) <= end_dt]
        
        return {
            "events": events,
            "total": len(events),
            "filters": {
                "threat_type": threat_type,
                "severity": severity,
                "start_time": start_time,
                "end_time": end_time
            }
        }
    except Exception as e:
        logger.error(f"보안 이벤트 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/alerts")
async def get_security_alerts(
    limit: int = Query(50, ge=1, le=500),
    severity: Optional[str] = Query(None),
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 알림 조회"""
    try:
        alerts = monitor.security_alerts[-limit:] if monitor.security_alerts else []
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # 알림을 딕셔너리로 변환
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "alert_id": alert.alert_id,
                "threat_type": alert.threat_type,
                "severity": alert.severity,
                "source_ip": alert.source_ip,
                "target": alert.target,
                "description": alert.description,
                "mitigation": alert.mitigation,
                "timestamp": alert.timestamp.isoformat(),
                "is_resolved": alert.is_resolved
            })
        
        return {
            "alerts": alert_data,
            "total": len(alert_data)
        }
    except Exception as e:
        logger.error(f"보안 알림 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security/events")
async def create_security_event(
    event_request: SecurityEventRequest,
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 이벤트 생성 (외부 시스템에서 이벤트 전송용)"""
    try:
        # 이벤트 분석
        analysis_result = await monitor.analyze_event(
            event_type=event_request.event_type,
            source_ip=event_request.source_ip,
            target=event_request.target,
            payload=event_request.payload,
            user_agent=event_request.user_agent
        )
        
        return {
            "status": "processed",
            "event_id": analysis_result.get('event_id'),
            "threat_detected": analysis_result.get('threat_detected', False),
            "threat_score": analysis_result.get('threat_score', 0),
            "threats": analysis_result.get('detected_threats', [])
        }
    except Exception as e:
        logger.error(f"보안 이벤트 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/metrics")
async def get_security_metrics(monitor: SecurityMonitor = Depends(get_security_monitor)):
    """보안 메트릭 조회"""
    try:
        # 최근 24시간 통계
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        recent_events = await monitor.get_recent_events(limit=10000)
        
        # 시간대별 이벤트 수
        hourly_stats = {}
        for i in range(24):
            hour = (start_time + timedelta(hours=i)).hour
            hourly_stats[f"{hour:02d}:00"] = 0
        
        for event in recent_events:
            event_time = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
            if start_time <= event_time <= end_time:
                hour_key = f"{event_time.hour:02d}:00"
                if hour_key in hourly_stats:
                    hourly_stats[hour_key] += 1
        
        # 상위 공격 IP
        ip_stats = {}
        for event in recent_events:
            ip = event.get('source_ip', 'unknown')
            ip_stats[ip] = ip_stats.get(ip, 0) + 1
        
        top_ips = sorted(ip_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 위협 트렌드
        threat_trend = {}
        for event in recent_events:
            threat_type = event.get('threat_type', 'unknown')
            threat_trend[threat_type] = threat_trend.get(threat_type, 0) + 1
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "hourly_events": hourly_stats,
            "top_attack_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
            "threat_distribution": threat_trend,
            "total_events_24h": len([e for e in recent_events 
                                   if start_time <= datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) <= end_time])
        }
    except Exception as e:
        logger.error(f"보안 메트릭 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/security/config")
async def update_security_config(
    config_update: SecurityConfigUpdate,
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 설정 업데이트"""
    try:
        updated_fields = {}
        
        if config_update.detection_enabled is not None:
            monitor.config['detection_enabled'] = config_update.detection_enabled
            updated_fields['detection_enabled'] = config_update.detection_enabled
        
        if config_update.alert_threshold is not None:
            monitor.config['alert_threshold'] = config_update.alert_threshold
            updated_fields['alert_threshold'] = config_update.alert_threshold
        
        if config_update.monitoring_interval is not None:
            monitor.config['monitoring_interval'] = config_update.monitoring_interval
            updated_fields['monitoring_interval'] = config_update.monitoring_interval
        
        if config_update.ip_whitelist is not None:
            monitor.config['ip_whitelist'] = config_update.ip_whitelist
            updated_fields['ip_whitelist'] = config_update.ip_whitelist
        
        if config_update.ip_blacklist is not None:
            monitor.config['ip_blacklist'] = config_update.ip_blacklist
            updated_fields['ip_blacklist'] = config_update.ip_blacklist
        
        return {
            "status": "updated",
            "updated_fields": updated_fields,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"보안 설정 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security/alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 알림 해결 처리"""
    try:
        # 알림 찾기 및 해결 처리
        for alert in monitor.security_alerts:
            if alert.alert_id == alert_id:
                alert.is_resolved = True
                alert.resolved_at = datetime.now()
                
                return {
                    "status": "resolved",
                    "alert_id": alert_id,
                    "resolved_at": alert.resolved_at.isoformat()
                }
        
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    except Exception as e:
        logger.error(f"보안 알림 해결 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/reports/summary")
async def get_security_summary_report(
    days: int = Query(7, ge=1, le=30),
    monitor: SecurityMonitor = Depends(get_security_monitor)
):
    """보안 요약 보고서"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        recent_events = await monitor.get_recent_events(limit=50000)
        period_events = [
            e for e in recent_events 
            if start_time <= datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) <= end_time
        ]
        
        # 위협 유형별 분석
        threat_analysis = {}
        for event in period_events:
            threat_type = event.get('threat_type', 'unknown')
            if threat_type not in threat_analysis:
                threat_analysis[threat_type] = {
                    'count': 0,
                    'high_severity': 0,
                    'unique_ips': set()
                }
            
            threat_analysis[threat_type]['count'] += 1
            if event.get('severity') == 'high':
                threat_analysis[threat_type]['high_severity'] += 1
            threat_analysis[threat_type]['unique_ips'].add(event.get('source_ip', ''))
        
        # set을 리스트로 변환
        for threat_type in threat_analysis:
            threat_analysis[threat_type]['unique_ips'] = len(threat_analysis[threat_type]['unique_ips'])
        
        # 일별 트렌드
        daily_trend = {}
        for i in range(days):
            date = (start_time + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_trend[date] = 0
        
        for event in period_events:
            event_date = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00')).strftime('%Y-%m-%d')
            if event_date in daily_trend:
                daily_trend[event_date] += 1
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": days
            },
            "summary": {
                "total_events": len(period_events),
                "unique_threat_types": len(threat_analysis),
                "total_alerts": len([a for a in monitor.security_alerts 
                                   if start_time <= a.timestamp <= end_time])
            },
            "threat_analysis": threat_analysis,
            "daily_trend": daily_trend
        }
    except Exception as e:
        logger.error(f"보안 요약 보고서 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "security_api_server:app",
        host="0.0.0.0",
        port=8007,
        reload=True,
        log_level="info"
    ) 