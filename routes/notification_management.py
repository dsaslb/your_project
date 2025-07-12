"""
알림 관리 API
다중 채널 알림, 히스토리, 통계, 템플릿, 규칙 관리
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models.notification_models import (  # type: ignore
    NotificationHistory, NotificationChannel, NotificationTemplate,
    NotificationRule
)
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
            name=channel.name,
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
        
        # 히스토리 저장
        for channel_name, success in results.items():
            history = NotificationHistory(
                title=notification_message.title,
                message=notification_message.message,
                level=notification_message.level,
                channel=channel_name,
                recipient=notification_message.recipient,
                metadata=notification_message.metadata,
                success=success,
                error_message=None if success else "Failed to send notification"
            )
            db.session.add(history)
        
        db.session.commit()
        
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
    """알림 히스토리 조회"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        channel = request.args.get('channel')
        success = request.args.get('success')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 쿼리 빌드
        query = NotificationHistory.query
        
        if level:
            query = query.filter(NotificationHistory.level == level)
        
        if channel:
            query = query.filter(NotificationHistory.channel == channel)
        
        if success is not None:
            query = query.filter(NotificationHistory.success == (success.lower() == 'true'))
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(NotificationHistory.sent_at >= start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(NotificationHistory.sent_at <= end_dt)
            except ValueError:
                pass
        
        # 정렬 및 페이징
        query = query.order_by(NotificationHistory.sent_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'status': 'success',
            'history': [
                {
                    'id': item.id,
                    'title': item.title,
                    'message': item.message,
                    'level': item.level,
                    'channel': item.channel,
                    'recipient': item.recipient,
                    'metadata': item.metadata,
                    'sent_at': item.sent_at.isoformat(),
                    'success': item.success,
                    'error_message': item.error_message
                }
                for item in pagination.items
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/statistics', methods=['GET'])
@login_required
@admin_required
def get_notification_statistics():
    """알림 통계 조회"""
    try:
        # 쿼리 파라미터
        days = request.args.get('days', 7, type=int)
        channel = request.args.get('channel')
        level = request.args.get('level')
        
        # 날짜 범위 계산
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 기본 통계 쿼리
        query = NotificationHistory.query.filter(
            NotificationHistory.sent_at >= start_date,
            NotificationHistory.sent_at <= end_date
        )
        
        if channel:
            query = query.filter(NotificationHistory.channel == channel)
        
        if level:
            query = query.filter(NotificationHistory.level == level)
        
        # 전체 통계
        total_sent = query.count()
        successful_sent = query.filter(NotificationHistory.success == True).count()
        failed_sent = query.filter(NotificationHistory.success == False).count()
        
        # 레벨별 통계
        level_stats = db.session.query(
            NotificationHistory.level,
            func.count(NotificationHistory.id).label('count'),
            func.sum(func.case([(NotificationHistory.success == True, 1)], else_=0)).label('success_count')
        ).filter(
            NotificationHistory.sent_at >= start_date,
            NotificationHistory.sent_at <= end_date
        ).group_by(NotificationHistory.level).all()
        
        # 채널별 통계
        channel_stats = db.session.query(
            NotificationHistory.channel,
            func.count(NotificationHistory.id).label('count'),
            func.sum(func.case([(NotificationHistory.success == True, 1)], else_=0)).label('success_count')
        ).filter(
            NotificationHistory.sent_at >= start_date,
            NotificationHistory.sent_at <= end_date
        ).group_by(NotificationHistory.channel).all()
        
        # 시간별 통계 (최근 24시간)
        hourly_stats = db.session.query(
            func.date_trunc('hour', NotificationHistory.sent_at).label('hour'),
            func.count(NotificationHistory.id).label('count')
        ).filter(
            NotificationHistory.sent_at >= end_date - timedelta(hours=24)
        ).group_by(
            func.date_trunc('hour', NotificationHistory.sent_at)
        ).order_by(
            func.date_trunc('hour', NotificationHistory.sent_at)
        ).all()
        
        return jsonify({
            'status': 'success',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'overall_stats': {
                'total_sent': total_sent,
                'successful_sent': successful_sent,
                'failed_sent': failed_sent,
                'success_rate': (successful_sent / total_sent * 100) if total_sent > 0 else 0
            },
            'level_stats': [
                {
                    'level': stat.level,
                    'count': stat.count,
                    'success_count': stat.success_count,
                    'success_rate': (stat.success_count / stat.count * 100) if stat.count > 0 else 0
                }
                for stat in level_stats
            ],
            'channel_stats': [
                {
                    'channel': stat.channel,
                    'count': stat.count,
                    'success_count': stat.success_count,
                    'success_rate': (stat.success_count / stat.count * 100) if stat.count > 0 else 0
                }
                for stat in channel_stats
            ],
            'hourly_stats': [
                {
                    'hour': stat.hour.isoformat(),
                    'count': stat.count
                }
                for stat in hourly_stats
            ]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/templates', methods=['GET'])
@login_required
@admin_required
def get_templates():
    """알림 템플릿 목록 조회"""
    try:
        templates = NotificationTemplate.query.all()
        return jsonify({
            'status': 'success',
            'templates': [
                {
                    'id': template.id,
                    'name': template.name,
                    'title_template': template.title_template,
                    'message_template': template.message_template,
                    'level': template.level,
                    'channels': template.channels,
                    'variables': template.variables,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat()
                }
                for template in templates
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/templates', methods=['POST'])
@login_required
@admin_required
def create_template():
    """새 알림 템플릿 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'title_template', 'message_template']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # 중복 이름 검사
        existing = NotificationTemplate.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Template name already exists'}), 400
        
        # 템플릿 생성
        template = NotificationTemplate(
            name=data['name'],
            title_template=data['title_template'],
            message_template=data['message_template'],
            level=data.get('level', 'info'),
            channels=data.get('channels', []),
            variables=data.get('variables', {})
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Template created successfully',
            'template_id': template.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/rules', methods=['GET'])
@login_required
@admin_required
def get_rules():
    """알림 규칙 목록 조회"""
    try:
        rules = NotificationRule.query.all()
        return jsonify({
            'status': 'success',
            'rules': [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'description': rule.description,
                    'condition_type': rule.condition_type,
                    'condition_config': rule.condition_config,
                    'template_id': rule.template_id,
                    'enabled': rule.enabled,
                    'cooldown_minutes': rule.cooldown_minutes,
                    'created_at': rule.created_at.isoformat(),
                    'updated_at': rule.updated_at.isoformat()
                }
                for rule in rules
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@notification_bp.route('/rules', methods=['POST'])
@login_required
@admin_required
def create_rule():
    """새 알림 규칙 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'condition_type', 'condition_config']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # 중복 이름 검사
        existing = NotificationRule.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'status': 'error', 'message': 'Rule name already exists'}), 400
        
        # 템플릿 존재 확인
        if 'template_id' in data:
            template = NotificationTemplate.query.get(data['template_id'])
            if not template:
                return jsonify({'status': 'error', 'message': 'Template not found'}), 404
        
        # 규칙 생성
        rule = NotificationRule(
            name=data['name'],
            description=data.get('description', ''),
            condition_type=data['condition_type'],
            condition_config=data['condition_config'],
            template_id=data.get('template_id'),
            enabled=data.get('enabled', True),
            cooldown_minutes=data.get('cooldown_minutes', 0)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Rule created successfully',
            'rule_id': rule.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500 