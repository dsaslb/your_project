from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import json
import logging
from datetime import datetime, timedelta
import traceback

# 보안 모듈 import
from security.multi_factor_auth import MultiFactorAuth
from security.data_encryption import DataEncryption
from security.audit_logger import SecurityAuditLogger
from security.threat_detection import ThreatDetection

# Blueprint 생성
security_api = Blueprint('security_api', __name__, url_prefix='/api/security')

# 로깅 설정
logger = logging.getLogger(__name__)

# 보안 모듈 인스턴스
mfa = MultiFactorAuth()
encryption = DataEncryption()
audit_logger = SecurityAuditLogger()
threat_detection = ThreatDetection()

@security_api.route('/mfa/setup', methods=['POST'])
@login_required
def setup_mfa():
    """MFA 설정 API"""
    try:
        # 사용자 ID 가져오기
        user_id = current_user.id if current_user else request.json.get('user_id')
        
        if not user_id:
            return jsonify({'error': '사용자 ID가 필요합니다'}), 400
        
        # MFA 설정
        result = mfa.setup_mfa(user_id)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='mfa_setup',
                user_id=user_id,
                ip_address=request.remote_addr,
                details=f"MFA 설정 완료: {result['secret']}"
            )
            
            return jsonify({
                'success': True,
                'secret': result['secret'],
                'qr_code': result['qr_code'],
                'backup_codes': result['backup_codes']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"MFA 설정 오류: {str(e)}")
        return jsonify({'error': 'MFA 설정 중 오류가 발생했습니다'}), 500

@security_api.route('/mfa/verify', methods=['POST'])
@login_required
def verify_mfa():
    """MFA 인증 API"""
    try:
        data = request.get_json()
        user_id = current_user.id if current_user else data.get('user_id')
        code = data.get('code')
        method = data.get('method', 'totp')  # totp, sms, email
        
        if not user_id or not code:
            return jsonify({'error': '사용자 ID와 인증 코드가 필요합니다'}), 400
        
        # MFA 인증
        result = mfa.verify_mfa(user_id, code, method)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='mfa_verification_success',
                user_id=user_id,
                ip_address=request.remote_addr,
                details=f"MFA 인증 성공: {method}"
            )
            
            return jsonify({'success': True, 'message': 'MFA 인증이 완료되었습니다'})
        else:
            # 실패 로그 기록
            audit_logger.log_event(
                event_type='mfa_verification_failed',
                user_id=user_id,
                ip_address=request.remote_addr,
                details=f"MFA 인증 실패: {method}, 코드: {code}"
            )
            
            return jsonify({'error': result['error']}), 401
            
    except Exception as e:
        logger.error(f"MFA 인증 오류: {str(e)}")
        return jsonify({'error': 'MFA 인증 중 오류가 발생했습니다'}), 500

@security_api.route('/mfa/disable', methods=['POST'])
@login_required
def disable_mfa():
    """MFA 비활성화 API"""
    try:
        user_id = current_user.id if current_user else request.json.get('user_id')
        
        if not user_id:
            return jsonify({'error': '사용자 ID가 필요합니다'}), 400
        
        # MFA 비활성화
        result = mfa.disable_mfa(user_id)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='mfa_disable',
                user_id=user_id,
                ip_address=request.remote_addr,
                details="MFA 비활성화 완료"
            )
            
            return jsonify({'success': True, 'message': 'MFA가 비활성화되었습니다'})
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"MFA 비활성화 오류: {str(e)}")
        return jsonify({'error': 'MFA 비활성화 중 오류가 발생했습니다'}), 500

