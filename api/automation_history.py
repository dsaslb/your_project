from flask import Blueprint, jsonify, request
import datetime

automation_history_bp = Blueprint('automation_history', __name__, url_prefix='/api/automation-history')

# 샘플 더미 데이터 (실제 운영에서는 DB/로그/파일 등과 연동)
DUMMY_HISTORY = [
    {"id": 1, "event": "시스템 정상", "status": "success", "timestamp": "2024-06-01 09:00"},
    {"id": 2, "event": "피드백 통계 API 오류", "status": "warning", "timestamp": "2024-06-01 09:05"},
    {"id": 3, "event": "실시간 알림 정상 동작", "status": "success", "timestamp": "2024-06-01 09:10"},
]

@automation_history_bp.route('', methods=['GET'])
def get_automation_history():
    # 검색/필터 예시
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    result = DUMMY_HISTORY
    if status:
        result = [h for h in result if h['status'] == status]
    if keyword:
        result = [h for h in result if keyword in h['event']]
    return jsonify({"history": result})

# [확장 안내]
# 실제 운영에서는 DB(automation_history 테이블), 로그 파일, 외부 모니터링 시스템 등과 연동 가능
# 초보자/운영자도 쉽게 확장/문의할 수 있도록 주석/예시/문의 안내 포함 