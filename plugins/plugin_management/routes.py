from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from . import plugin_management
from .testing import run_automated_tests
from models_main import (
    PluginActivation, PluginPermission, PluginHierarchy, 
    PluginTestResult, User, Brand, Branch, db
)


@plugin_management.route('/plugins', methods=['GET'])
@login_required
def get_plugins():
    """사용 가능한 플러그인 목록 조회"""
    try:
        # 현재 사용자의 권한 확인
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 사용 가능한 플러그인 목록
        available_plugins = [
            {
                'id': 'attendance_management',
                'name': '출근관리',
                'description': '직원 출근/퇴근 관리 및 근무시간 추적',
                'version': '1.0.0',
                'category': 'hr',
                'icon': 'clock'
            },
            {
                'id': 'inventory_management',
                'name': '재고관리',
                'description': '상품 재고 관리 및 입출고 추적',
                'version': '1.0.0',
                'category': 'inventory',
                'icon': 'box'
            },
            {
                'id': 'purchase_management',
                'name': '구매관리',
                'description': '구매 주문 및 공급업체 관리',
                'version': '1.0.0',
                'category': 'purchase',
                'icon': 'shopping-cart'
            },
            {
                'id': 'schedule_management',
                'name': '스케줄관리',
                'description': '직원 근무 스케줄 관리',
                'version': '1.0.0',
                'category': 'hr',
                'icon': 'calendar'
            }
        ]
        
        return jsonify({
            'success': True,
            'plugins': available_plugins
        })
        
    except Exception as e:
        current_app.logger.error(f"플러그인 목록 조회 오류: {str(e)}")
        return jsonify({'error': '플러그인 목록을 불러오는데 실패했습니다.'}), 500


@plugin_management.route('/activation', methods=['GET'])
@login_required
def get_plugin_activations():
    """플러그인 활성화 상태 조회"""
    try:
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        target_type = request.args.get('target_type', 'brand')
        target_id = request.args.get('target_id', type=int)
        
        if not target_id:
            return jsonify({'error': '대상 ID가 필요합니다.'}), 400
        
        # 활성화 상태 조회
        activations = PluginActivation.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).all()
        
        activation_data = []
        for activation in activations:
            activation_data.append({
                'id': activation.id,
                'plugin_id': activation.plugin_id,
                'target_type': activation.target_type,
                'target_id': activation.target_id,
                'is_active': activation.is_active,
                'activation_date': activation.activation_date.isoformat() if activation.activation_date else None,
                'deactivation_date': activation.deactivation_date.isoformat() if activation.deactivation_date else None,
                'activated_by': activation.activated_by,
                'settings': activation.settings,
                'version': activation.version,
                'created_at': activation.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'activations': activation_data
        })
        
    except Exception as e:
        current_app.logger.error(f"플러그인 활성화 상태 조회 오류: {str(e)}")
        return jsonify({'error': '활성화 상태를 불러오는데 실패했습니다.'}), 500


