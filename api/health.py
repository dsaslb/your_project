"""
헬스체크 및 메트릭 API
- /healthz: 프로세스 및 DB 상태
- /readyz: 종속 서비스 준비 상태
- /metrics: Prometheus 메트릭
"""
from flask import Blueprint, jsonify, current_app
from extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
import time
import logging
import psutil
import os

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)

@health_bp.route("/healthz", methods=["GET"])
def healthz():
    """
    기본 헬스체크 - 프로세스 및 DB 상태
    """
    start_time = time.time()
    
    try:
        # DB 연결 확인
        db.session.execute(text("SELECT 1"))
        db_status = "ok"
        db_response_time = int((time.time() - start_time) * 1000)
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"error: {str(e)}"
        db_response_time = int((time.time() - start_time) * 1000)
    
    # 시스템 리소스 확인
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_status = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # 리소스 임계값 체크
        is_healthy = (
            cpu_percent < 90 and
            memory.percent < 90 and
            disk.percent < 90
        )
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        system_status = {"error": str(e)}
        is_healthy = False
    
    # 전체 상태 결정
    overall_healthy = db_status == "ok" and is_healthy
    
    response_data = {
        "ok": overall_healthy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "response_time_ms": db_response_time
        },
        "system": system_status,
        "uptime_seconds": int(time.time() - psutil.Process().create_time())
    }
    
    status_code = 200 if overall_healthy else 503
    return jsonify(response_data), status_code

@health_bp.route("/readyz", methods=["GET"])
def readyz():
    """
    준비 상태 체크 - 종속 서비스 준비 여부
    """
    start_time = time.time()
    checks = {}
    all_ready = True
    
    # 1. 데이터베이스 준비 상태
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = {
            "status": "ready",
            "response_time_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        checks["database"] = {
            "status": "not_ready",
            "error": str(e)
        }
        all_ready = False
    
    # 2. Redis 연결 확인 (있는 경우)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
        r.ping()
        checks["redis"] = {"status": "ready"}
    except Exception as e:
        checks["redis"] = {"status": "not_ready", "error": str(e)}
        # Redis는 선택적이므로 전체 상태에 영향 없음
    
    # 3. Outbox 상태 확인
    try:
        from utils.outbox import get_outbox_stats
        outbox_stats = get_outbox_stats()
        
        # 실패한 이벤트가 너무 많으면 not ready
        failed_ratio = outbox_stats.get("failed", 0) / max(outbox_stats.get("total", 1), 1)
        is_outbox_ready = failed_ratio < 0.2  # 20% 미만
        
        checks["outbox"] = {
            "status": "ready" if is_outbox_ready else "not_ready",
            "stats": outbox_stats,
            "failed_ratio": failed_ratio
        }
        
        if not is_outbox_ready:
            all_ready = False
            
    except Exception as e:
        checks["outbox"] = {
            "status": "not_ready",
            "error": str(e)
        }
        all_ready = False
    
    # 4. 외부 API 연결 확인 (선택적)
    try:
        # 예: 카카오 API, 결제 API 등
        # 실제 구현에서는 필요한 외부 서비스들을 체크
        checks["external_apis"] = {"status": "ready"}
    except Exception as e:
        checks["external_apis"] = {
            "status": "not_ready",
            "error": str(e)
        }
        # 외부 API는 선택적이므로 전체 상태에 영향 없음
    
    response_data = {
        "ok": all_ready,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "overall_response_time_ms": int((time.time() - start_time) * 1000)
    }
    
    status_code = 200 if all_ready else 503
    return jsonify(response_data), status_code

