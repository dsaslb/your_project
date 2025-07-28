# -*- coding: utf-8 -*-
"""
백엔드 관리자 전용 라우트
업종별 관리자 승인/관리, 플러그인 마켓플레이스, 시스템 모니터링, 보안 관리, 실시간 이벤트/알림, API/DB 문서
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json

from extensions import db
from models_main import IndustryAdmin, Module, SystemLog, Notification, ActionLog, User

# Blueprint 생성
backend_admin_bp = Blueprint('backend_admin', __name__)

@backend_admin_bp.route('/admin/backend')
@login_required
def backend_dashboard():
    """백엔드 관리자 대시보드 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    return render_template('admin/cyberpunk_dashboard.html')

@backend_admin_bp.route('/admin/backend/legacy')
@login_required
def backend_dashboard_legacy():
    """기존 백엔드 관리자 대시보드"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    return render_template('admin/backend_admin_dashboard.html')

@backend_admin_bp.route('/admin/backend/industry-admin')
@login_required
def industry_admin_management():
    """업종별 관리자 승인/관리 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 업종별 관리자 목록 조회
    admins = IndustryAdmin.query.all()
    return render_template('admin/cyberpunk_industry_admin.html', admins=admins)

@backend_admin_bp.route('/admin/backend/plugin-marketplace')
@login_required
def plugin_marketplace():
    """플러그인 마켓플레이스 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 플러그인 목록 조회
    plugins = Module.query.filter_by(status='approved').all()
    return render_template('admin/cyberpunk_plugin_marketplace.html', plugins=plugins)

@backend_admin_bp.route('/admin/backend/plugin-management')
@login_required
def plugin_management():
    """플러그인 관리/개발 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 설치된 플러그인 목록
    installed_plugins = Module.query.filter_by(status='approved').all()
    return render_template('admin/cyberpunk_plugin_management.html', plugins=installed_plugins)

@backend_admin_bp.route('/admin/backend/module-development')
@login_required
def module_development():
    """모듈 개발 시스템 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    return render_template('admin/cyberpunk_module_development.html')

@backend_admin_bp.route('/admin/backend/module-projects')
@login_required
def module_projects():
    """모듈 프로젝트 목록"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    return render_template('admin/module_projects.html')

@backend_admin_bp.route('/admin/backend/system-monitoring')
@login_required
def system_monitoring():
    """시스템/서버 운영/모니터링 - 사이버펑크 스타일"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 시스템 로그 조회
    system_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(100).all()
    return render_template('admin/cyberpunk_system_monitoring.html', logs=system_logs)

@backend_admin_bp.route('/admin/backend/security')
@login_required
def security_management():
    """보안 관리"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 보안 관련 로그 조회
    security_logs = SystemLog.query.filter(
        SystemLog.level.in_(['warning', 'critical'])
    ).order_by(SystemLog.created_at.desc()).limit(50).all()
    
    return render_template('admin/cyberpunk_security_management.html', logs=security_logs)

@backend_admin_bp.route('/admin/backend/events')
@login_required
def events_monitoring():
    """실시간 이벤트/알림"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    # 최근 이벤트 조회
    recent_events = ActionLog.query.order_by(ActionLog.created_at.desc()).limit(50).all()
    notifications = Notification.query.filter_by(is_admin_only=True).order_by(Notification.created_at.desc()).limit(20).all()
    
    return render_template('admin/cyberpunk_events_monitoring.html', events=recent_events, notifications=notifications)

@backend_admin_bp.route('/admin/backend/docs')
@login_required
def api_docs():
    """API/DB 문서"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('auth.login'))
    
    return render_template('admin/api_docs.html')

