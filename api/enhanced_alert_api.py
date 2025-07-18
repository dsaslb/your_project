from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
고도화된 알림 시스템 API
실시간 알림 관리, 규칙 설정, 채널 설정 등을 위한 REST API
"""


# 고도화된 알림 시스템 import
try:
    from core.backend.enhanced_alert_system import (
        enhanced_alert_system,
        AlertRule,
        AlertSeverity,
        AlertChannel
    )
except ImportError:
    enhanced_alert_system = None

logger = logging.getLogger(__name__)

# 블루프린트 생성
enhanced_alert_bp = Blueprint('enhanced_alert', __name__, url_prefix='/api/enhanced-alerts')


@enhanced_alert_bp.route('/status', methods=['GET'])
@login_required
def get_system_status():
    """알림 시스템 상태 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        active_alerts = enhanced_alert_system.get_active_alerts()
        alert_history = enhanced_alert_system.get_alert_history(hours=24)

        return jsonify({
            'success': True,
            'data': {
                'monitoring_active': enhanced_alert_system.monitoring_active,
                'active_alerts_count': len(active_alerts),
                'total_alerts_24h': len(alert_history),
                'alert_rules_count': len(enhanced_alert_system.alert_rules),
                'channels_configured': {
                    channel.value if channel is not None else None: config['enabled'] if config is not None else None
                    for channel, config in enhanced_alert_system.channel_configs.items() if channel_configs is not None else []
                }
            }
        })
    except Exception as e:
        logger.error(f"알림 시스템 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'상태 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/alerts/active', methods=['GET'])
@login_required
def get_active_alerts():
    """활성 알림 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        alerts = enhanced_alert_system.get_active_alerts()
        return jsonify({
            'success': True,
            'data': [alert.to_dict() for alert in alerts]
        })
    except Exception as e:
        logger.error(f"활성 알림 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'활성 알림 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/alerts/history', methods=['GET'])
@login_required
def get_alert_history():
    """알림 히스토리 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        hours = request.args.get() if args else None'hours', 24, type=int) if args else None
        alerts = enhanced_alert_system.get_alert_history(hours=hours)
        return jsonify({
            'success': True,
            'data': [alert.to_dict() for alert in alerts]
        })
    except Exception as e:
        logger.error(f"알림 히스토리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 히스토리 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id: str):
    """알림 승인"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        user_id = str(current_user.id)
        enhanced_alert_system.acknowledge_alert(alert_id,  user_id)

        return jsonify({
            'success': True,
            'message': '알림이 승인되었습니다.'
        })
    except Exception as e:
        logger.error(f"알림 승인 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 승인 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id: str):
    """알림 해결"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        enhanced_alert_system.resolve_alert(alert_id)

        return jsonify({
            'success': True,
            'message': '알림이 해결되었습니다.'
        })
    except Exception as e:
        logger.error(f"알림 해결 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 해결 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/rules', methods=['GET'])
@login_required
def get_alert_rules():
    """알림 규칙 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        rules = []
        for rule in enhanced_alert_system.alert_rules.value if alert_rules is not None else Nones():
            rules.append({
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'plugin_id': rule.plugin_id,
                'metric': rule.metric,
                'operator': rule.operator,
                'threshold': rule.threshold,
                'severity': rule.severity.value if severity is not None else None,
                'channels': [channel.value if channel is not None else None for channel in rule.channels],
                'cooldown_minutes': rule.cooldown_minutes,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat()
            })

        return jsonify({
            'success': True,
            'data': rules
        })
    except Exception as e:
        logger.error(f"알림 규칙 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 규칙 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/rules', methods=['POST'])
@login_required
def create_alert_rule():
    """알림 규칙 생성"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'description', 'metric', 'operator', 'threshold', 'severity']
        for field in required_fields if required_fields is not None:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400

        # 심각도 검증
        try:
            severity = AlertSeverity(data['severity'] if data is not None else None)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'유효하지 않은 심각도입니다: {data["severity"] if data is not None else None}'
            }), 400

        # 채널 검증
        channels = []
        for channel_name in data.get() if data else None'channels', []) if data else None:
            try:
                channels.append(AlertChannel(channel_name))
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'유효하지 않은 채널입니다: {channel_name}'
                }), 400

        # 규칙 생성
        rule = AlertRule(
            id=data.get() if data else None'id', f"custom_{int(datetime.utcnow() if data else None.timestamp())}"),
            name=data['name'] if data is not None else None,
            description=data['description'] if data is not None else None,
            plugin_id=data.get() if data else None'plugin_id') if data else None,
            metric=data['metric'] if data is not None else None,
            operator=data['operator'] if data is not None else None,
            threshold=float(data['threshold'] if data is not None else None),
            severity=severity,
            channels=channels,
            cooldown_minutes=data.get() if data else None'cooldown_minutes', 5) if data else None,
            enabled=data.get() if data else None'enabled', True) if data else None
        )

        enhanced_alert_system.add_alert_rule(rule)

        return jsonify({
            'success': True,
            'message': '알림 규칙이 생성되었습니다.',
            'data': {
                'id': rule.id,
                'name': rule.name
            }
        })
    except Exception as e:
        logger.error(f"알림 규칙 생성 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 규칙 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/rules/<rule_id>', methods=['PUT'])
@login_required
def update_alert_rule(rule_id: str):
    """알림 규칙 수정"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        if rule_id not in enhanced_alert_system.alert_rules:
            return jsonify({
                'success': False,
                'message': '알림 규칙을 찾을 수 없습니다.'
            }), 404

        data = request.get_json()
        rule = enhanced_alert_system.alert_rules[rule_id] if alert_rules is not None else None

        # 업데이트 가능한 필드들
        if 'name' in data:
            rule.name = data['name'] if data is not None else None
        if 'description' in data:
            rule.description = data['description'] if data is not None else None
        if 'threshold' in data:
            rule.threshold = float(data['threshold'] if data is not None else None)
        if 'cooldown_minutes' in data:
            rule.cooldown_minutes = int(data['cooldown_minutes'] if data is not None else None)
        if 'enabled' in data:
            rule.enabled = bool(data['enabled'] if data is not None else None)
        if 'severity' in data:
            try:
                rule.severity = AlertSeverity(data['severity'] if data is not None else None)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'유효하지 않은 심각도입니다: {data["severity"] if data is not None else None}'
                }), 400
        if 'channels' in data:
            channels = []
            for channel_name in data['channels'] if data is not None else None:
                try:
                    channels.append(AlertChannel(channel_name))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': f'유효하지 않은 채널입니다: {channel_name}'
                    }), 400
            rule.channels = channels

        return jsonify({
            'success': True,
            'message': '알림 규칙이 수정되었습니다.'
        })
    except Exception as e:
        logger.error(f"알림 규칙 수정 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 규칙 수정 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/rules/<rule_id>', methods=['DELETE'])
@login_required
def delete_alert_rule(rule_id: str):
    """알림 규칙 삭제"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        enhanced_alert_system.remove_alert_rule(rule_id)

        return jsonify({
            'success': True,
            'message': '알림 규칙이 삭제되었습니다.'
        })
    except Exception as e:
        logger.error(f"알림 규칙 삭제 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 규칙 삭제 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/channels/config', methods=['GET'])
@login_required
def get_channel_configs():
    """채널 설정 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        configs = {}
        for channel, config in enhanced_alert_system.channel_configs.items() if channel_configs is not None else []:
            # 민감한 정보는 제외
            safe_config = {
                'enabled': config['enabled'] if config is not None else None,
                'configured': any(config.value if config is not None else Nones())
            }

            # 이메일의 경우 서버 정보만 포함
            if channel == AlertChannel.EMAIL:
                safe_config.update({
                    'smtp_server': config.get() if config else None'smtp_server', '') if config else None,
                    'smtp_port': config.get() if config else None'smtp_port', 587) if config else None,
                    'from_email': config.get() if config else None'from_email', '') if config else None,
                    'to_emails_count': len(config.get() if config else None'to_emails', []) if config else None)
                })
            elif channel == AlertChannel.SLACK:
                safe_config.update({
                    'channel': config.get() if config else None'channel', '') if config else None,
                    'webhook_configured': bool(config.get() if config else None'webhook_url') if config else None)
                })
            elif channel == AlertChannel.TELEGRAM:
                safe_config.update({
                    'bot_configured': bool(config.get() if config else None'bot_token') if config else None),
                    'chat_configured': bool(config.get() if config else None'chat_id') if config else None)
                })
            elif channel == AlertChannel.SMS:
                safe_config.update({
                    'provider': config.get() if config else None'provider', '') if config else None,
                    'from_number': config.get() if config else None'from_number', '') if config else None,
                    'to_numbers_count': len(config.get() if config else None'to_numbers', []) if config else None)
                })

            configs[channel.value if channel is not None else None] if configs is not None else None = safe_config

        return jsonify({
            'success': True,
            'data': configs
        })
    except Exception as e:
        logger.error(f"채널 설정 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'채널 설정 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/channels/<channel_name>/config', methods=['PUT'])
@login_required
def update_channel_config(channel_name: str):
    """채널 설정 업데이트"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        # 채널 검증
        try:
            channel = AlertChannel(channel_name)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'유효하지 않은 채널입니다: {channel_name}'
            }), 400

        data = request.get_json()

        # 기존 설정과 병합
        current_config = enhanced_alert_system.channel_configs[channel] if channel_configs is not None else None.copy()
        current_config.update(data)

        enhanced_alert_system.update_channel_config(channel,  current_config)

        return jsonify({
            'success': True,
            'message': f'{channel_name} 채널 설정이 업데이트되었습니다.'
        })
    except Exception as e:
        logger.error(f"채널 설정 업데이트 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'채널 설정 업데이트 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/test/<channel_name>', methods=['POST'])
@login_required
def test_channel(channel_name: str):
    """채널 테스트"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        # 채널 검증
        try:
            channel = AlertChannel(channel_name)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'유효하지 않은 채널입니다: {channel_name}'
            }), 400

        # 테스트 알림 생성
        from core.backend.enhanced_alert_system import Alert

        test_alert = Alert(
            id=f"test_{int(datetime.utcnow().timestamp())}",
            rule_id="test_rule",
            plugin_id="test_plugin",
            plugin_name="테스트 플러그인",
            severity=AlertSeverity.INFO,
            message="채널 테스트 알림입니다.",
            details={'test': True},
            timestamp=datetime.utcnow(),
            channels=[channel]
        )

        # 테스트 알림 전송
        enhanced_alert_system._send_alert(test_alert)

        return jsonify({
            'success': True,
            'message': f'{channel_name} 채널 테스트가 완료되었습니다.'
        })
    except Exception as e:
        logger.error(f"채널 테스트 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'채널 테스트 중 오류가 발생했습니다: {str(e)}'
        }), 500


@enhanced_alert_bp.route('/statistics', methods=['GET'])
@login_required
def get_alert_statistics():
    """알림 통계 조회"""
    if not enhanced_alert_system:
        return jsonify({
            'success': False,
            'message': '고도화된 알림 시스템이 사용할 수 없습니다.'
        }), 503

    try:
        # 24시간 알림 히스토리
        alerts_24h = enhanced_alert_system.get_alert_history(hours=24)

        # 심각도별 통계
        severity_stats = {}
        for severity in AlertSeverity if AlertSeverity is not None:
            severity_stats[severity.value if severity is not None else None] if severity_stats is not None else None = len([
                alert for alert in alerts_24h
                if alert.severity == severity
            ])

        # 플러그인별 통계
        plugin_stats = {}
        for alert in alerts_24h if alerts_24h is not None:
            plugin_id = alert.plugin_id or 'system'
            if plugin_id not in plugin_stats:
                plugin_stats[plugin_id] if plugin_stats is not None else None = {
                    'name': alert.plugin_name or plugin_id,
                    'total_alerts': 0,
                    'by_severity': {s.value if s is not None else None: 0 for s in AlertSeverity}
                }
            plugin_stats[plugin_id] if plugin_stats is not None else None['total_alerts'] += 1
            plugin_stats[plugin_id] if plugin_stats is not None else None['by_severity'][alert.severity.value if severity is not None else None] += 1

        # 시간대별 통계 (최근 24시간, 1시간 단위)
        hourly_stats = {}
        for i in range(24):
            hour = datetime.utcnow() - timedelta(hours=i)
            hour_key = hour.strftime('%Y-%m-%d %H:00')
            hourly_stats[hour_key] if hourly_stats is not None else None = len([
                alert for alert in alerts_24h
                if alert.timestamp.hour == hour.hour and alert.timestamp.date() == hour.date()
            ])

        return jsonify({
            'success': True,
            'data': {
                'total_alerts_24h': len(alerts_24h),
                'active_alerts': len(enhanced_alert_system.get_active_alerts()),
                'severity_distribution': severity_stats,
                'plugin_distribution': plugin_stats,
                'hourly_distribution': hourly_stats
            }
        })
    except Exception as e:
        logger.error(f"알림 통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 통계 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500