@health_bp.route("/metrics", methods=["GET"])
def metrics():
    """
    Prometheus 메트릭 (간단한 버전)
    """
    try:
        from utils.outbox import get_outbox_stats
        from models_sync import SyncAudit, SyncMetrics
        
        # Outbox 메트릭
        outbox_stats = get_outbox_stats()
        
        # 동기화 통계
        sync_stats = db.session.query(
            SyncAudit.status,
            db.func.count(SyncAudit.id).label('count')
        ).group_by(SyncAudit.status).all()
        
        # 최근 1시간 처리량
        from datetime import timedelta
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_syncs = SyncAudit.query.filter(
            SyncAudit.created_at >= one_hour_ago
        ).count()
        
        # 시스템 메트릭
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        metrics_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "outbox": {
                "total_events": outbox_stats.get("total", 0),
                "pending_events": outbox_stats.get("pending", 0),
                "delivered_events": outbox_stats.get("delivered", 0),
                "failed_events": outbox_stats.get("failed", 0),
                "delivery_rate": outbox_stats.get("delivery_rate", 0)
            },
            "sync": {
                "recent_syncs_1h": recent_syncs,
                "status_breakdown": {stat.status: stat.count for stat in sync_stats}
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024)
            }
        }
        
        return jsonify(metrics_data)
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return jsonify({
            "error": "Failed to collect metrics",
            "code": "METRICS_ERROR"
        }), 500

@health_bp.route("/metrics/prometheus", methods=["GET"])
def prometheus_metrics():
    """
    Prometheus 형식의 메트릭
    """
    try:
        from utils.outbox import get_outbox_stats
        from models_sync import SyncAudit
        
        outbox_stats = get_outbox_stats()
        
        # Prometheus 형식으로 메트릭 생성
        metrics_lines = []
        
        # Outbox 메트릭
        metrics_lines.append(f"# HELP outbox_events_total Total number of outbox events")
        metrics_lines.append(f"# TYPE outbox_events_total counter")
        metrics_lines.append(f"outbox_events_total {outbox_stats.get('total', 0)}")
        
        metrics_lines.append(f"# HELP outbox_events_pending Number of pending outbox events")
        metrics_lines.append(f"# TYPE outbox_events_pending gauge")
        metrics_lines.append(f"outbox_events_pending {outbox_stats.get('pending', 0)}")
        
        metrics_lines.append(f"# HELP outbox_events_delivered Number of delivered outbox events")
        metrics_lines.append(f"# TYPE outbox_events_delivered counter")
        metrics_lines.append(f"outbox_events_delivered {outbox_stats.get('delivered', 0)}")
        
        metrics_lines.append(f"# HELP outbox_events_failed Number of failed outbox events")
        metrics_lines.append(f"# TYPE outbox_events_failed counter")
        metrics_lines.append(f"outbox_events_failed {outbox_stats.get('failed', 0)}")
        
        # 동기화 메트릭
        sync_stats = db.session.query(
            SyncAudit.status,
            db.func.count(SyncAudit.id).label('count')
        ).group_by(SyncAudit.status).all()
        
        for stat in sync_stats:
            metrics_lines.append(f"# HELP sync_audits_total Total number of sync audits by status")
            metrics_lines.append(f"# TYPE sync_audits_total counter")
            metrics_lines.append(f'sync_audits_total{{status="{stat.status}"}} {stat.count}')
        
        # 시스템 메트릭
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        metrics_lines.append(f"# HELP system_cpu_percent CPU usage percentage")
        metrics_lines.append(f"# TYPE system_cpu_percent gauge")
        metrics_lines.append(f"system_cpu_percent {cpu_percent}")
        
        metrics_lines.append(f"# HELP system_memory_percent Memory usage percentage")
        metrics_lines.append(f"# TYPE system_memory_percent gauge")
        metrics_lines.append(f"system_memory_percent {memory.percent}")
        
        metrics_text = "\n".join(metrics_lines)
        
        return metrics_text, 200, {"Content-Type": "text/plain; charset=utf-8"}
        
    except Exception as e:
        logger.error(f"Prometheus metrics failed: {e}")
        return f"# ERROR: {str(e)}", 500, {"Content-Type": "text/plain; charset=utf-8"}

@health_bp.route("/version", methods=["GET"])
def version():
    """애플리케이션 버전 정보"""
    try:
        version_info = {
            "app_version": current_app.config.get("APP_VERSION", "1.0.0"),
            "python_version": os.sys.version,
            "flask_version": current_app.config.get("FLASK_VERSION", "unknown"),
            "build_time": current_app.config.get("BUILD_TIME", "unknown"),
            "git_commit": current_app.config.get("GIT_COMMIT", "unknown")
        }
        
        return jsonify(version_info)
        
    except Exception as e:
        logger.error(f"Version info failed: {e}")
        return jsonify({
            "error": "Failed to get version info"
        }), 500