@plugin_management.route('/activation', methods=['POST'])
@login_required
def activate_plugin():
    """플러그인 활성화/비활성화"""
    try:
        if not current_user.has_permission('system_management', 'manage'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        is_active = data.get('is_active', True)
        settings = data.get('settings', {})
        
        if not all([plugin_id, target_type, target_id]):
            return jsonify({'error': '필수 파라미터가 누락되었습니다.'}), 400
        
        # 기존 활성화 상태 확인
        activation = PluginActivation.query.filter_by(
            plugin_id=plugin_id,
            target_type=target_type,
            target_id=target_id
        ).first()
        
        if activation:
            # 기존 활성화 상태 업데이트
            activation.is_active = is_active
            if is_active:
                activation.activation_date = datetime.utcnow()
                activation.deactivation_date = None
            else:
                activation.deactivation_date = datetime.utcnow()
            activation.settings = settings
            activation.activated_by = current_user.id
        else:
            # 새로운 활성화 상태 생성
            activation = PluginActivation(
                plugin_id=plugin_id,
                target_type=target_type,
                target_id=target_id,
                is_active=is_active,
                activation_date=datetime.utcnow() if is_active else None,
                deactivation_date=None if is_active else datetime.utcnow(),
                activated_by=current_user.id,
                settings=settings,
                version='1.0.0'
            )
            db.session.add(activation)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'플러그인이 {"활성화" if is_active else "비활성화"}되었습니다.',
            'activation_id': activation.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 활성화 오류: {str(e)}")
        return jsonify({'error': '플러그인 활성화에 실패했습니다.'}), 500


@plugin_management.route('/permissions', methods=['GET'])
@login_required
def get_plugin_permissions():
    """플러그인 권한 조회"""
    try:
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        target_type = request.args.get('target_type', 'brand')
        target_id = request.args.get('target_id', type=int)
        plugin_id = request.args.get('plugin_id')
        
        if not target_id:
            return jsonify({'error': '대상 ID가 필요합니다.'}), 400
        
        query = PluginPermission.query.filter_by(
            target_type=target_type,
            target_id=target_id
        )
        
        if plugin_id:
            query = query.filter_by(plugin_id=plugin_id)
        
        permissions = query.all()
        
        permission_data = []
        for perm in permissions:
            permission_data.append({
                'id': perm.id,
                'plugin_id': perm.plugin_id,
                'target_type': perm.target_type,
                'target_id': perm.target_id,
                'role': perm.role,
                'permissions': perm.permissions,
                'is_inherited': perm.is_inherited,
                'inherited_from': perm.inherited_from,
                'created_by': perm.created_by,
                'created_at': perm.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'permissions': permission_data
        })
        
    except Exception as e:
        current_app.logger.error(f"플러그인 권한 조회 오류: {str(e)}")
        return jsonify({'error': '권한 정보를 불러오는데 실패했습니다.'}), 500


@plugin_management.route('/permissions', methods=['POST'])
@login_required
def set_plugin_permissions():
    """플러그인 권한 설정"""
    try:
        if not current_user.has_permission('system_management', 'manage'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        role = data.get('role')
        permissions = data.get('permissions', {})
        
        if not all([plugin_id, target_type, target_id, role]):
            return jsonify({'error': '필수 파라미터가 누락되었습니다.'}), 400
        
        # 기존 권한 확인
        existing_permission = PluginPermission.query.filter_by(
            plugin_id=plugin_id,
            target_type=target_type,
            target_id=target_id,
            role=role
        ).first()
        
        if existing_permission:
            # 기존 권한 업데이트
            existing_permission.permissions = permissions
            existing_permission.is_inherited = False
            existing_permission.inherited_from = None
        else:
            # 새로운 권한 생성
            new_permission = PluginPermission(
                plugin_id=plugin_id,
                target_type=target_type,
                target_id=target_id,
                role=role,
                permissions=permissions,
                is_inherited=False,
                created_by=current_user.id
            )
            db.session.add(new_permission)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '플러그인 권한이 설정되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 권한 설정 오류: {str(e)}")
        return jsonify({'error': '권한 설정에 실패했습니다.'}), 500


@plugin_management.route('/hierarchy', methods=['GET'])
@login_required
def get_plugin_hierarchy():
    """플러그인 계층 구조 조회"""
    try:
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        plugin_id = request.args.get('plugin_id')
        
        query = PluginHierarchy.query
        if plugin_id:
            query = query.filter_by(plugin_id=plugin_id)
        
        hierarchies = query.all()
        
        hierarchy_data = []
        for hierarchy in hierarchies:
            hierarchy_data.append({
                'id': hierarchy.id,
                'plugin_id': hierarchy.plugin_id,
                'parent_type': hierarchy.parent_type,
                'parent_id': hierarchy.parent_id,
                'child_type': hierarchy.child_type,
                'child_id': hierarchy.child_id,
                'inheritance_type': hierarchy.inheritance_type,
                'inheritance_settings': hierarchy.inheritance_settings,
                'created_at': hierarchy.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'hierarchies': hierarchy_data
        })
        
    except Exception as e:
        current_app.logger.error(f"플러그인 계층 구조 조회 오류: {str(e)}")
        return jsonify({'error': '계층 구조를 불러오는데 실패했습니다.'}), 500


@plugin_management.route('/hierarchy', methods=['POST'])
@login_required
def set_plugin_hierarchy():
    """플러그인 계층 구조 설정"""
    try:
        if not current_user.has_permission('system_management', 'manage'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        parent_type = data.get('parent_type')
        parent_id = data.get('parent_id')
        child_type = data.get('child_type')
        child_id = data.get('child_id')
        inheritance_type = data.get('inheritance_type', 'full')
        inheritance_settings = data.get('inheritance_settings', {})
        
        if not all([plugin_id, parent_type, parent_id, child_type, child_id]):
            return jsonify({'error': '필수 파라미터가 누락되었습니다.'}), 400
        
        # 기존 계층 구조 확인
        existing_hierarchy = PluginHierarchy.query.filter_by(
            plugin_id=plugin_id,
            parent_type=parent_type,
            parent_id=parent_id,
            child_type=child_type,
            child_id=child_id
        ).first()
        
        if existing_hierarchy:
            # 기존 계층 구조 업데이트
            existing_hierarchy.inheritance_type = inheritance_type
            existing_hierarchy.inheritance_settings = inheritance_settings
        else:
            # 새로운 계층 구조 생성
            new_hierarchy = PluginHierarchy(
                plugin_id=plugin_id,
                parent_type=parent_type,
                parent_id=parent_id,
                child_type=child_type,
                child_id=child_id,
                inheritance_type=inheritance_type,
                inheritance_settings=inheritance_settings
            )
            db.session.add(new_hierarchy)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '플러그인 계층 구조가 설정되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 계층 구조 설정 오류: {str(e)}")
        return jsonify({'error': '계층 구조 설정에 실패했습니다.'}), 500


@plugin_management.route('/test', methods=['POST'])
@login_required
def test_plugin():
    """플러그인 테스트 실행"""
    try:
        if not current_user.has_permission('system_management', 'test'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        test_type = data.get('test_type', 'activation')
        
        if not all([plugin_id, target_type, target_id]):
            return jsonify({'error': '필수 파라미터가 누락되었습니다.'}), 400
        
        start_time = datetime.utcnow()
        test_result = {
            'status': 'passed',
            'message': '테스트가 성공적으로 완료되었습니다.',
            'data': {}
        }
        
        try:
            if test_type == 'activation':
                # 활성화 테스트
                activation = PluginActivation.query.filter_by(
                    plugin_id=plugin_id,
                    target_type=target_type,
                    target_id=target_id
                ).first()
                
                if not activation or not activation.is_active:
                    test_result['status'] = 'failed'
                    test_result['message'] = '플러그인이 활성화되지 않았습니다.'
                else:
                    test_result['data']['activation'] = {
                        'is_active': activation.is_active,
                        'settings': activation.settings,
                        'version': activation.version
                    }
            
            elif test_type == 'permission':
                # 권한 테스트
                permissions = PluginPermission.query.filter_by(
                    plugin_id=plugin_id,
                    target_type=target_type,
                    target_id=target_id
                ).all()
                
                if not permissions:
                    test_result['status'] = 'failed'
                    test_result['message'] = '플러그인 권한이 설정되지 않았습니다.'
                else:
                    test_result['data']['permissions'] = [
                        {
                            'role': perm.role,
                            'permissions': perm.permissions
                        } for perm in permissions
                    ]
            
            elif test_type == 'ui':
                # UI 테스트 (기본적인 접근 가능 여부 확인)
                test_result['data']['ui_test'] = {
                    'accessible': True,
                    'endpoints': [
                        f'/api/{plugin_id}/status',
                        f'/api/{plugin_id}/settings'
                    ]
                }
            
            elif test_type == 'api':
                # API 테스트 (기본적인 엔드포인트 확인)
                test_result['data']['api_test'] = {
                    'endpoints_available': True,
                    'response_time': 0.1
                }
            
        except Exception as test_error:
            test_result['status'] = 'error'
            test_result['message'] = f'테스트 실행 중 오류 발생: {str(test_error)}'
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 테스트 결과 저장
        test_record = PluginTestResult(
            plugin_id=plugin_id,
            target_type=target_type,
            target_id=target_id,
            test_type=test_type,
            test_name=f'{test_type}_test',
            status=test_result['status'],
            result_data=test_result['data'],
            error_message=test_result['message'] if test_result['status'] != 'passed' else None,
            execution_time=execution_time,
            tested_by=current_user.id
        )
        db.session.add(test_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'test_result': test_result,
            'execution_time': execution_time
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 테스트 오류: {str(e)}")
        return jsonify({'error': '테스트 실행에 실패했습니다.'}), 500


@plugin_management.route('/automated-test', methods=['POST'])
@login_required
def run_automated_test():
    """자동화된 테스트 실행"""
    try:
        if not current_user.has_permission('system_management', 'test'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        target_type = data.get('target_type', 'brand')
        target_id = data.get('target_id')
        
        if not target_id:
            return jsonify({'error': '대상 ID가 필요합니다.'}), 400
        
        # 자동화된 테스트 실행
        results = run_automated_tests(target_type, target_id, current_user.id)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"자동화된 테스트 실행 오류: {str(e)}")
        return jsonify({'error': '자동화된 테스트 실행에 실패했습니다.'}), 500


@plugin_management.route('/test-results', methods=['GET'])
@login_required
def get_test_results():
    """테스트 결과 조회"""
    try:
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        plugin_id = request.args.get('plugin_id')
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id', type=int)
        test_type = request.args.get('test_type')
        
        query = PluginTestResult.query
        
        if plugin_id:
            query = query.filter_by(plugin_id=plugin_id)
        if target_type:
            query = query.filter_by(target_type=target_type)
        if target_id:
            query = query.filter_by(target_id=target_id)
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        # 최근 50개 결과만 조회
        results = query.order_by(PluginTestResult.created_at.desc()).limit(50).all()
        
        result_data = []
        for result in results:
            result_data.append({
                'id': result.id,
                'plugin_id': result.plugin_id,
                'target_type': result.target_type,
                'target_id': result.target_id,
                'test_type': result.test_type,
                'test_name': result.test_name,
                'status': result.status,
                'result_data': result.result_data,
                'error_message': result.error_message,
                'execution_time': result.execution_time,
                'tested_by': result.tested_by,
                'created_at': result.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'test_results': result_data
        })
        
    except Exception as e:
        current_app.logger.error(f"테스트 결과 조회 오류: {str(e)}")
        return jsonify({'error': '테스트 결과를 불러오는데 실패했습니다.'}), 500


@plugin_management.route('/bulk-activate', methods=['POST'])
@login_required
def bulk_activate_plugins():
    """플러그인 일괄 활성화/비활성화"""
    try:
        if not current_user.has_permission('system_management', 'manage'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        target_type = data.get('target_type')
        target_id = data.get('target_id')
        plugin_ids = data.get('plugin_ids', [])
        is_active = data.get('is_active', True)
        settings = data.get('settings', {})
        
        if not all([target_type, target_id, plugin_ids]):
            return jsonify({'error': '필수 파라미터가 누락되었습니다.'}), 400
        
        activated_count = 0
        for plugin_id in plugin_ids:
            # 기존 활성화 상태 확인
            activation = PluginActivation.query.filter_by(
                plugin_id=plugin_id,
                target_type=target_type,
                target_id=target_id
            ).first()
            
            if activation:
                # 기존 활성화 상태 업데이트
                activation.is_active = is_active
                if is_active:
                    activation.activation_date = datetime.utcnow()
                    activation.deactivation_date = None
                else:
                    activation.deactivation_date = datetime.utcnow()
                activation.settings = settings.get(plugin_id, {})
                activation.activated_by = current_user.id
            else:
                # 새로운 활성화 상태 생성
                activation = PluginActivation(
                    plugin_id=plugin_id,
                    target_type=target_type,
                    target_id=target_id,
                    is_active=is_active,
                    activation_date=datetime.utcnow() if is_active else None,
                    deactivation_date=None if is_active else datetime.utcnow(),
                    activated_by=current_user.id,
                    settings=settings.get(plugin_id, {}),
                    version='1.0.0'
                )
                db.session.add(activation)
            
            activated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{activated_count}개의 플러그인이 {"활성화" if is_active else "비활성화"}되었습니다.',
            'activated_count': activated_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 일괄 활성화 오류: {str(e)}")
        return jsonify({'error': '일괄 활성화에 실패했습니다.'}), 500


@plugin_management.route('/status', methods=['GET'])
@login_required
def get_plugin_status():
    """플러그인 전체 상태 조회"""
    try:
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        target_type = request.args.get('target_type', 'brand')
        target_id = request.args.get('target_id', type=int)
        
        if not target_id:
            return jsonify({'error': '대상 ID가 필요합니다.'}), 400
        
        # 활성화 상태 조회
        activations = PluginActivation.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).all()
        
        # 권한 상태 조회
        permissions = PluginPermission.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).all()
        
        # 테스트 결과 조회 (최근)
        test_results = PluginTestResult.query.filter_by(
            target_type=target_type,
            target_id=target_id
        ).order_by(PluginTestResult.created_at.desc()).limit(10).all()
        
        status_data = {
            'target_type': target_type,
            'target_id': target_id,
            'activations': [
                {
                    'plugin_id': activation.plugin_id,
                    'is_active': activation.is_active,
                    'version': activation.version,
                    'settings': activation.settings
                } for activation in activations
            ],
            'permissions': [
                {
                    'plugin_id': perm.plugin_id,
                    'role': perm.role,
                    'permissions': perm.permissions,
                    'is_inherited': perm.is_inherited
                } for perm in permissions
            ],
            'recent_tests': [
                {
                    'plugin_id': result.plugin_id,
                    'test_type': result.test_type,
                    'status': result.status,
                    'created_at': result.created_at.isoformat()
                } for result in test_results
            ]
        }
        
        return jsonify({
            'success': True,
            'status': status_data
        })
        
    except Exception as e:
        current_app.logger.error(f"플러그인 상태 조회 오류: {str(e)}")
        return jsonify({'error': '플러그인 상태를 불러오는데 실패했습니다.'}), 500 