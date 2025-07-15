from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, Order, Attendance, InventoryItem
# (실제 환경에서는 외부 LLM/GPT API, 사내 AI 모델 등 연동)

ai_assistant_api = Blueprint('ai_assistant_api', __name__, url_prefix='/api/ai/assistant')

# 통합 데이터 기반 AI 리포트/진단/예측/개선점 추천 API
@ai_assistant_api.route('/report', methods=['POST'])
def ai_report():
    """
    매출/인건비/근무/재고 등 통합 데이터 기반 AI 리포트/진단/예측/개선점 추천
    (LLM/GPT 기반 자연어 리포트 예시 포함)
    """
    data = request.get_json() or {}
    # 1. 데이터 집계(예시)
    today = datetime.utcnow().date()
    sales = db.session.query(db.func.sum(Order.total_amount)).filter(Order.created_at >= today).scalar() or 0
    attendance_count = Attendance.query.filter(Attendance.clock_in >= today).count()
    inventory_low = InventoryItem.query.filter(InventoryItem.current_stock < 10).count()
    # 2. AI 진단/예측/개선점(예시)
    diagnosis = "매출이 전주 대비 10% 감소했습니다. 인건비 비율이 높아 개선이 필요합니다."
    prediction = "다음달 매출은 5% 증가가 예상됩니다."
    improvement = "재고 관리 자동화, 출근 지각률 개선을 추천합니다."
    # 3. LLM/GPT 기반 자연어 리포트(예시)
    llm_report = f"오늘 매출은 {sales:,}원이며, 출근 인원 {attendance_count}명, 재고 부족 품목 {inventory_low}건입니다. {diagnosis} {improvement} {prediction}"
    # 4. 결과 반환
    return jsonify({
        'sales': sales,
        'attendance_count': attendance_count,
        'inventory_low': inventory_low,
        'diagnosis': diagnosis,
        'prediction': prediction,
        'improvement': improvement,
        'llm_report': llm_report,
        'timestamp': datetime.utcnow().isoformat()
    })

# 실시간 이상 패턴/경보 감지 및 알림 API
@ai_assistant_api.route('/alerts', methods=['GET'])
def ai_alerts():
    """
    매출 급감/이상 입고 등 이상 패턴 자동 감지, 실시간 경보/알림 반환
    """
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=7)
    sales_today = db.session.query(db.func.sum(Order.total_amount)).filter(Order.created_at >= today).scalar() or 0
    sales_last_7 = db.session.query(db.func.sum(Order.total_amount)).filter(Order.created_at >= seven_days_ago, Order.created_at < today).scalar() or 0
    avg_sales_7 = sales_last_7 / 7 if sales_last_7 else 0
    alerts = []
    if avg_sales_7 > 0 and sales_today < avg_sales_7 * 0.7:
        alerts.append({
            'type': 'sales_drop',
            'message': f'오늘 매출이 최근 7일 평균 대비 30% 이상 급감했습니다.',
            'severity': 'critical',
            'timestamp': datetime.utcnow().isoformat()
        })
    # (추가: 재고 이상, 출근 지각 등 다양한 경보 확장 가능)
    return jsonify({'alerts': alerts, 'timestamp': datetime.utcnow().isoformat()}) 