"""
알림 관리 API
다중 채널 알림, 히스토리, 통계, 템플릿, 규칙 관리
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, NotificationHistory, NotificationChannel, NotificationTemplate, NotificationRule
from utils.notification_channels import notification_manager, NotificationMessage
from utils.auth_decorators import admin_required

notification_bp = Blueprint('notification', __name__, url_prefix='/api/admin/notifications')

@notification_bp.route('/channels', methods=['GET'])
@login_required
@admin_required
def get_channels():
    """알림 채널 목록 조회"""
    try:
        channels = NotificationChannel.query.all()
        return jsonify({
            'status': 'success',
            'channels': [
                {
                    'id': channel.id,
                    'name': channel.name,
                    'type': channel.type,
                    'enabled': channel.enabled,
                    'priority': channel.priority,
                    'created_at': channel.created_at.isoformat(),
                    'updated_at': channel.updated_at.isoformat()
                }
                for channel in channels
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/channels', methods=['POST'])
@login_required
@admin_required
def create_channel():
    """새 알림 채널 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'type', 'config']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # 중복 이름 검사
        existing = NotificationChannel.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Channel name already exists'}), 400
        
        # 채널 생성
        channel = NotificationChannel(
            name=data['name'],
            type=data['type'],
            enabled=data.get('enabled', True),
            config=data['config'],
            priority=data.get('priority', 2)
        )
        
        db.session.add(channel)
        db.session.commit()
        
        # 알림 매니저에도 추가
        notification_manager.add_channel(
            name=channel.name,
            channel_type=channel.type,
            config=channel.config,
            priority=channel.priority,
            enabled=channel.enabled
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Channel created successfully',
            'channel_id': channel.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/channels/<int:channel_id>', methods=['PUT'])
@login_required
@admin_required
def update_channel(channel_id):
    """알림 채널 업데이트"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        data = request.get_json()
        
        # 업데이트할 필드들
        if 'name' in data:
            # 이름 중복 검사
            existing = NotificationChannel.query.filter(
                NotificationChannel.name == data['name'],
                NotificationChannel.id != channel_id
            ).first()
            if existing:
                return jsonify({'status': 'error', 'message': 'Channel name already exists'}), 400
            channel.name = data['name']
        
        if 'type' in data:
            channel.type = data['type']
        
        if 'enabled' in data:
            channel.enabled = data['enabled']
        
        if 'config' in data:
            channel.config = data['config']
        
        if 'priority' in data:
            channel.priority = data['priority']
        
        channel.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 알림 매니저에도 업데이트
        notification_manager.update_channel(
            channel.name,
            type=channel.type,
            enabled=channel.enabled,
            config=channel.config,
            priority=channel.priority
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Channel updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/channels/<int:channel_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_channel(channel_id):
    """알림 채널 삭제"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        
        # 알림 매니저에서도 제거
        notification_manager.remove_channel(channel.name)
        
        db.session.delete(channel)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Channel deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/channels/<int:channel_id>/test', methods=['POST'])
@login_required
@admin_required
def test_channel(channel_id):
    """알림 채널 테스트"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        
        # 테스트 메시지 생성
        test_message = NotificationMessage(
            title="Channel Test",
            message="This is a test notification to verify channel configuration.",
            level="info",
            channel=channel.name
        )
        
        # 알림 전송
        results = notification_manager.send_notification(test_message)
        success = results.get(channel.name, False)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Channel test completed',
            'success': success
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/send', methods=['POST'])
@login_required
@admin_required
def send_notification():
    """알림 전송"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['title', 'message', 'level']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # 메시지 생성
        notification_message = NotificationMessage(
            title=data['title'],
            message=data['message'],
            level=data['level'],
            channel=data.get('channel', ''),
            recipient=data.get('recipient'),
            metadata=data.get('metadata')
        )
        
        # 알림 전송
        results = notification_manager.send_notification(notification_message)
        
        # 히스토리 저장 부분 제거 (개발 단계)
        # TODO: 필요시 NotificationHistory 모델 수정 후 재구현
        
        return jsonify({
            'status': 'success',
            'message': 'Notification sent',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/history', methods=['GET'])
@login_required
@admin_required
def get_notification_history():
    """알림 히스토리 조회 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 빈 응답 반환
        return jsonify({
            'status': 'success',
            'history': [],
            'pagination': {
                'page': 1,
                'per_page': 50,
                'total': 0,
                'pages': 0,
                'has_next': False,
                'has_prev': False
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/statistics', methods=['GET'])
@login_required
@admin_required
def get_notification_statistics():
    """알림 통계 조회 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 기본 통계 반환
        return jsonify({
            'status': 'success',
            'period': {
                'start_date': (datetime.utcnow() - timedelta(days=7)).isoformat(),
                'end_date': datetime.utcnow().isoformat(),
                'days': 7
            },
            'overall_stats': {
                'total_sent': 0,
                'successful_sent': 0,
                'failed_sent': 0,
                'success_rate': 0
            },
            'level_stats': [],
            'channel_stats': [],
            'hourly_stats': []
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/templates', methods=['GET'])
@login_required
@admin_required
def get_templates():
    """알림 템플릿 목록 조회 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 빈 응답 반환
        return jsonify({
            'status': 'success',
            'templates': []
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/templates', methods=['POST'])
@login_required
@admin_required
def create_template():
    """새 알림 템플릿 생성 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 성공 응답만 반환
        return jsonify({
            'status': 'success',
            'message': 'Template created successfully (dev mode)',
            'template_id': 1
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/rules', methods=['GET'])
@login_required
@admin_required
def get_rules():
    """알림 규칙 목록 조회 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 빈 응답 반환
        return jsonify({
            'status': 'success',
            'rules': []
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/rules', methods=['POST'])
@login_required
@admin_required
def create_rule():
    """새 알림 규칙 생성 (개발 단계 - 임시 구현)"""
    try:
        # 개발 단계에서는 성공 응답만 반환
        return jsonify({
            'status': 'success',
            'message': 'Rule created successfully (dev mode)',
            'rule_id': 1
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 