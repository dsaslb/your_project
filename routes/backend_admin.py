# -*- coding: utf-8 -*-
"""
백엔드 관리자 전용 라우트
업종별 관리자 승인/관리, 플러그인 마켓플레이스, 시스템 모니터링, 보안 관리, 실시간 이벤트/알림, API/DB 문서
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, g, flash
from flask_login import login_required, current_user
from extensions import csrf
from datetime import datetime, timedelta
import json

from extensions import db
from models_main import IndustryAdmin, Module, SystemLog, Notification, ActionLog, User
from utils.cache_manager import cache_manager, cached

# Blueprint 생성
backend_admin_bp = Blueprint('backend_admin', __name__)

@backend_admin_bp.route('/admin/backend')
def backend_dashboard():
    """백엔드 관리자 대시보드"""
    if not current_user.has_permission('system_management', 'view'):
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('dashboard'))
    
    # 캐시된 공통 데이터 사용
    common_data = getattr(g, 'common_data', {})
    admin_stats = common_data.get('admin_stats', {})
    system_status = common_data.get('system_status', {})
    
    return render_template('admin/cyberpunk_dashboard.html', 
                         admin_stats=admin_stats,
                         system_status=system_status)

@backend_admin_bp.route('/admin/backend/legacy')
def backend_dashboard_legacy():
    """기존 백엔드 관리자 대시보드"""
    if not current_user.has_permission('system_management', 'view'):
        return redirect(url_for('dashboard'))
    
    return render_template('admin/backend_admin_dashboard.html')

@backend_admin_bp.route('/admin/backend/industry-admin')
def industry_admin_management():
    """업종별 관리자 승인/관리 - 사이버펑크 스타일"""
    # 업종별 관리자 목록 조회
    admins = IndustryAdmin.query.all()
    return render_template('admin/cyberpunk_industry_admin.html', admins=admins)

@backend_admin_bp.route('/admin/backend/plugin-marketplace')
def plugin_marketplace():
    """플러그인 마켓플레이스 - 사이버펑크 스타일"""
    # 플러그인 목록 조회
    plugins = Module.query.filter_by(status='approved').all()
    return render_template('admin/cyberpunk_plugin_marketplace.html', plugins=plugins)

@backend_admin_bp.route('/admin/backend/plugin-management')
def plugin_management():
    """플러그인 관리/개발 - 사이버펑크 스타일"""
    # 설치된 플러그인 목록
    installed_plugins = Module.query.filter_by(status='approved').all()
    return render_template('admin/cyberpunk_plugin_management.html', plugins=installed_plugins)

@backend_admin_bp.route('/admin/backend/module-development')
def module_development():
    """모듈 개발 시스템 - 사이버펑크 스타일"""
    return render_template('admin/cyberpunk_module_development.html')

@backend_admin_bp.route('/admin/backend/module-projects')
def module_projects():
    """모듈 프로젝트 목록"""
    return render_template('admin/module_projects.html')

@backend_admin_bp.route('/admin/backend/system-monitoring')
def system_monitoring():
    """시스템/서버 운영/모니터링 - 사이버펑크 스타일"""
    # 시스템 로그 조회
    system_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(100).all()
    return render_template('admin/cyberpunk_system_monitoring.html', logs=system_logs)

@backend_admin_bp.route('/admin/backend/security')
def security_management():
    """보안 관리 - 사이버펑크 스타일"""
    return render_template('admin/cyberpunk_security_management.html')

@backend_admin_bp.route('/admin/backend/events')
def events_monitoring():
    """실시간 이벤트/알림 모니터링 - 사이버펑크 스타일"""
    return render_template('admin/cyberpunk_events_monitoring.html')

@backend_admin_bp.route('/admin/backend/docs')
def api_docs():
    """API/DB 문서 - 사이버펑크 스타일"""
    return render_template('admin/cyberpunk_api_docs.html')

# API 엔드포인트들

@backend_admin_bp.route('/api/admin/dashboard-stats')
@cached(expire=300, key_prefix="dashboard_stats")  # 5분 캐시
def get_dashboard_stats():
    """대시보드 통계 데이터 (캐시 적용)"""
    try:
        from models_main import User, Brand, Branch, Industry, Module
        
        # 캐시된 데이터 사용
        common_data = getattr(g, 'common_data', {})
        admin_stats = common_data.get('admin_stats', {})
        
        if not admin_stats:
            # 캐시가 없으면 새로 계산
            admin_stats = {
                'total_users': User.query.count(),
                'total_brands': Brand.query.count(),
                'total_branches': Branch.query.count(),
                'total_industries': Industry.query.count(),
                'active_users': User.query.filter_by(status='approved').count(),
                'pending_users': User.query.filter_by(status='pending').count(),
                'active_modules': Module.query.filter_by(status='approved').count(),
                # 역할별 사용자 통계 추가
                'role_stats': {
                    'admin': User.query.filter_by(role='admin').count(),
                    'brand_admin': User.query.filter_by(role='brand_admin').count(),
                    'store_admin': User.query.filter_by(role='store_admin').count(),
                    'employee': User.query.filter_by(role='employee').count(),
                    'manager': User.query.filter_by(role='manager').count()
                },
                # 브랜드별 매장 통계
                'brand_stats': {
                    'total_brands': Brand.query.count(),
                    'active_brands': Brand.query.filter_by(status='active').count(),
                    'total_branches': Branch.query.count(),
                    'active_branches': Branch.query.filter_by(status='active').count()
                },
                'updated_at': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'stats': admin_stats
        })
        
    except Exception as e:
        print(f"대시보드 통계 조회 오류: {e}")
        return jsonify({'error': '통계 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/system-status')
@cached(expire=60, key_prefix="system_status")  # 1분 캐시
def get_system_status():
    """시스템 상태 (캐시 적용)"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        # 캐시된 데이터 사용
        common_data = getattr(g, 'common_data', {})
        system_status = common_data.get('system_status', {})
        
        if not system_status:
            # 캐시가 없으면 새로 계산
            import psutil
            system_status = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
                'updated_at': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'status': system_status
        })
        
    except Exception as e:
        print(f"시스템 상태 조회 오류: {e}")
        return jsonify({'error': '시스템 상태 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/backend/industry-admin/approve/<int:admin_id>', methods=['POST'])
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
def get_industries():
    """업종 목록 조회"""
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
            'data': industries_data
        })
        
    except Exception as e:
        print(f"업종 목록 조회 오류: {e}")
        return jsonify({'error': '업종 목록 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/industries', methods=['POST'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def create_industry():
    """업종 생성 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'create'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, db
        
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Request body: {request.get_data()}")
        print(f"Request is_json: {request.is_json}")
        
        try:
            data = request.get_json()
            print(f"업종 생성 요청 데이터: {data}")
        except Exception as json_error:
            print(f"JSON 파싱 오류: {json_error}")
            return jsonify({'error': f'JSON 파싱 오류: {str(json_error)}'}), 400
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code'):
            print(f"필수 필드 누락: name={data.get('name')}, code={data.get('code')}")
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
            is_active=data.get('status', 'active') == 'active'
        )
        
        db.session.add(new_industry)
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache()
            cache_manager.invalidate_admin_cache()
        
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
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'업종 생성에 실패했습니다: {str(e)}'}), 500

@backend_admin_bp.route('/api/admin/industries/<int:industry_id>', methods=['PUT'])
@login_required
def update_industry(industry_id):
    """업종 수정 (캐시 무효화)"""
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
        industry.is_active = data.get('status', 'active') == 'active'
        
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache(industry_id)
            cache_manager.invalidate_admin_cache()
        
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
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def delete_industry(industry_id):
    """업종 삭제 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'delete'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, db
        import traceback
        
        print(f"업종 삭제 시작: ID {industry_id}")
        
        industry = Industry.query.get_or_404(industry_id)
        print(f"업종 찾음: {industry.name}")
        
        # 관련 데이터 확인 (임시로 비활성화)
        # try:
        #     brands_count = industry.brands_list.count() if hasattr(industry, 'brands_list') else 0
        #     print(f"관련 브랜드 수: {brands_count}")
        # except Exception as e:
        #     print(f"브랜드 수 확인 오류: {e}")
        #     brands_count = 0
        
        # try:
        #     users_count = industry.users.count() if hasattr(industry, 'users') else 0
        #     print(f"관련 사용자 수: {users_count}")
        # except Exception as e:
        #     print(f"사용자 수 확인 오류: {e}")
        #     users_count = 0
        
        # if brands_count > 0:
        #     return jsonify({'error': '이 업종에 속한 브랜드가 있어 삭제할 수 없습니다.'}), 400
        
        # if users_count > 0:
        #     return jsonify({'error': '이 업종에 속한 사용자가 있어 삭제할 수 없습니다.'}), 400
        
        # 업종 삭제 (실제 삭제 대신 비활성화)
        print(f"업종 비활성화 전: is_active = {industry.is_active}")
        industry.is_active = False
        print(f"업종 비활성화 후: is_active = {industry.is_active}")
        
        db.session.commit()
        print("데이터베이스 커밋 완료")
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache(industry_id)
            cache_manager.invalidate_admin_cache()
        
        return jsonify({
            'success': True,
            'message': '업종이 성공적으로 비활성화되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"업종 삭제 오류: {e}")
        print(f"오류 상세: {traceback.format_exc()}")
        return jsonify({'error': '업종 삭제에 실패했습니다.'}), 500 

# 브랜드 관리 API
@backend_admin_bp.route('/api/admin/brands', methods=['GET'])
def get_brands():
    """브랜드 목록 조회 (캐시 적용)"""
    try:
        from models_main import Brand, Industry
        
        brands = Brand.query.filter_by(status="active").order_by(Brand.name).all()
        
        brands_data = []
        for brand in brands:
            industry = Industry.query.get(brand.industry_id)
            brands_data.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'industry_id': brand.industry_id,
                'industry_name': industry.name if industry else None,
                'is_active': brand.status == "active",
                'branch_count': brand.branches.count() if hasattr(brand, 'branches') else 0,
                'created_at': brand.created_at.isoformat() if brand.created_at else None,
                'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': brands_data
        })
        
    except Exception as e:
        import traceback
        print(f"브랜드 목록 조회 오류: {e}")
        print(f"오류 상세: {traceback.format_exc()}")
        return jsonify({'error': '브랜드 목록 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/brands', methods=['POST'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def create_brand():
    """브랜드 생성 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'create'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Brand, Industry, db
        
        print(f"브랜드 생성 요청 데이터: {request.get_data()}")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Request is_json: {request.is_json}")
        
        try:
            data = request.get_json()
            print(f"브랜드 생성 요청 데이터: {data}")
        except Exception as json_error:
            print(f"JSON 파싱 오류: {json_error}")
            return jsonify({'error': f'JSON 파싱 오류: {str(json_error)}'}), 400
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code') or not data.get('industry_id'):
            return jsonify({'error': '브랜드명, 코드, 업종은 필수입니다.'}), 400
        
        # 업종 존재 확인
        industry = Industry.query.get(data['industry_id'])
        if not industry:
            return jsonify({'error': '존재하지 않는 업종입니다.'}), 400
        
        # 중복 검사
        existing_brand = Brand.query.filter(
            (Brand.name == data['name']) | (Brand.code == data['code'])
        ).first()
        
        if existing_brand:
            return jsonify({'error': '이미 존재하는 브랜드명 또는 코드입니다.'}), 400
        
        # 새 브랜드 생성
        new_brand = Brand(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            industry_id=data['industry_id'],
            status=data.get('status', 'active')
        )
        
        db.session.add(new_brand)
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache()
            cache_manager.clear_pattern('brands_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'brand': {
                'id': new_brand.id,
                'name': new_brand.name,
                'code': new_brand.code,
                'description': new_brand.description,
                'industry_id': new_brand.industry_id,
                'status': new_brand.status,
                'created_at': new_brand.created_at.isoformat() if new_brand.created_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"브랜드 생성 오류: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'브랜드 생성에 실패했습니다: {str(e)}'}), 500

@backend_admin_bp.route('/api/admin/brands/<int:brand_id>', methods=['PUT'])
@login_required
def update_brand(brand_id):
    """브랜드 수정 (캐시 무효화)"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Brand, Industry, db
        
        brand = Brand.query.get_or_404(brand_id)
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('code') or not data.get('industry_id'):
            return jsonify({'error': '브랜드명, 코드, 업종은 필수입니다.'}), 400
        
        # 업종 존재 확인
        industry = Industry.query.get(data['industry_id'])
        if not industry:
            return jsonify({'error': '존재하지 않는 업종입니다.'}), 400
        
        # 중복 검사 (자신 제외)
        existing_brand = Brand.query.filter(
            (Brand.name == data['name']) | (Brand.code == data['code']),
            Brand.id != brand_id
        ).first()
        
        if existing_brand:
            return jsonify({'error': '이미 존재하는 브랜드명 또는 코드입니다.'}), 400
        
        # 브랜드 정보 업데이트
        brand.name = data['name']
        brand.code = data['code']
        brand.description = data.get('description', brand.description)
        brand.industry_id = data['industry_id']
        brand.status = data.get('status', 'active')
        
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache()
            cache_manager.clear_pattern('brands_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 수정되었습니다.',
            'brand': {
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'description': brand.description,
                'industry_id': brand.industry_id,
                'status': brand.status,
                'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"브랜드 수정 오류: {e}")
        return jsonify({'error': '브랜드 수정에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/brands/<int:brand_id>', methods=['DELETE'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def delete_brand(brand_id):
    """브랜드 삭제 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'delete'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Brand, db
        
        brand = Brand.query.get_or_404(brand_id)
        print(f"브랜드 찾음: {brand.name}")
        
        # 관련 데이터 확인 (임시로 비활성화)
        # if brand.branches.count() > 0:
        #     return jsonify({'error': '이 브랜드에 속한 매장이 있어 삭제할 수 없습니다.'}), 400
        
        # 브랜드 삭제 (실제 삭제 대신 비활성화)
        brand.status = 'inactive'
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache()
            cache_manager.clear_pattern('brands_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 비활성화되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"브랜드 삭제 오류: {e}")
        return jsonify({'error': '브랜드 삭제에 실패했습니다.'}), 500

# 매장 관리 API
@backend_admin_bp.route('/api/admin/branches', methods=['GET'])
@cached(expire=1800, key_prefix="branches_list")  # 30분 캐시
def get_branches():
    """매장 목록 조회 (캐시 적용)"""
    try:
        from models_main import Branch, Brand
        
        branches = Branch.query.filter_by(status="active").order_by(Branch.name).all()
        
        branches_data = []
        for branch in branches:
            brand = Brand.query.get(branch.brand_id)
            branches_data.append({
                'id': branch.id,
                'name': branch.name,
                'store_code': branch.store_code,
                'address': branch.address,
                'phone': branch.phone,
                'brand_id': branch.brand_id,
                'brand_name': brand.name if brand else None,
                'is_active': branch.status == "active",
                'user_count': len(branch.users) if hasattr(branch, 'users') and branch.users else 0,
                'created_at': branch.created_at.isoformat() if branch.created_at else None,
                'updated_at': branch.updated_at.isoformat() if branch.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': branches_data
        })
        
    except Exception as e:
        print(f"매장 목록 조회 오류: {e}")
        return jsonify({'error': '매장 목록 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/branches', methods=['POST'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def create_branch():
    """매장 생성 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'create'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Branch, Brand, db
        
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('store_code') or not data.get('brand_id'):
            return jsonify({'error': '매장명, 매장코드, 브랜드는 필수입니다.'}), 400
        
        # 브랜드 존재 확인
        brand = Brand.query.get(data['brand_id'])
        if not brand:
            return jsonify({'error': '존재하지 않는 브랜드입니다.'}), 400
        
        # 중복 검사
        existing_branch = Branch.query.filter(
            (Branch.name == data['name']) | (Branch.store_code == data['store_code'])
        ).first()
        
        if existing_branch:
            return jsonify({'error': '이미 존재하는 매장명 또는 매장코드입니다.'}), 400
        
        # 새 매장 생성
        new_branch = Branch(
            name=data['name'],
            store_code=data['store_code'],
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            brand_id=data['brand_id'],
            status=data.get('status', True)
        )
        
        db.session.add(new_branch)
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('branches_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 생성되었습니다.',
            'branch': {
                'id': new_branch.id,
                'name': new_branch.name,
                'store_code': new_branch.store_code,
                'address': new_branch.address,
                'phone': new_branch.phone,
                'brand_id': new_branch.brand_id,
                'is_active': new_branch.status == 'active',
                'created_at': new_branch.created_at.isoformat() if new_branch.created_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"매장 생성 오류: {e}")
        return jsonify({'error': '매장 생성에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/branches/<int:branch_id>', methods=['PUT'])
@login_required
def update_branch(branch_id):
    """매장 수정 (캐시 무효화)"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Branch, Brand, db
        
        branch = Branch.query.get_or_404(branch_id)
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('name') or not data.get('store_code') or not data.get('brand_id'):
            return jsonify({'error': '매장명, 매장코드, 브랜드는 필수입니다.'}), 400
        
        # 브랜드 존재 확인
        brand = Brand.query.get(data['brand_id'])
        if not brand:
            return jsonify({'error': '존재하지 않는 브랜드입니다.'}), 400
        
        # 중복 검사 (자신 제외)
        existing_branch = Branch.query.filter(
            (Branch.name == data['name']) | (Branch.store_code == data['store_code']),
            Branch.id != branch_id
        ).first()
        
        if existing_branch:
            return jsonify({'error': '이미 존재하는 매장명 또는 매장코드입니다.'}), 400
        
        # 매장 정보 업데이트
        branch.name = data['name']
        branch.store_code = data['store_code']
        branch.address = data.get('address', branch.address)
        branch.phone = data.get('phone', branch.phone)
        branch.brand_id = data['brand_id']
        branch.status = data.get('status', True)
        
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('branches_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 수정되었습니다.',
            'branch': {
                'id': branch.id,
                'name': branch.name,
                'store_code': branch.store_code,
                'address': branch.address,
                'phone': branch.phone,
                'brand_id': branch.brand_id,
                'is_active': branch.status == 'active',
                'updated_at': branch.updated_at.isoformat() if branch.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"매장 수정 오류: {e}")
        return jsonify({'error': '매장 수정에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/branches/<int:branch_id>', methods=['DELETE'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def delete_branch(branch_id):
    """매장 삭제 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'delete'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Branch, db
        
        branch = Branch.query.get_or_404(branch_id)
        print(f"매장 찾음: {branch.name}")
        
        # 관련 데이터 확인 (임시로 비활성화)
        # if branch.users.count() > 0:
        #     return jsonify({'error': '이 매장에 속한 직원이 있어 삭제할 수 없습니다.'}), 400
        
        # 매장 삭제 (실제 삭제 대신 비활성화)
        branch.status = 'inactive'
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('branches_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 비활성화되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"매장 삭제 오류: {e}")
        return jsonify({'error': '매장 삭제에 실패했습니다.'}), 500

# 직원 관리 API
@backend_admin_bp.route('/api/admin/employees', methods=['GET'])
@cached(expire=1800, key_prefix="employees_list")  # 30분 캐시
def get_employees():
    """직원 목록 조회 (캐시 적용)"""
    try:
        from models_main import User, Branch
        
        employees = User.query.filter_by(role='employee', status='approved').order_by(User.username).all()
        
        employees_data = []
        for employee in employees:
            branch = Branch.query.get(employee.branch_id) if employee.branch_id else None
            employees_data.append({
                'id': employee.id,
                'username': employee.username,
                'email': employee.email,
                'role': employee.role,
                'status': employee.status,
                'branch_id': employee.branch_id,
                'branch_name': branch.name if branch else None,
                'created_at': employee.created_at.isoformat() if employee.created_at else None,
                'updated_at': employee.updated_at.isoformat() if employee.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': employees_data
        })
        
    except Exception as e:
        print(f"직원 목록 조회 오류: {e}")
        return jsonify({'error': '직원 목록 조회에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/employees', methods=['POST'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def create_employee():
    """직원 생성 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'create'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import User, Branch, db
        from werkzeug.security import generate_password_hash
        
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('username') or not data.get('email') or not data.get('password') or not data.get('branch_id'):
            return jsonify({'error': '직원명, 이메일, 비밀번호, 매장은 필수입니다.'}), 400
        
        # 매장 존재 확인
        branch = Branch.query.get(data['branch_id'])
        if not branch:
            return jsonify({'error': '존재하지 않는 매장입니다.'}), 400
        
        # 중복 검사
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': '이미 존재하는 직원명 또는 이메일입니다.'}), 400
        
        # 새 직원 생성
        new_employee = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'employee'),
            status=data.get('status', True),
            branch_id=data['branch_id']
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('employees_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 생성되었습니다.',
            'employee': {
                'id': new_employee.id,
                'username': new_employee.username,
                'email': new_employee.email,
                'role': new_employee.role,
                'status': new_employee.status,
                'branch_id': new_employee.branch_id,
                'created_at': new_employee.created_at.isoformat() if new_employee.created_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"직원 생성 오류: {e}")
        return jsonify({'error': '직원 생성에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/employees/<int:employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    """직원 수정 (캐시 무효화)"""
    if not current_user.has_permission('system_management', 'edit'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import User, Branch, db
        from werkzeug.security import generate_password_hash
        
        employee = User.query.get_or_404(employee_id)
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get('username') or not data.get('email') or not data.get('branch_id'):
            return jsonify({'error': '직원명, 이메일, 매장은 필수입니다.'}), 400
        
        # 매장 존재 확인
        branch = Branch.query.get(data['branch_id'])
        if not branch:
            return jsonify({'error': '존재하지 않는 매장입니다.'}), 400
        
        # 중복 검사 (자신 제외)
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email']),
            User.id != employee_id
        ).first()
        
        if existing_user:
            return jsonify({'error': '이미 존재하는 직원명 또는 이메일입니다.'}), 400
        
        # 직원 정보 업데이트
        employee.username = data['username']
        employee.email = data['email']
        employee.role = data.get('role', employee.role)
        employee.status = data.get('status', employee.status)
        employee.branch_id = data['branch_id']
        
        # 비밀번호가 제공된 경우에만 업데이트
        if data.get('password'):
            employee.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('employees_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 수정되었습니다.',
            'employee': {
                'id': employee.id,
                'username': employee.username,
                'email': employee.email,
                'role': employee.role,
                'status': employee.status,
                'branch_id': employee.branch_id,
                'updated_at': employee.updated_at.isoformat() if employee.updated_at else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"직원 수정 오류: {e}")
        return jsonify({'error': '직원 수정에 실패했습니다.'}), 500

@backend_admin_bp.route('/api/admin/employees/<int:employee_id>', methods=['DELETE'])
# @login_required  # 임시로 주석 처리
@csrf.exempt  # CSRF 보호 비활성화
def delete_employee(employee_id):
    """직원 삭제 (캐시 무효화)"""
    # if not current_user.has_permission('system_management', 'delete'):  # 임시로 주석 처리
    #     return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import User, db
        
        employee = User.query.get_or_404(employee_id)
        
        # 직원 삭제 (실제 삭제 대신 비활성화)
        employee.status = 'inactive'
        db.session.commit()
        
        # 관련 캐시 무효화
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.clear_pattern('employees_list')
            cache_manager.clear_pattern('hierarchy_*')
        
        return jsonify({
            'success': True,
            'message': '직원이 성공적으로 비활성화되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"직원 삭제 오류: {e}")
        return jsonify({'error': '직원 삭제에 실패했습니다.'}), 500

# 계층별 관리 시스템 라우트 추가

@backend_admin_bp.route('/admin/backend/hierarchy-management')
def hierarchy_management():
    """계층별 관리 메인 페이지"""
    return render_template('admin/cyberpunk_hierarchy_management.html')

@backend_admin_bp.route('/admin/backend/industry-management')
def industry_management():
    """업종 관리 페이지"""
    return render_template('admin/cyberpunk_industry_management.html')

@backend_admin_bp.route('/admin/backend/brand-management')
def brand_management():
    """브랜드 관리 페이지"""
    return render_template('admin/cyberpunk_brand_management.html')

@backend_admin_bp.route('/admin/backend/branch-management')
def branch_management():
    """매장 관리 페이지"""
    return render_template('admin/cyberpunk_branch_management.html')

@backend_admin_bp.route('/admin/backend/employee-management')
def employee_management():
    """직원 관리 페이지"""
    return render_template('admin/cyberpunk_employee_management.html')

# 계층별 트리 API
@backend_admin_bp.route('/api/admin/hierarchy/tree')
@cached(expire=1800, key_prefix="hierarchy_tree")  # 30분 캐시
def get_hierarchy_tree():
    """전체 계층 트리 조회"""
    
    try:
        from models_main import Industry, Brand, Branch, User
        
        # DB에서 조회 (모든 업종 조회)
        industries = Industry.query.order_by(Industry.name).all()
        
        tree_data = {
            'industries': []
        }
        
        total_brands = 0
        total_branches = 0
        total_users = 0
        
        for industry in industries:
            brands = Brand.query.filter_by(industry_id=industry.id).order_by(Brand.name).all()
            brand_data = []
            
            for brand in brands:
                branches = Branch.query.filter_by(brand_id=brand.id).order_by(Branch.name).all()
                branch_data = []
                
                for branch in branches:
                    users = User.query.filter_by(branch_id=branch.id).all()
                    user_data = []
                    
                    for user in users:
                        user_data.append({
                            'id': user.id,
                            'name': user.name,
                            'role': user.role,
                            'status': user.status
                        })
                        total_users += 1
                    
                    branch_data.append({
                        'id': branch.id,
                        'name': branch.name,
                        'store_code': branch.store_code,
                        'address': branch.address,
                        'users': user_data
                    })
                    total_branches += 1
                
                brand_data.append({
                    'id': brand.id,
                    'name': brand.name,
                    'code': brand.code,
                    'branches': branch_data
                })
                total_brands += 1
            
            tree_data['industries'].append({
                'id': industry.id,
                'name': industry.name,
                'code': industry.code,
                'brands': brand_data
            })
        
        # 전체 통계 추가
        tree_data['stats'] = {
            'total_industries': len(tree_data['industries']),
            'total_brands': total_brands,
            'total_branches': total_branches,
            'total_users': total_users
        }
        
        return jsonify(tree_data)
        
    except Exception as e:
        print(f"계층 트리 조회 오류: {e}")
        return jsonify({'error': '계층 트리 조회에 실패했습니다.'}), 500

# 업종별 트리 API
@backend_admin_bp.route('/api/admin/hierarchy/industry/<int:industry_id>/tree')
@login_required
@cached(expire=1800, key_prefix="industry_tree")
def get_industry_tree(industry_id):
    """특정 업종 트리 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Industry, Brand, Branch, User
        
        industry = Industry.query.get_or_404(industry_id)
        
        # 캐시된 데이터 사용
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            tree_data = cache_manager.get_industry_tree(industry_id)
            if tree_data:
                return jsonify({
                    'success': True,
                    'data': tree_data
                })
        
        brands = Brand.query.filter_by(industry_id=industry.id, is_active=True).order_by(Brand.name).all()
        brand_data = []
        
        for brand in brands:
            branches = Branch.query.filter_by(brand_id=brand.id, is_active=True).order_by(Branch.name).all()
            branch_data = []
            
            for branch in branches:
                users = User.query.filter_by(branch_id=branch.id, status='approved').order_by(User.username).all()
                user_data = [{
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'status': user.status
                } for user in users]
                
                branch_data.append({
                    'id': branch.id,
                    'name': branch.name,
                    'store_code': branch.store_code,
                    'status': branch.status,
                    'users': user_data
                })
            
            brand_data.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'status': brand.status,
                'branches': branch_data
            })
        
        tree_data = {
            'id': industry.id,
            'name': industry.name,
            'code': industry.code,
            'color': industry.color,
            'icon': industry.icon,
            'brands': brand_data
        }
        
        # 캐시에 저장
        if cache_manager:
            cache_manager.set(f'industry_tree:{industry_id}', tree_data, 1800)
        
        return jsonify({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        print(f"업종 트리 조회 오류: {e}")
        return jsonify({'error': '업종 트리 조회에 실패했습니다.'}), 500

# 브랜드별 트리 API
@backend_admin_bp.route('/api/admin/hierarchy/brand/<int:brand_id>/tree')
@login_required
@cached(expire=1800, key_prefix="brand_tree")
def get_brand_tree(brand_id):
    """특정 브랜드 트리 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import Brand, Branch, User
        
        brand = Brand.query.get_or_404(brand_id)
        
        branches = Branch.query.filter_by(brand_id=brand.id, is_active=True).order_by(Branch.name).all()
        branch_data = []
        
        for branch in branches:
            users = User.query.filter_by(branch_id=branch.id, status='approved').order_by(User.username).all()
            user_data = [{
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'status': user.status
            } for user in users]
            
            branch_data.append({
                'id': branch.id,
                'name': branch.name,
                'store_code': branch.store_code,
                'status': branch.status,
                'users': user_data
            })
        
        tree_data = {
            'id': brand.id,
            'name': brand.name,
            'code': brand.code,
            'status': brand.status,
            'branches': branch_data
        }
        
        return jsonify({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        print(f"브랜드 트리 조회 오류: {e}")
        return jsonify({'error': '브랜드 트리 조회에 실패했습니다.'}), 500

# 계층별 통계 API
@backend_admin_bp.route('/api/admin/hierarchy/stats')
@cached(expire=300, key_prefix="hierarchy_stats")  # 5분 캐시
def get_hierarchy_stats():
    """계층별 통계 조회"""
    
    try:
        from models_main import Industry, Brand, Branch, User
        from sqlalchemy import func
        
        # 업종별 통계
        industry_stats = db.session.query(
            Industry.name,
            func.count(Brand.id).label('brand_count'),
            func.count(Branch.id).label('branch_count'),
            func.count(User.id).label('user_count')
        ).outerjoin(Brand).outerjoin(Branch).outerjoin(User).group_by(Industry.id, Industry.name).all()
        
        # 전체 통계
        total_stats = {
            'total_industries': Industry.query.count(),
            'total_brands': Brand.query.count(),
            'total_branches': Branch.query.count(),
            'total_users': User.query.count()
        }
        
        # 역할별 사용자 통계
        role_stats = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        role_data = {}
        for role, count in role_stats:
            role_data[role] = count
        
        return jsonify({
            'success': True,
            'data': {
                'industry_stats': [
                    {
                        'name': name,
                        'brand_count': brand_count,
                        'branch_count': branch_count,
                        'user_count': user_count
                    }
                    for name, brand_count, branch_count, user_count in industry_stats
                ],
                'total_stats': total_stats,
                'role_stats': role_data
            }
        })
        
    except Exception as e:
        print(f"계층 통계 조회 오류: {e}")
        return jsonify({'error': '계층 통계 조회에 실패했습니다.'}), 500

# 변경 이력 API
@backend_admin_bp.route('/api/admin/hierarchy/changelog')
@login_required
def get_hierarchy_changelog():
    """계층별 변경 이력 조회"""
    if not current_user.has_permission('system_management', 'view'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        from models_main import ActionLog
        
        # 최근 100개 변경 이력
        changelog = ActionLog.query.filter(
            ActionLog.action_type.in_(['create', 'update', 'delete']),
            ActionLog.table_name.in_(['industry', 'brand', 'branch', 'user'])
        ).order_by(ActionLog.created_at.desc()).limit(100).all()
        
        changelog_data = [{
            'id': log.id,
            'action_type': log.action_type,
            'table_name': log.table_name,
            'record_id': log.record_id,
            'old_values': log.old_values,
            'new_values': log.new_values,
            'user_id': log.user_id,
            'created_at': log.created_at.isoformat() if log.created_at else None
        } for log in changelog]
        
        return jsonify({
            'success': True,
            'data': changelog_data
        })
        
    except Exception as e:
        print(f"변경 이력 조회 오류: {e}")
        return jsonify({'error': '변경 이력 조회에 실패했습니다.'}), 500

# 캐시 무효화 API
@backend_admin_bp.route('/api/admin/hierarchy/cache/clear', methods=['POST'])
@login_required
def clear_hierarchy_cache():
    """계층별 캐시 무효화"""
    if not current_user.has_permission('system_management', 'admin'):
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    try:
        cache_manager = getattr(g, 'cache_manager', None)
        if cache_manager:
            cache_manager.invalidate_industry_cache()
            cache_manager.clear_pattern('hierarchy_*')
            cache_manager.clear_pattern('industry_tree*')
            cache_manager.clear_pattern('brand_tree*')
        
        return jsonify({
            'success': True,
            'message': '계층별 캐시가 성공적으로 무효화되었습니다.'
        })
        
    except Exception as e:
        print(f"캐시 무효화 오류: {e}")
        return jsonify({'error': '캐시 무효화에 실패했습니다.'}), 500 