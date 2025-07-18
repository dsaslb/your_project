from flask import Blueprint, jsonify
import os
import json
import time
import datetime

admin_dashboard_api = Blueprint('admin_dashboard_api', __name__)

@admin_dashboard_api.route('/api/automation-status', methods=['GET'])
def get_automation_status():
    """
    프론트엔드 대시보드 자동화 상태/최신화/보안 점검 결과 API (샘플)
    실제로는 auto_reminder_and_update_check.py, auto_env_check_and_notify.py 등 자동화 점검 결과를 통합해 반환
    초보자/운영자도 쉽게 확장/문의할 수 있도록 주석/예시 포함
    """
    # 샘플: 최근 30일 이내 미수정 파일이 있으면 경고, 없으면 정상
    CHECK_FILES = [
        'README.md',
        'docs/ADMIN_OPERATION_GUIDE.md',
        'frontend/app/accessibility/page.tsx',
        'frontend/app/faq/page.tsx',
        'scripts/auto_report_and_alert.py',
        'scripts/auto_env_check_and_notify.py',
    ]
    REMIND_DAYS = 30
    now = time.time()
    outdated = []
    for f in CHECK_FILES:
        if not os.path.exists(f):
            outdated.append(f'파일 없음: {f}')
            continue
        mtime = os.path.getmtime(f)
        days = int((now - mtime) // 86400)
        if days >= REMIND_DAYS:
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            outdated.append(f'{f} - {days}일 미수정 (최종: {dt})')
    up_to_date = len(outdated) == 0
    return jsonify({
        'upToDate': up_to_date,
        'outdatedFiles': len(outdated),
        'securityPatch': False,  # 샘플: 실제 보안 점검 결과 연동 가능
        'lastCheck': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'details': outdated,
    })


# (확장 예시) SQLAlchemy DB 모델 및 쿼리로 자동화 이력 불러오기
# 실제 운영에서는 아래 모델/쿼리를 사용해 DB에서 이력 데이터를 조회할 수 있습니다.
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
# class AutomationHistory(db.Model):
#     __tablename__ = 'automation_history'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(20))
#     status = db.Column(db.String(20))
#     details = db.Column(db.String(255))
#
# @admin_dashboard_api.route('/api/automation-history', methods=['GET'])
# def get_automation_history():
#     """
#     DB에서 자동화 이력 데이터를 불러오는 예시 (초보자/운영자 주석)
#     """
#     rows = AutomationHistory.query.order_by(AutomationHistory.date.desc()).limit(100).all()
#     return jsonify([
#         { 'date': r.date, 'status': r.status, 'details': r.details } for r in rows
#     ])


@admin_dashboard_api.route("/api/admin/dashboard-stats")
def get_dashboard_stats():
    # 예시: 승인률, 처리속도, 피드백 수, 차트 데이터 등
    stats = {
        "approval_rate": 92,
        "avg_process_time": 13,
        "feedback_count": 27,
        "chart_labels": ["월", "화", "수", "목", "금", "토", "일"],
        "approval_counts": [5, 7, 8, 6, 9, 4, 3],
        "feedback_counts": [1, 2, 3, 2, 4, 1, 1],
    }
    return jsonify({"success": True, "stats": stats})
