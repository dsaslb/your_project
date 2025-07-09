from flask import Blueprint, jsonify
import random
from datetime import datetime, timedelta

ai_analytics_bp = Blueprint('ai_analytics', __name__)

@ai_analytics_bp.route('/api/ai/analysis', methods=['GET'])
def get_ai_analysis():
    """AI 기반 매장 운영 분석 데이터 반환"""
    
    # 더미 AI 분석 데이터
    analysis_data = {
        "summary": "이번 주 매장 운영 분석 결과, 인력 배치 최적화와 재고 관리 개선이 필요합니다.",
        "recommendations": [
            "금요일 저녁 시간대 인력 2명 추가 배치 권장",
            "A상품 재고 발주량 20% 증가 필요", 
            "고객 피드백 분석 결과: 서비스 응답 시간 개선 필요",
            "이번 달 마케팅 예산 효율성 15% 향상"
        ],
        "metrics": {
            "sales": random.randint(10000000, 15000000),
            "staff": random.randint(6, 12),
            "inventory": random.randint(75, 95),
            "customer": random.randint(85, 98)
        },
        "trends": {
            "sales_trend": "up",
            "staff_efficiency": "stable", 
            "inventory_turnover": "down",
            "customer_satisfaction": "up"
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return jsonify(analysis_data)

@ai_analytics_bp.route('/api/ai/predictions', methods=['GET'])
def get_ai_predictions():
    """AI 기반 예측 데이터 반환"""
    
    predictions = {
        "next_week_sales": random.randint(12000000, 18000000),
        "optimal_staff_count": random.randint(8, 15),
        "inventory_alert": [
            {"item": "A상품", "current": 15, "min_required": 20},
            {"item": "B상품", "current": 8, "min_required": 10}
        ],
        "customer_retention_rate": random.randint(85, 95),
        "risk_factors": [
            "재고 부족으로 인한 매출 감소 위험",
            "인력 부족으로 인한 서비스 품질 저하 위험"
        ]
    }
    
    return jsonify(predictions) 