"""
알림(이메일/SMS/푸시) 발송 및 내역 API (관리자 전용)
- /api/admin/notifications/send [POST]
- /api/admin/notifications/history [GET]
"""
from flask import Blueprint, request, jsonify, abort
from middleware.security import admin_required
import os
import smtplib
from email.mime.text import MIMEText
import time

bp = Blueprint('admin_notifications_api', __name__, url_prefix='/api/admin/notifications')

NOTIFY_HISTORY_FILE = 'logs/notification_history.json'

def save_history(entry):
    import json
    try:
        if os.path.exists(NOTIFY_HISTORY_FILE):
            with open(NOTIFY_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
    except Exception:
        history = []
    history.append(entry)
    with open(NOTIFY_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history[-100:], f, ensure_ascii=False, indent=2)

@bp.route('/send', methods=['POST'])
@admin_required
def send_notification():
    """알림(이메일/SMS/푸시) 발송"""
    data = request.json
    notif_type = data.get('type', 'email')
    to = data.get('to')
    subject = data.get('subject', '알림')
    message = data.get('message')
    status = 'success'
    error = None
    try:
        if notif_type == 'email':
            smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('EMAIL_PORT', 587))
            smtp_user = os.getenv('EMAIL_USERNAME')
            smtp_pass = os.getenv('EMAIL_PASSWORD')
            if not smtp_user or not smtp_pass:
                raise Exception('이메일 환경변수 미설정')
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = to
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [to], msg.as_string())
        elif notif_type == 'sms':
            # Twilio 등 SMS 연동 예시 (실제 구현 필요)
            # from twilio.rest import Client
            # ...
            pass
        elif notif_type == 'push':
            # Firebase 등 푸시 연동 예시 (실제 구현 필요)
            pass
        else:
            raise Exception('지원하지 않는 알림 유형')
    except Exception as e:
        status = 'fail'
        error = str(e)
    entry = {
        'type': notif_type,
        'to': to,
        'subject': subject,
        'message': message,
        'status': status,
        'error': error,
        'timestamp': int(time.time())
    }
    save_history(entry)
    if status == 'success':
        return jsonify({'result': 'ok'})
    else:
        return jsonify({'result': 'fail', 'error': error}), 500

@bp.route('/history', methods=['GET'])
@admin_required
def notification_history():
    """알림 발송 내역 조회"""
    import json
    if not os.path.exists(NOTIFY_HISTORY_FILE):
        return jsonify({'history': []})
    with open(NOTIFY_HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
    return jsonify({'history': history[::-1]}) 