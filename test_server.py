"""
간단한 테스트 서버
- 동기화 API만 포함한 최소한의 서버
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    """헬스체크 엔드포인트"""
    return jsonify({
        "ok": True,
        "database": {"status": "ok"},
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/readyz', methods=['GET'])
def readyz():
    """레디체크 엔드포인트"""
    return jsonify({
        "ok": True,
        "ready": True
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """메트릭 엔드포인트"""
    return jsonify({
        "outbox": {
            "total_events": 0,
            "pending_events": 0,
            "delivered_events": 0,
            "failed_events": 0
        },
        "sync": {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0
        }
    })

@app.route('/api/mobile/sync/batch', methods=['POST'])
def sync_batch():
    """배치 동기화 엔드포인트 (테스트용)"""
    try:
        data = request.get_json() or {}
        items = data.get("items", [])
        meta = data.get("meta", {})
        
        logger.info(f"배치 동기화 요청: {len(items)}개 아이템")
        
        results = []
        for item in items:
            item_type = item.get("type")
            item_idem = item.get("idem")
            
            # 간단한 응답 생성
            result = {
                "idem": item_idem,
                "status": "ok"  # 테스트용으로 항상 성공
            }
            results.append(result)
        
        return jsonify({
            "ok": True,
            "results": results,
            "stats": {
                "total": len(items),
                "ok": len(items),
                "dup": 0,
                "error": 0
            }
        })
        
    except Exception as e:
        logger.error(f"배치 동기화 오류: {e}")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/mobile/dashboard', methods=['GET'])
def mobile_dashboard():
    """모바일 대시보드 엔드포인트 (테스트용)"""
    return jsonify({
        "user": {"id": 1, "username": "테스트 사용자", "role": "employee"},
        "today_schedule": "09:00 - 18:00",
        "attendance_status": "미체크",
        "pending_orders": 0,
        "inventory_alerts": 0,
        "quick_stats": {
            "today_orders": 0,
            "pending_orders": 0,
            "today_revenue": 0,
            "staff_on_duty": 0
        },
        "recent_activities": [],
        "quick_actions": [
            {"id": "attendance", "title": "출퇴근", "icon": "clock", "color": "orange"},
            {"id": "inventory_check", "title": "재고 확인", "icon": "package", "color": "green"}
        ],
        "timestamp": "2024-01-01T00:00:00Z"
    })

if __name__ == '__main__':
    logger.info("🚀 테스트 서버 시작...")
    logger.info("🌐 서버 주소: http://localhost:5000")
    logger.info("📊 대시보드: http://localhost:5000/api/mobile/dashboard")
    logger.info("🏥 헬스체크: http://localhost:5000/healthz")
    logger.info("🔄 배치 동기화: http://localhost:5000/api/mobile/sync/batch")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"서버 실행 실패: {e}")