# API 엔드포인트들
@backend_admin_bp.route('/api/backend/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """백엔드 관리자 대시보드 통계 (인증 불필요)"""
    try:
        from models_main import IndustryAdmin, Module, SystemLog
        from models.plugin_models import PluginInstallation
        from sqlalchemy import func
        
        # 업종별 관리자 통계
        industry_admin_stats = {
            'total_count': IndustryAdmin.query.count(),
            'pending_count': IndustryAdmin.query.filter_by(status='pending').count(),
            'approved_count': IndustryAdmin.query.filter_by(status='approved').count(),
            'rejected_count': IndustryAdmin.query.filter_by(status='rejected').count(),
            'inactive_count': IndustryAdmin.query.filter_by(status='inactive').count()
        }
        
        # 플러그인 통계
        plugin_stats = {
            'total_plugins': Module.query.filter_by(is_marketplace=True).count(),
            'active_plugins': PluginInstallation.query.filter_by(status='active').count(),
            'total_installs': PluginInstallation.query.count(),
            'total_downloads': db.session.query(func.sum(Module.download_count)).filter_by(is_marketplace=True).scalar() or 0
        }
        
        # 시스템 로그 통계
        system_log_stats = {
            'total_logs': SystemLog.query.count(),
            'error_logs': SystemLog.query.filter_by(level='error').count(),
            'warning_logs': SystemLog.query.filter_by(level='warning').count(),
            'critical_logs': SystemLog.query.filter_by(level='critical').count()
        }
        
        return jsonify({
            'industry_admin': industry_admin_stats,
            'plugin': plugin_stats,
            'system_log': system_log_stats
        })
        
    except Exception as e:
        print(f"대시보드 통계 조회 실패: {e}")
        return jsonify({'error': '통계 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/backend/industry-admin/approve/<int:admin_id>', methods=['POST'])
@login_required
def approve_industry_admin(admin_id):
    """업종별 관리자 승인"""
    if not current_user.has_permission('system_management', 'approve'):
        return jsonify({'error': '승인 권한이 없습니다.'}), 403
    
    try:
        admin = IndustryAdmin.query.get_or_404(admin_id)
        admin.approve(current_user.id)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '승인되었습니다.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/industry-admin/reject/<int:admin_id>', methods=['POST'])
@login_required
def reject_industry_admin(admin_id):
    """업종별 관리자 거절"""
    if not current_user.has_permission('system_management', 'approve'):
        return jsonify({'error': '거절 권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        rejection_reason = data.get('reason', '')
        
        admin = IndustryAdmin.query.get_or_404(admin_id)
        admin.reject(current_user.id, rejection_reason)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '거절되었습니다.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/plugin/install/<plugin_id>', methods=['POST'])
@login_required
def install_plugin(plugin_id):
    """플러그인 설치"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '설치 권한이 없습니다.'}), 403
    
    try:
        plugin = Module.query.get_or_404(plugin_id)
        plugin.is_active = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': '플러그인이 설치되었습니다.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/plugin/uninstall/<plugin_id>', methods=['POST'])
@login_required
def uninstall_plugin(plugin_id):
    """플러그인 제거"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '제거 권한이 없습니다.'}), 403
    
    try:
        plugin = Module.query.get_or_404(plugin_id)
        plugin.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': '플러그인이 제거되었습니다.'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/system/logs')
@login_required
def get_system_logs():
    """시스템 로그 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '조회 권한이 없습니다.'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        
        query = SystemLog.query
        
        if level:
            query = query.filter(SystemLog.level == level)
        
        logs = query.order_by(SystemLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [{
                'id': log.id,
                'level': log.level,
                'message': log.message,
                'timestamp': log.timestamp.isoformat(),
                'source': log.source
            } for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/security/alerts')
@login_required
def get_security_alerts():
    """보안 경고 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '조회 권한이 없습니다.'}), 403
    
    try:
        # 최근 24시간 보안 경고
        yesterday = datetime.utcnow() - timedelta(days=1)
        alerts = SystemLog.query.filter(
            SystemLog.level.in_(['warning', 'critical']),
                    SystemLog.created_at >= yesterday
    ).order_by(SystemLog.created_at.desc()).limit(20).all()
        
        return jsonify({
            'alerts': [{
                'id': alert.id,
                'level': alert.level,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'source': alert.source
            } for alert in alerts]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/events/recent')
@login_required
def get_recent_events():
    """최근 이벤트 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '조회 권한이 없습니다.'}), 403
    
    try:
        # 최근 24시간 이벤트
        yesterday = datetime.utcnow() - timedelta(days=1)
        events = ActionLog.query.filter(
                    ActionLog.created_at >= yesterday
    ).order_by(ActionLog.created_at.desc()).limit(30).all()
        
        return jsonify({
            'success': True,
            'events': [{
                'id': event.id,
                'action': event.action,
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details
            } for event in events]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/plugins/list')
@login_required
def get_plugins_list():
    """설치된 플러그인 목록 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '조회 권한이 없습니다.'}), 403
    
    try:
        plugins = Module.query.all()
        
        return jsonify({
            'success': True,
            'plugins': [{
                'id': plugin.id,
                'name': plugin.name,
                'description': plugin.description,
                'version': plugin.version,
                'is_active': plugin.is_active,
                'needs_update': False,  # TODO: 업데이트 체크 로직 구현
                'installed_at': plugin.created_at.isoformat() if plugin.created_at else None
            } for plugin in plugins]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/plugin/toggle/<plugin_id>', methods=['POST'])
@login_required
def toggle_plugin(plugin_id):
    """플러그인 활성화/비활성화"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '수정 권한이 없습니다.'}), 403
    
    try:
        plugin = Module.query.get_or_404(plugin_id)
        plugin.is_active = not plugin.is_active
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'플러그인이 {"활성화" if plugin.is_active else "비활성화"}되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/module/save', methods=['POST'])
@login_required
def save_module():
    """모듈 프로젝트 저장"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '수정 권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        
        # 프로젝트 정보 저장
        project_data = {
            'name': data.get('name', '새 프로젝트'),
            'description': data.get('description', ''),
            'type': data.get('type', 'general'),
            'components': data.get('components', []),
            'created_by': current_user.id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # TODO: 실제 데이터베이스에 저장
        # 임시로 파일로 저장
        import json
        import os
        
        projects_dir = 'data/module_projects'
        os.makedirs(projects_dir, exist_ok=True)
        
        project_id = f"project_{int(datetime.utcnow().timestamp())}"
        project_file = os.path.join(projects_dir, f"{project_id}.json")
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': '프로젝트가 저장되었습니다.'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/module/deploy', methods=['POST'])
@login_required
def deploy_module():
    """모듈 배포"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '수정 권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        
        # 모듈 검증
        if not data.get('components'):
            return jsonify({'error': '배포할 컴포넌트가 없습니다.'}), 400
        
        # 모듈 생성
        module = Module(
            name=data.get('name', '새 모듈'),
            description=data.get('description', ''),
            version='1.0.0',
            is_active=True,
            created_by=current_user.id
        )
        
        db.session.add(module)
        db.session.commit()
        
        # TODO: 실제 모듈 파일 생성 및 배포 로직
        
        return jsonify({
            'success': True,
            'module_id': module.id,
            'message': '모듈이 성공적으로 배포되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@backend_admin_bp.route('/api/backend/module/projects', methods=['GET'])
@login_required
def get_module_projects():
    """모듈 프로젝트 목록 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '조회 권한이 없습니다.'}), 403
    
    try:
        import os
        import json
        
        projects_dir = 'data/module_projects'
        projects = []
        
        if os.path.exists(projects_dir):
            for filename in os.listdir(projects_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(projects_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        project_data['id'] = filename.replace('.json', '')
                        projects.append(project_data)
        
        return jsonify({
            'success': True,
            'projects': projects
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 업종 관리 API 엔드포인트들
@backend_admin_bp.route('/api/admin/industries', methods=['GET'])
@login_required
def get_industries():
    """업종 목록 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry
        
        industries = Industry.query.filter_by(is_active=True).order_by(Industry.name).all()
        
        industries_data = []
        for industry in industries:
            industries_data.append({
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'description': industry.description,
                'icon': industry.icon,
                'color': industry.color,
                'is_active': industry.is_active,
                'created_at': industry.created_at.isoformat() if industry.created_at else None,
                'updated_at': industry.updated_at.isoformat() if industry.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'industries': industries_data
        })
        
    except Exception as e:
        print(f"업종 목록 조회 오류: {e}")
        return jsonify({'error': '업종 목록 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/industries', methods=['POST'])
@login_required
def create_industry():
    """업종 생성"""
    if not current_user.has_permission('system_management', 'create'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, db
        
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': '업종명과 코드는 필수입니다.'}), 400
        
        # 중복 검사
        existing_industry = Industry.query.filter(
            (Industry.name == data['name']) | (Industry.code == data['code'])
        ).first()
        
        if existing_industry:
            return jsonify({'error': '이미 존재하는 업종명 또는 코드입니다.'}), 400
        
        # 새 업종 생성
        new_industry = Industry(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            color=data.get('color', '#4ecdc4'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_industry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 생성되었습니다.',
            'industry': {
                'id': new_industry.id,
                'name': new_industry.name,
                'code': new_industry.code,
                'description': new_industry.description,
                'icon': new_industry.icon,
                'color': new_industry.color,
                'is_active': new_industry.is_active,
                'created_at': new_industry.created_at.isoformat() if new_industry.created_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"업종 생성 오류: {e}")
        return jsonify({'error': '업종 생성에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/industries/<int:industry_id>', methods=['PUT'])
@login_required
def update_industry(industry_id):
    """업종 수정"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, db
        
        industry = Industry.query.get_or_404(industry_id)
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code'):
            return jsonify({'error': '업종명과 코드는 필수입니다.'}), 400
        
        # 중복 검사 (자신 제외)
        existing_industry = Industry.query.filter(
            (Industry.name == data['name']) | (Industry.code == data['code']),
            Industry.id != industry_id
        ).first()
        
        if existing_industry:
            return jsonify({'error': '이미 존재하는 업종명 또는 코드입니다.'}), 400
        
        # 업종 정보 업데이트
        industry.name = data['name']
        industry.code = data['code']
        industry.description = data.get('description', industry.description)
        industry.icon = data.get('icon', industry.icon)
        industry.color = data.get('color', industry.color)
        industry.is_active = data.get('is_active', industry.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 수정되었습니다.',
            'industry': {
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'description': industry.description,
                'icon': industry.icon,
                'color': industry.color,
                'is_active': industry.is_active,
                'updated_at': industry.updated_at.isoformat() if industry.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"업종 수정 오류: {e}")
        return jsonify({'error': '업종 수정에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/industries/<int:industry_id>', methods=['DELETE'])
@login_required
def delete_industry(industry_id):
    """업종 삭제"""
    if not current_user.has_permission('system_management', 'delete'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, db
        
        industry = Industry.query.get_or_404(industry_id)
        
        # 관련 데이터가 있는지 확인
        if industry.brands_list.count() > 0:
            return jsonify({'error': '이 업종에 속한 브랜드가 있어 삭제할 수 없습니다.'}), 400
        
        if industry.users.count() > 0:
            return jsonify({'error': '이 업종에 속한 사용자가 있어 삭제할 수 없습니다.'}), 400
        
        # 업종 삭제 (실제 삭제 대신 비활성화)
        industry.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 비활성화되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"업종 삭제 오류: {e}")
        return jsonify({'error': '업종 삭제에 실패했습니다.'}), 500 