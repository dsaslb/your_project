import json
from sqlalchemy import desc
from models_main import db, PluginCustomization, PluginDeployment, PluginAccessControl, Module, Brand, Branch, Industry
from datetime import datetime
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
#!/usr/bin/env python3
"""
플러그인 커스터마이징 및 배포 관리 API
업종/브랜드/매장별 플러그인 커스터마이징, 배포, 접근 제어 관리
"""


plugin_customization_bp = Blueprint('plugin_customization', __name__)

# ==================== 플러그인 커스터마이징 API ====================


@plugin_customization_bp.route('/plugins/<plugin_id>/customizations', methods=['GET'])
@login_required
def get_plugin_customizations(plugin_id):
    """
    플러그인 커스터마이징 목록 조회
    """
    try:
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id')

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 쿼리 구성
        query = PluginCustomization.query.filter_by(plugin_id=plugin_id)

        # 필터 적용
        if target_type:
            query = query.filter_by(target_type=target_type)
        if target_id:
            query = query.filter_by(target_id=target_id)

        # 권한 확인 (관리자이거나 해당 대상의 관리자만)
        if not current_user.is_admin():
            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403

        customizations = query.all()

        return jsonify({
            'success': True,
            'data': {
                'customizations': [{
                    'id': custom.id,
                    'target_type': custom.target_type,
                    'target_id': custom.target_id,
                    'is_active': custom.is_active,
                    'settings': custom.settings,
                    'permissions': custom.permissions,
                    'menu_visibility': custom.menu_visibility,
                    'created_at': custom.created_at.isoformat(),
                    'updated_at': custom.updated_at.isoformat()
                } for custom in customizations]
            }
        })

    except Exception as e:
        current_app.logger.error(f"커스터마이징 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/plugins/<plugin_id>/customizations', methods=['POST'])
@login_required
def create_plugin_customization(plugin_id):
    """
    플러그인 커스터마이징 생성
    """
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['target_type', 'target_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            target_type = data['target_type']
            target_id = data['target_id']

            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '브랜드 커스터마이징 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '매장 커스터마이징 권한이 없습니다'}), 403

        # 기존 커스터마이징 확인
        existing = PluginCustomization.query.filter_by(
            plugin_id=plugin_id,
            target_type=data['target_type'],
            target_id=data['target_id']
        ).first()

        if existing:
            return jsonify({'success': False, 'error': '이미 커스터마이징이 존재합니다'}), 400

        # 커스터마이징 생성
        customization = PluginCustomization(
            plugin_id=plugin_id,
            target_type=data['target_type'],
            target_id=data['target_id'],
            settings=data.get('settings', {}),
            permissions=data.get('permissions', {}),
            menu_visibility=data.get('menu_visibility', {})
        )

        db.session.add(customization)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '커스터마이징이 생성되었습니다',
            'data': {
                'id': customization.id,
                'target_type': customization.target_type,
                'target_id': customization.target_id,
                'is_active': customization.is_active
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"커스터마이징 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/customizations/<int:customization_id>', methods=['PUT'])
@login_required
def update_plugin_customization(customization_id):
    """플러그인 커스터마이징 업데이트"""
    try:
        data = request.get_json()

        customization = PluginCustomization.query.get(customization_id)
        if not customization:
            return jsonify({'success': False, 'error': '커스터마이징을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            if customization.target_type == 'brand':
                brand = Brand.query.get(customization.target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '수정 권한이 없습니다'}), 403
            elif customization.target_type == 'store':
                store = Branch.query.get(customization.target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '수정 권한이 없습니다'}), 403

        # 업데이트
        if 'settings' in data:
            customization.settings = data['settings']
        if 'permissions' in data:
            customization.permissions = data['permissions']
        if 'menu_visibility' in data:
            customization.menu_visibility = data['menu_visibility']
        if 'is_active' in data:
            customization.is_active = data['is_active']

        customization.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '커스터마이징이 업데이트되었습니다',
            'data': {
                'id': customization.id,
                'target_type': customization.target_type,
                'target_id': customization.target_id,
                'is_active': customization.is_active,
                'updated_at': customization.updated_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"커스터마이징 업데이트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/customizations/<int:customization_id>', methods=['DELETE'])
@login_required
def delete_plugin_customization(customization_id):
    """플러그인 커스터마이징 삭제"""
    try:
        customization = PluginCustomization.query.get(customization_id)
        if not customization:
            return jsonify({'success': False, 'error': '커스터마이징을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            if customization.target_type == 'brand':
                brand = Brand.query.get(customization.target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '삭제 권한이 없습니다'}), 403
            elif customization.target_type == 'store':
                store = Branch.query.get(customization.target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '삭제 권한이 없습니다'}), 403

        db.session.delete(customization)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '커스터마이징이 삭제되었습니다'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"커스터마이징 삭제 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 플러그인 배포 관리 API ====================


@plugin_customization_bp.route('/plugins/<plugin_id>/deployments', methods=['GET'])
@login_required
def get_plugin_deployments(plugin_id):
    """플러그인 배포 목록 조회"""
    try:
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id')
        status = request.args.get('status')

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 쿼리 구성
        query = PluginDeployment.query.filter_by(plugin_id=plugin_id)

        # 필터 적용
        if target_type:
            query = query.filter_by(target_type=target_type)
        if target_id:
            query = query.filter_by(target_id=target_id)
        if status:
            query = query.filter_by(status=status)

        # 권한 확인
        if not current_user.is_admin():
            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403

        # 정렬 (최신순)
        query = query.order_by(desc(PluginDeployment.created_at))

        deployments = query.all()

        return jsonify({
            'success': True,
            'data': {
                'deployments': [{
                    'id': deployment.id,
                    'version': deployment.version,
                    'target_type': deployment.target_type,
                    'target_id': deployment.target_id,
                    'deployment_type': deployment.deployment_type,
                    'status': deployment.status,
                    'scheduled_at': deployment.scheduled_at.isoformat() if deployment.scheduled_at else None,
                    'started_at': deployment.started_at.isoformat() if deployment.started_at else None,
                    'completed_at': deployment.completed_at.isoformat() if deployment.completed_at else None,
                    'error_message': deployment.error_message,
                    'created_at': deployment.created_at.isoformat()
                } for deployment in deployments]
            }
        })

    except Exception as e:
        current_app.logger.error(f"배포 목록 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/plugins/<plugin_id>/deploy', methods=['POST'])
@login_required
def deploy_plugin(plugin_id):
    """플러그인 배포"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['target_type', 'target_id', 'deployment_type']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400

        # 플러그인 존재 확인 (deploy_plugin 등에서도 동일하게)
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            target_type = data['target_type']
            target_id = data['target_id']

            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '브랜드 배포 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '매장 배포 권한이 없습니다'}), 403

        # 배포 생성
        deployment = PluginDeployment(
            plugin_id=plugin_id,
            version=data.get('version', plugin.version),
            target_type=data['target_type'],
            target_id=data['target_id'],
            deployment_type=data['deployment_type'],
            status='pending',
            scheduled_at=datetime.utcnow() if data.get('deploy_now', True) else None,
            created_by=current_user.id
        )

        db.session.add(deployment)
        db.session.commit()

        # 즉시 배포인 경우 배포 실행
        if data.get('deploy_now', True):
            # 실제 배포 로직은 별도 서비스에서 처리
            deployment.status = 'in_progress'
            deployment.started_at = datetime.utcnow()
            db.session.commit()

        return jsonify({
            'success': True,
            'message': '배포가 요청되었습니다',
            'data': {
                'id': deployment.id,
                'status': deployment.status,
                'scheduled_at': deployment.scheduled_at.isoformat() if deployment.scheduled_at else None
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"플러그인 배포 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/deployments/<int:deployment_id>/status', methods=['PUT'])
@login_required
def update_deployment_status(deployment_id):
    """배포 상태 업데이트"""
    try:
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': '관리자 권한이 필요합니다'}), 403

        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'success': False, 'error': '상태는 필수입니다'}), 400

        if new_status not in ['pending', 'in_progress', 'completed', 'failed']:
            return jsonify({'success': False, 'error': '유효하지 않은 상태입니다'}), 400

        deployment = PluginDeployment.query.get(deployment_id)
        if not deployment:
            return jsonify({'success': False, 'error': '배포를 찾을 수 없습니다'}), 404

        # 상태 업데이트
        deployment.status = new_status

        if new_status == 'in_progress' and not deployment.started_at:
            deployment.started_at = datetime.utcnow()
        elif new_status in ['completed', 'failed']:
            deployment.completed_at = datetime.utcnow()
            if new_status == 'failed':
                deployment.error_message = data.get('error_message')

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '배포 상태가 업데이트되었습니다',
            'status': deployment.status
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"배포 상태 업데이트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 플러그인 접근 제어 API ====================


@plugin_customization_bp.route('/plugins/<plugin_id>/access-controls', methods=['GET'])
@login_required
def get_plugin_access_controls(plugin_id):
    """플러그인 접근 제어 목록 조회"""
    try:
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id')

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 쿼리 구성
        query = PluginAccessControl.query.filter_by(plugin_id=plugin_id)

        # 필터 적용
        if target_type:
            query = query.filter_by(target_type=target_type)
        if target_id:
            query = query.filter_by(target_id=target_id)

        # 권한 확인
        if not current_user.is_admin():
            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403

        access_controls = query.all()

        return jsonify({
            'success': True,
            'data': {
                'access_controls': [{
                    'id': control.id,
                    'target_type': control.target_type,
                    'target_id': control.target_id,
                    'access_type': control.access_type,
                    'is_allowed': control.is_allowed,
                    'conditions': control.conditions,
                    'created_at': control.created_at.isoformat(),
                    'updated_at': control.updated_at.isoformat()
                } for control in access_controls]
            }
        })

    except Exception as e:
        current_app.logger.error(f"접근 제어 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/plugins/<plugin_id>/access-controls', methods=['POST'])
@login_required
def create_plugin_access_control(plugin_id):
    """플러그인 접근 제어 생성"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['target_type', 'target_id', 'access_type']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            target_type = data['target_type']
            target_id = data['target_id']

            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '브랜드 접근 제어 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '매장 접근 제어 권한이 없습니다'}), 403

        # 기존 접근 제어 확인
        existing = PluginAccessControl.query.filter_by(
            plugin_id=plugin_id,
            target_type=data['target_type'],
            target_id=data['target_id'],
            access_type=data['access_type']
        ).first()

        if existing:
            return jsonify({'success': False, 'error': '이미 접근 제어가 존재합니다'}), 400

        # 접근 제어 생성
        access_control = PluginAccessControl(
            plugin_id=plugin_id,
            target_type=data['target_type'],
            target_id=data['target_id'],
            access_type=data['access_type'],
            is_allowed=data.get('is_allowed', True),
            conditions=data.get('conditions', {})
        )

        db.session.add(access_control)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '접근 제어가 생성되었습니다',
            'data': {
                'id': access_control.id,
                'target_type': access_control.target_type,
                'target_id': access_control.target_id,
                'access_type': access_control.access_type,
                'is_allowed': access_control.is_allowed
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"접근 제어 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/access-controls/<int:control_id>', methods=['PUT'])
@login_required
def update_plugin_access_control(control_id):
    """플러그인 접근 제어 업데이트"""
    try:
        data = request.get_json()

        access_control = PluginAccessControl.query.get(control_id)
        if not access_control:
            return jsonify({'success': False, 'error': '접근 제어를 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            if access_control.target_type == 'brand':
                brand = Brand.query.get(access_control.target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '수정 권한이 없습니다'}), 403
            elif access_control.target_type == 'store':
                store = Branch.query.get(access_control.target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '수정 권한이 없습니다'}), 403

        # 업데이트
        if 'is_allowed' in data:
            access_control.is_allowed = data['is_allowed']
        if 'conditions' in data:
            access_control.conditions = data['conditions']

        access_control.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '접근 제어가 업데이트되었습니다',
            'data': {
                'id': access_control.id,
                'is_allowed': access_control.is_allowed,
                'updated_at': access_control.updated_at.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"접근 제어 업데이트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 유틸리티 API ====================


@plugin_customization_bp.route('/targets', methods=['GET'])
@login_required
def get_available_targets():
    """사용 가능한 대상 목록 조회"""
    try:
        target_type = request.args.get('target_type')

        targets = []

        if target_type == 'industry' or not target_type:
            industries = Industry.query.filter_by(is_active=True).all()
            targets.extend([{
                'id': str(industry.id),
                'name': industry.name,
                'type': 'industry'
            } for industry in industries])

        if target_type == 'brand' or not target_type:
            if current_user.is_admin():
                brands = Brand.query.filter_by(status='active').all()
            else:
                brands = [current_user.brand] if current_user.brand else []

            targets.extend([{
                'id': str(brand.id),
                'name': brand.name,
                'type': 'brand'
            } for brand in brands])

        if target_type == 'store' or not target_type:
            if current_user.is_admin():
                stores = Branch.query.filter_by(status='active').all()
            else:
                stores = Branch.query.filter_by(
                    brand_id=current_user.brand_id,
                    status='active'
                ).all() if current_user.brand_id else []

            targets.extend([{
                'id': str(store.id),
                'name': store.name,
                'type': 'store'
            } for store in stores])

        return jsonify({
            'success': True,
            'data': {
                'targets': targets
            }
        })

    except Exception as e:
        current_app.logger.error(f"대상 목록 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@plugin_customization_bp.route('/plugins/<plugin_id>/effective-settings', methods=['GET'])
@login_required
def get_effective_plugin_settings(plugin_id):
    """플러그인의 실제 적용되는 설정 조회"""
    try:
        target_type = request.args.get('target_type')
        target_id = request.args.get('target_id')

        if not target_type or not target_id:
            return jsonify({'success': False, 'error': 'target_type과 target_id는 필수입니다'}), 400

        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404

        # 권한 확인
        if not current_user.is_admin():
            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if not brand or brand.id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if not store or store.brand_id != current_user.brand_id:
                    return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403

        # 계층적 설정 조회 (업종 > 브랜드 > 매장 > 사용자 순)
        effective_settings = {}
        effective_permissions = {}
        effective_menu_visibility = {}

        # 업종 설정 (업종이 있는 경우)
        if target_type in ['brand', 'store']:
            if target_type == 'brand':
                brand = Brand.query.get(target_id)
                if brand and brand.industry_id:
                    industry_customization = PluginCustomization.query.filter_by(
                        plugin_id=plugin_id,
                        target_type='industry',
                        target_id=str(brand.industry_id),
                        is_active=True
                    ).first()

                    if industry_customization:
                        effective_settings.update(industry_customization.settings or {})
                        effective_permissions.update(industry_customization.permissions or {})
                        effective_menu_visibility.update(industry_customization.menu_visibility or {})

            elif target_type == 'store':
                store = Branch.query.get(target_id)
                if store:
                    # 브랜드 설정
                    if store.brand_id:
                        brand_customization = PluginCustomization.query.filter_by(
                            plugin_id=plugin_id,
                            target_type='brand',
                            target_id=str(store.brand_id),
                            is_active=True
                        ).first()

                        if brand_customization:
                            effective_settings.update(brand_customization.settings or {})
                            effective_permissions.update(brand_customization.permissions or {})
                            effective_menu_visibility.update(brand_customization.menu_visibility or {})

        # 대상별 설정
        target_customization = PluginCustomization.query.filter_by(
            plugin_id=plugin_id,
            target_type=target_type,
            target_id=target_id,
            is_active=True
        ).first()

        if target_customization:
            effective_settings.update(target_customization.settings or {})
            effective_permissions.update(target_customization.permissions or {})
            effective_menu_visibility.update(target_customization.menu_visibility or {})

        return jsonify({
            'success': True,
            'data': {
                'plugin_id': plugin_id,
                'target_type': target_type,
                'target_id': target_id,
                'settings': effective_settings,
                'permissions': effective_permissions,
                'menu_visibility': effective_menu_visibility
            }
        })

    except Exception as e:
        current_app.logger.error(f"실제 설정 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
