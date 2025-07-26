from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "websocket_available": False
    })

@app.route('/api/admin/brand_stats')
def brand_stats():
    """브랜드별 통계 API (더미 데이터)"""
    stats_data = [
        {
            "brand_id": 1,
            "brand_name": "스타벅스",
            "employee_count": 25,
            "manager_count": 3,
            "store_count": 5,
            "total_count": 28,
        },
        {
            "brand_id": 2,
            "brand_name": "투썸플레이스",
            "employee_count": 18,
            "manager_count": 2,
            "store_count": 3,
            "total_count": 20,
        },
        {
            "brand_id": 3,
            "brand_name": "할리스",
            "employee_count": 15,
            "manager_count": 2,
            "store_count": 2,
            "total_count": 17,
        }
    ]
    
    return jsonify({
        "brand_stats": stats_data,
        "source": "test_server",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/admin/brand_stats_real')
def brand_stats_real():
    """실제 데이터 브랜드 통계 API"""
    try:
        # 실제 데이터베이스 쿼리 대신 더미 데이터 반환
        stats_data = [
            {
                "brand_id": 1,
                "brand_name": "스타벅스",
                "employee_count": 25,
                "manager_count": 3,
                "store_count": 5,
                "total_count": 28,
                "growth_rate": 12.5,
                "avg_employees_per_store": 5.0,
                "activity_score": 85
            },
            {
                "brand_id": 2,
                "brand_name": "투썸플레이스",
                "employee_count": 18,
                "manager_count": 2,
                "store_count": 3,
                "total_count": 20,
                "growth_rate": 8.3,
                "avg_employees_per_store": 6.0,
                "activity_score": 78
            },
            {
                "brand_id": 3,
                "brand_name": "할리스",
                "employee_count": 15,
                "manager_count": 2,
                "store_count": 2,
                "total_count": 17,
                "growth_rate": 15.2,
                "avg_employees_per_store": 7.5,
                "activity_score": 92
            }
        ]
        
        return jsonify({
            "brand_stats": stats_data,
            "summary": {
                "total_brands": len(stats_data),
                "total_employees": sum(s["employee_count"] for s in stats_data),
                "total_stores": sum(s["store_count"] for s in stats_data),
                "avg_growth_rate": sum(s["growth_rate"] for s in stats_data) / len(stats_data)
            },
            "source": "test_server_real",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "브랜드 통계 조회 중 오류가 발생했습니다.",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/admin/brand_stats/realtime')
def brand_stats_realtime():
    """실시간 브랜드 통계 API"""
    try:
        # 실시간 업데이트 시뮬레이션
        recent_changes = [
            {
                "type": "employee_added",
                "brand_name": "스타벅스",
                "message": "새 직원 등록",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "type": "store_updated",
                "brand_name": "투썸플레이스",
                "message": "매장 정보 업데이트",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            "recent_changes": recent_changes,
            "last_update": datetime.utcnow().isoformat(),
            "source": "test_server_realtime"
        })
    except Exception as e:
        return jsonify({
            "error": "실시간 통계 조회 중 오류가 발생했습니다.",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/admin/brand_stats/analytics')
def brand_stats_analytics():
    """브랜드 통계 고급 분석 API"""
    try:
        analytics_data = {
            "growth_analysis": {
                "top_growing_brand": "할리스",
                "growth_rate": 15.2,
                "monthly_trend": [8.5, 10.2, 12.1, 15.2]
            },
            "efficiency_metrics": {
                "avg_employees_per_store": 6.2,
                "most_efficient_brand": "스타벅스",
                "efficiency_score": 85
            },
            "activity_scores": [
                {"brand": "스타벅스", "score": 85},
                {"brand": "투썸플레이스", "score": 78},
                {"brand": "할리스", "score": 92}
            ],
            "monthly_registrations": [
                {"month": "2024-01", "count": 45},
                {"month": "2024-02", "count": 52},
                {"month": "2024-03", "count": 48},
                {"month": "2024-04", "count": 61}
            ]
        }
        
        return jsonify({
            "analytics": analytics_data,
            "source": "test_server_analytics",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "분석 데이터 조회 중 오류가 발생했습니다.",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/websocket/test-notification', methods=['POST'])
def test_notification():
    """WebSocket 알림 테스트 API (더미)"""
    try:
        data = request.get_json() if request.is_json else {}
        notification_data = {
            'type': 'notification',
            'notification': {
                'type': data.get('type', 'info'),
                'title': data.get('title', '테스트 알림'),
                'message': data.get('message', 'WebSocket 알림 테스트입니다.'),
                'priority': data.get('priority', 'medium')
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "success": True,
            "message": "알림이 처리되었습니다 (WebSocket 비활성화)",
            "notification": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": "알림 처리 실패",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 테스트 서버가 시작됩니다...")
    print("⚠️ WebSocket 없이 기본 Flask 서버를 시작합니다...")
    app.run(debug=True, host="0.0.0.0", port=5000) 