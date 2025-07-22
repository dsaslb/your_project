from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta

# 보안 모듈 import
from security.multi_factor_auth import MultiFactorAuth
from security.data_encryption import DataEncryption
from security.audit_logger import SecurityAuditLogger
from security.threat_detection import ThreatDetection

# Blueprint 생성
security_dashboard = Blueprint('security_dashboard', __name__)

# 로깅 설정
logger = logging.getLogger(__name__)

# 보안 모듈 인스턴스
mfa = MultiFactorAuth()
encryption = DataEncryption()
audit_logger = SecurityAuditLogger()
threat_detection = ThreatDetection()

@security_dashboard.route('/admin/security')
@login_required
def security_dashboard_page():
    """보안 대시보드 메인 페이지"""
    try:
        # 기본 보안 상태 정보
        security_status = {
            'mfa_enabled_users': mfa.get_enabled_users_count(),
            'active_threats': threat_detection.get_active_threats_count(),
            'blocked_ips': threat_detection.get_blocked_ips_count(),
            'recent_audit_events': audit_logger.get_recent_events_count(),
            'system_health': {
                'mfa_system': mfa.is_healthy(),
                'encryption_system': encryption.is_healthy(),
                'audit_system': audit_logger.is_healthy(),
                'threat_detection_system': threat_detection.is_healthy()
            }
        }
        
        return render_template('admin/security_dashboard.html', 
                             security_status=security_status,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"보안 대시보드 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/mfa-management')
@login_required
def mfa_management():
    """MFA 관리 페이지"""
    try:
        # MFA 설정된 사용자 목록
        mfa_users = mfa.get_enabled_users()
        
        return render_template('admin/mfa_management.html',
                             mfa_users=mfa_users,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"MFA 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/encryption-management')
@login_required
def encryption_management():
    """암호화 관리 페이지"""
    try:
        # 암호화 시스템 상태
        encryption_status = encryption.get_status()
        
        return render_template('admin/encryption_management.html',
                             encryption_status=encryption_status,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"암호화 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/audit-management')
@login_required
def audit_management():
    """감사 로그 관리 페이지"""
    try:
        # 최근 감사 이벤트 통계
        audit_stats = audit_logger.get_statistics()
        
        return render_template('admin/audit_management.html',
                             audit_stats=audit_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"감사 로그 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/threat-management')
@login_required
def threat_management():
    """위협 탐지 관리 페이지"""
    try:
        # 위협 탐지 통계
        threat_stats = threat_detection.get_statistics()
        
        return render_template('admin/threat_management.html',
                             threat_stats=threat_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"위협 탐지 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/settings')
@login_required
def security_settings():
    """보안 설정 페이지"""
    try:
        # 현재 보안 설정
        settings = {
            'mfa_settings': mfa.get_settings(),
            'encryption_settings': encryption.get_settings(),
            'audit_settings': audit_logger.get_settings(),
            'threat_detection_settings': threat_detection.get_settings()
        }
        
        return render_template('admin/security_settings.html',
                             settings=settings,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"보안 설정 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@security_dashboard.route('/admin/security/reports')
@login_required
def security_reports():
    """보안 리포트 페이지"""
    try:
        # 보안 리포트 데이터
        report_data = {
            'daily_threats': threat_detection.get_daily_threats(),
            'weekly_audit_summary': audit_logger.get_weekly_summary(),
            'mfa_adoption_rate': mfa.get_adoption_rate(),
            'encryption_usage': encryption.get_usage_statistics()
        }
        
        return render_template('admin/security_reports.html',
                             report_data=report_data,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"보안 리포트 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

# 에러 핸들러
@security_dashboard.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@security_dashboard.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html', error=str(error)), 500 