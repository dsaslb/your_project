import os
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
environ = None  # pyright: ignore
#!/usr/bin/env python3
"""
알림 관리 API 엔드포인트
알림 로그, 통계, 설정 관리 기능
"""


# 알림 로그 모델 import
try:
    from models.alert_log import AlertLog, db
except ImportError:
    AlertLog = None
    db = None

logger = logging.getLogger(__name__)

# Blueprint 생성
alert_management_bp = Blueprint('alert_management', __name__, url_prefix='/api/alerts')


@alert_management_bp.route('/logs', methods=['GET'])
def get_alert_logs():
    """알림 로그 조회"""
    try:
        if not AlertLog:
            return jsonify({
                'success': False,
                'error': '알림 로그 모델을 사용할 수 없습니다'
            }), 500

        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        level = request.args.get('level')
        channel = request.args.get('channel')
        plugin_id = request.args.get('plugin_id')
        days = request.args.get('days', 7, type=int)

        # 기본 쿼리 (최근 N일)
        query = AlertLog.query.filter(
            AlertLog.timestamp >= datetime.utcnow() - timedelta(days=days)
        )

        # 필터 적용
        if level:
            query = query.filter(AlertLog.level == level)
        if channel:
            query = query.filter(AlertLog.channel == channel)
        if plugin_id:
            query = query.filter(AlertLog.plugin_id == plugin_id)

        # 정렬 및 페이징
        logs = query.order_by(AlertLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': logs.total,
                    'pages': logs.pages
                }
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"알림 로그 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@alert_management_bp.route('/stats', methods=['GET'])
def get_alert_stats():
    """알림 통계 조회"""
    try:
        if not AlertLog:
            return jsonify({
                'success': False,
                'error': '알림 로그 모델을 사용할 수 없습니다'
            }), 500

        days = request.args.get('days', 7, type=int) if args else None
        start_date = datetime.utcnow() - timedelta(days=days)

        # 전체 알림 수
        total_alerts = AlertLog.query.filter(
            AlertLog.timestamp >= start_date
        ).count()

        # 레벨별 통계
        level_stats = db.session.query(
            AlertLog.level,
            db.func.count(AlertLog.id)
        ).filter(
            AlertLog.timestamp >= start_date
        ).group_by(AlertLog.level).all()

        # 채널별 통계
        channel_stats = db.session.query(
            AlertLog.channel,
            db.func.count(AlertLog.id)
        ).filter(
            AlertLog.timestamp >= start_date
        ).group_by(AlertLog.channel).all()

        # 플러그인별 통계
        plugin_stats = db.session.query(
            AlertLog.plugin_id,
            db.func.count(AlertLog.id)
        ).filter(
            AlertLog.timestamp >= start_date,
            AlertLog.plugin_id.isnot(None)
        ).group_by(AlertLog.plugin_id).all()

        # 시간대별 통계 (최근 24시간)
        hourly_stats = db.session.query(
            db.func.date_trunc('hour', AlertLog.timestamp),
            db.func.count(AlertLog.id)
        ).filter(
            AlertLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).group_by(
            db.func.date_trunc('hour', AlertLog.timestamp)
        ).order_by(
            db.func.date_trunc('hour', AlertLog.timestamp)
        ).all()

        return jsonify({
            'success': True,
            'data': {
                'total_alerts': total_alerts,
                'level_stats': dict(level_stats),
                'channel_stats': dict(channel_stats),
                'plugin_stats': dict(plugin_stats),
                'hourly_stats': [
                    {
                        'hour': hour.isoformat(),
                        'count': count
                    } for hour, count in hourly_stats
                ]
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"알림 통계 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@alert_management_bp.route('/settings', methods=['GET'])
def get_alert_settings():
    """알림 설정 조회"""
    try:
        # 환경변수에서 설정 정보 조회
        settings = {
            'slack': {
                'enabled': bool(os.environ.get('SLACK_WEBHOOK_URL')),
                'webhook_url': os.environ.get('SLACK_WEBHOOK_URL', '')
            },
            'email': {
                'enabled': bool(os.environ.get('ALERT_SMTP_SERVER')),
                'smtp_server': os.environ.get('ALERT_SMTP_SERVER', ''),
                'from_email': os.environ.get('ALERT_FROM_EMAIL', ''),
                'to_email': os.environ.get('ALERT_TO_EMAIL', '')
            },
            'sms': {
                'enabled': bool(os.environ.get('TWILIO_ACCOUNT_SID') or os.environ.get('NAVER_SMS_SERVICE_ID')),
                'provider': 'twilio' if os.environ.get('TWILIO_ACCOUNT_SID') else 'naver' if os.environ.get('NAVER_SMS_SERVICE_ID') else 'none'
            },
            'kakao': {
                'enabled': bool(os.environ.get('KAKAO_ACCESS_TOKEN')),
                'template_id': os.environ.get('KAKAO_TEMPLATE_ID', ''),
                'to_number': os.environ.get('KAKAO_TO_NUMBER', '')
            }
        }

        return jsonify({
            'success': True,
            'data': settings,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"알림 설정 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@alert_management_bp.route('/test', methods=['POST'])
def test_alert():
    """알림 테스트 전송"""
    try:
        data = request.get_json()
        channel = data.get('channel', 'slack') if data else None
        message = data.get('message', '테스트 알림입니다.') if data else None
        level = data.get('level', 'info') if data else None

        from utils.alert_notifier import send_alert

        # 테스트 알림 전송
        send_alert(message, level=level)

        return jsonify({
            'success': True,
            'message': f'{channel} 채널로 테스트 알림이 전송되었습니다.',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"알림 테스트 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