@security_api.route('/encrypt', methods=['POST'])
@login_required
def encrypt_data():
    """데이터 암호화 API"""
    try:
        data = request.get_json()
        text = data.get('text')
        encryption_type = data.get('type', 'symmetric')  # symmetric, asymmetric
        
        if not text:
            return jsonify({'error': '암호화할 텍스트가 필요합니다'}), 400
        
        # 데이터 암호화
        if encryption_type == 'symmetric':
            result = encryption.encrypt_symmetric(text)
        else:
            result = encryption.encrypt_asymmetric(text)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='data_encryption',
                user_id=current_user.id if current_user else None,
                ip_address=request.remote_addr,
                details=f"데이터 암호화 완료: {encryption_type}"
            )
            
            return jsonify({
                'success': True,
                'encrypted_data': result['encrypted_data'],
                'type': encryption_type
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"데이터 암호화 오류: {str(e)}")
        return jsonify({'error': '데이터 암호화 중 오류가 발생했습니다'}), 500

@security_api.route('/decrypt', methods=['POST'])
@login_required
def decrypt_data():
    """데이터 복호화 API"""
    try:
        data = request.get_json()
        encrypted_data = data.get('encrypted_data')
        encryption_type = data.get('type', 'symmetric')  # symmetric, asymmetric
        
        if not encrypted_data:
            return jsonify({'error': '복호화할 데이터가 필요합니다'}), 400
        
        # 데이터 복호화
        if encryption_type == 'symmetric':
            result = encryption.decrypt_symmetric(encrypted_data)
        else:
            result = encryption.decrypt_asymmetric(encrypted_data)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='data_decryption',
                user_id=current_user.id if current_user else None,
                ip_address=request.remote_addr,
                details=f"데이터 복호화 완료: {encryption_type}"
            )
            
            return jsonify({
                'success': True,
                'decrypted_data': result['decrypted_data'],
                'type': encryption_type
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"데이터 복호화 오류: {str(e)}")
        return jsonify({'error': '데이터 복호화 중 오류가 발생했습니다'}), 500

@security_api.route('/audit-logs', methods=['GET'])
@login_required
def get_audit_logs():
    """감사 로그 조회 API"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 감사 로그 조회
        logs = audit_logger.get_events(
            page=page,
            per_page=per_page,
            event_type=event_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'logs': logs['events'],
            'total': logs['total'],
            'page': page,
            'per_page': per_page,
            'pages': logs['pages']
        })
        
    except Exception as e:
        logger.error(f"감사 로그 조회 오류: {str(e)}")
        return jsonify({'error': '감사 로그 조회 중 오류가 발생했습니다'}), 500

@security_api.route('/audit-logs/export', methods=['GET'])
@login_required
def export_audit_logs():
    """감사 로그 내보내기 API"""
    try:
        format_type = request.args.get('format', 'json')  # json, csv
        event_type = request.args.get('event_type')
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 감사 로그 내보내기
        result = audit_logger.export_logs(
            format_type=format_type,
            event_type=event_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'download_url': result['download_url'],
                'filename': result['filename']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"감사 로그 내보내기 오류: {str(e)}")
        return jsonify({'error': '감사 로그 내보내기 중 오류가 발생했습니다'}), 500

@security_api.route('/threats', methods=['GET'])
@login_required
def get_threats():
    """위협 탐지 로그 조회 API"""
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        threat_type = request.args.get('threat_type')
        ip_address = request.args.get('ip_address')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 위협 로그 조회
        threats = threat_detection.get_threats(
            page=page,
            per_page=per_page,
            threat_type=threat_type,
            ip_address=ip_address,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'threats': threats['threats'],
            'total': threats['total'],
            'page': page,
            'per_page': per_page,
            'pages': threats['pages']
        })
        
    except Exception as e:
        logger.error(f"위협 로그 조회 오류: {str(e)}")
        return jsonify({'error': '위협 로그 조회 중 오류가 발생했습니다'}), 500

@security_api.route('/threats/block-ip', methods=['POST'])
@login_required
def block_ip():
    """IP 차단 API"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        reason = data.get('reason', '관리자에 의한 수동 차단')
        duration = data.get('duration', 3600)  # 초 단위
        
        if not ip_address:
            return jsonify({'error': 'IP 주소가 필요합니다'}), 400
        
        # IP 차단
        result = threat_detection.block_ip(ip_address, reason, duration)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='ip_blocked',
                user_id=current_user.id if current_user else None,
                ip_address=request.remote_addr,
                details=f"IP 차단: {ip_address}, 사유: {reason}, 기간: {duration}초"
            )
            
            return jsonify({'success': True, 'message': f'IP {ip_address}가 차단되었습니다'})
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"IP 차단 오류: {str(e)}")
        return jsonify({'error': 'IP 차단 중 오류가 발생했습니다'}), 500

@security_api.route('/threats/unblock-ip', methods=['POST'])
@login_required
def unblock_ip():
    """IP 차단 해제 API"""
    try:
        data = request.get_json()
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return jsonify({'error': 'IP 주소가 필요합니다'}), 400
        
        # IP 차단 해제
        result = threat_detection.unblock_ip(ip_address)
        
        if result['success']:
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='ip_unblocked',
                user_id=current_user.id if current_user else None,
                ip_address=request.remote_addr,
                details=f"IP 차단 해제: {ip_address}"
            )
            
            return jsonify({'success': True, 'message': f'IP {ip_address}의 차단이 해제되었습니다'})
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        logger.error(f"IP 차단 해제 오류: {str(e)}")
        return jsonify({'error': 'IP 차단 해제 중 오류가 발생했습니다'}), 500

@security_api.route('/security-status', methods=['GET'])
@login_required
def get_security_status():
    """보안 상태 조회 API"""
    try:
        # 현재 보안 상태 정보 수집
        status = {
            'mfa_enabled_users': mfa.get_enabled_users_count(),
            'active_threats': threat_detection.get_active_threats_count(),
            'blocked_ips': threat_detection.get_blocked_ips_count(),
            'recent_audit_events': audit_logger.get_recent_events_count(),
            'encryption_status': encryption.get_status(),
            'system_health': {
                'mfa_system': mfa.is_healthy(),
                'encryption_system': encryption.is_healthy(),
                'audit_system': audit_logger.is_healthy(),
                'threat_detection_system': threat_detection.is_healthy()
            }
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"보안 상태 조회 오류: {str(e)}")
        return jsonify({'error': '보안 상태 조회 중 오류가 발생했습니다'}), 500

@security_api.route('/security-settings', methods=['GET', 'PUT'])
@login_required
def security_settings():
    """보안 설정 API"""
    try:
        if request.method == 'GET':
            # 현재 보안 설정 조회
            settings = {
                'mfa_settings': mfa.get_settings(),
                'encryption_settings': encryption.get_settings(),
                'audit_settings': audit_logger.get_settings(),
                'threat_detection_settings': threat_detection.get_settings()
            }
            
            return jsonify({
                'success': True,
                'settings': settings
            })
            
        elif request.method == 'PUT':
            # 보안 설정 업데이트
            data = request.get_json()
            
            # 각 모듈별 설정 업데이트
            if 'mfa_settings' in data:
                mfa.update_settings(data['mfa_settings'])
            
            if 'encryption_settings' in data:
                encryption.update_settings(data['encryption_settings'])
            
            if 'audit_settings' in data:
                audit_logger.update_settings(data['audit_settings'])
            
            if 'threat_detection_settings' in data:
                threat_detection.update_settings(data['threat_detection_settings'])
            
            # 감사 로그 기록
            audit_logger.log_event(
                event_type='security_settings_updated',
                user_id=current_user.id if current_user else None,
                ip_address=request.remote_addr,
                details="보안 설정 업데이트"
            )
            
            return jsonify({'success': True, 'message': '보안 설정이 업데이트되었습니다'})
            
    except Exception as e:
        logger.error(f"보안 설정 오류: {str(e)}")
        return jsonify({'error': '보안 설정 처리 중 오류가 발생했습니다'}), 500

# 에러 핸들러
@security_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': '요청한 리소스를 찾을 수 없습니다'}), 404

@security_api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '내부 서버 오류가 발생했습니다'}), 500
