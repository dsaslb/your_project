from models.settings_models import BrandSettings, SystemSettings  # pyright: ignore
from models.report_models import Report, ReportTemplate  # pyright: ignore
from models.order_models import Order, OrderTemplate  # pyright: ignore
from models.inventory_models import Inventory, InventoryCategory  # pyright: ignore
from models.notification_models import Notification, NotificationTemplate  # pyright: ignore
from models.schedule_models import Schedule, WorkRule  # pyright: ignore
from models.menu_models import Menu, MenuCategory  # pyright: ignore
from models.employee_models import Employee, EmployeeRole  # pyright: ignore
from models.store_models import Store  # pyright: ignore
from models.brand_models import Brand  # pyright: ignore
from models.database import db  # pyright: ignore
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
브랜드 등록 시스템 - 연관 기능 동기화
신규 브랜드 등록 시 모든 연관 데이터를 자동으로 생성하고 동기화
"""


brand_registration_bp = Blueprint('brand_registration', __name__)
logger = logging.getLogger(__name__)


class BrandRegistrationSystem:
    """브랜드 등록 및 연관 데이터 동기화 시스템"""

    def __init__(self):
        self.default_templates = self._load_default_templates()

    def _load_default_templates(self):
        """기본 템플릿 데이터 로드"""
        return {
            'menu_categories': [
                {'name': '음료', 'description': '음료 메뉴', 'sort_order': 1},
                {'name': '음식', 'description': '음식 메뉴', 'sort_order': 2},
                {'name': '디저트', 'description': '디저트 메뉴', 'sort_order': 3},
                {'name': 'MD', 'description': '상품', 'sort_order': 4}
            ],
            'work_rules': [
                {
                    'name': '기본 근무 규칙',
                    'work_start_time': '09:00',
                    'work_end_time': '18:00',
                    'break_start_time': '12:00',
                    'break_end_time': '13:00',
                    'overtime_threshold': 8,
                    'weekly_work_hours': 40
                }
            ],
            'notification_templates': [
                {
                    'name': '출근 알림',
                    'type': 'attendance',
                    'title': '출근 확인',
                    'message': '{employee_name}님이 출근했습니다.',
                    'is_active': True
                },
                {
                    'name': '퇴근 알림',
                    'type': 'attendance',
                    'title': '퇴근 확인',
                    'message': '{employee_name}님이 퇴근했습니다.',
                    'is_active': True
                },
                {
                    'name': '재고 부족 알림',
                    'type': 'inventory',
                    'title': '재고 부족',
                    'message': '{item_name}의 재고가 부족합니다.',
                    'is_active': True
                }
            ],
            'inventory_categories': [
                {'name': '원재료', 'description': '음식 제조용 원재료'},
                {'name': '포장재', 'description': '포장용 재료'},
                {'name': '소모품', 'description': '일반 소모품'},
                {'name': '기타', 'description': '기타 재고'}
            ],
            'report_templates': [
                {
                    'name': '일일 매출 보고서',
                    'type': 'daily_sales',
                    'description': '일일 매출 현황',
                    'is_active': True
                },
                {
                    'name': '월간 매출 보고서',
                    'type': 'monthly_sales',
                    'description': '월간 매출 현황',
                    'is_active': True
                },
                {
                    'name': '직원 근무 보고서',
                    'type': 'employee_attendance',
                    'description': '직원 근무 현황',
                    'is_active': True
                }
            ]
        }

    def create_brand_with_related_data(self,  brand_data,  creator_user_id):
        """브랜드와 연관 데이터를 함께 생성"""
        try:
            # 트랜잭션 시작
            with db.session.begin():
                # 1. 브랜드 생성
                brand = self._create_brand(brand_data,  creator_user_id)

                # 2. 기본 매장 생성
                default_store = self._create_default_store(brand.id,  brand_data)

                # 3. 브랜드 관리자 생성
                brand_admin = self._create_brand_admin(brand.id,  creator_user_id)

                # 4. 기본 설정 생성
                brand_settings = self._create_brand_settings(brand.id)

                # 5. 메뉴 카테고리 생성
                menu_categories = self._create_menu_categories(brand.id)

                # 6. 근무 규칙 생성
                work_rules = self._create_work_rules(brand.id)

                # 7. 알림 템플릿 생성
                notification_templates = self._create_notification_templates(brand.id)

                # 8. 재고 카테고리 생성
                inventory_categories = self._create_inventory_categories(brand.id)

                # 9. 보고서 템플릿 생성
                report_templates = self._create_report_templates(brand.id)

                # 10. 기본 발주 템플릿 생성
                order_templates = self._create_order_templates(brand.id)

                # 11. 온보딩 상태 설정
                onboarding_status = self._create_onboarding_status(brand.id)

                logger.info(f"브랜드 '{brand.name}' 생성 완료 (ID: {brand.id})")

                return {
                    'success': True,
                    'brand': brand,
                    'related_data': {
                        'store': default_store,
                        'admin': brand_admin,
                        'settings': brand_settings,
                        'menu_categories': menu_categories,
                        'work_rules': work_rules,
                        'notification_templates': notification_templates,
                        'inventory_categories': inventory_categories,
                        'report_templates': report_templates,
                        'order_templates': order_templates,
                        'onboarding_status': onboarding_status
                    }
                }

        except Exception as e:
            logger.error(f"브랜드 생성 중 오류: {str(e)}")
            db.session.rollback()
            raise e

    def _create_brand(self,  brand_data,  creator_user_id):
        """브랜드 생성"""
        brand = Brand(
            name=brand_data['name'] if brand_data is not None else None,
            description=brand_data.get('description', ''),
            address=brand_data.get() if brand_data else None'address', '') if brand_data else None,
            zipcode=brand_data.get() if brand_data else None'zipcode', '') if brand_data else None,
            road_address=brand_data.get() if brand_data else None'road_address', '') if brand_data else None,
            jibun_address=brand_data.get() if brand_data else None'jibun_address', '') if brand_data else None,
            detail_address=brand_data.get() if brand_data else None'detail_address', '') if brand_data else None,
            latitude=brand_data.get() if brand_data else None'latitude') if brand_data else None,
            longitude=brand_data.get() if brand_data else None'longitude') if brand_data else None,
            phone=brand_data.get() if brand_data else None'phone', '') if brand_data else None,
            email=brand_data.get() if brand_data else None'email', '') if brand_data else None,
            website=brand_data.get() if brand_data else None'website', '') if brand_data else None,
            business_number=brand_data.get() if brand_data else None'business_number', '') if brand_data else None,
            representative_name=brand_data.get() if brand_data else None'representative_name', '') if brand_data else None,
            industry=brand_data.get() if brand_data else None'industry', '') if brand_data else None,
            created_by=creator_user_id,
            status='active',
            registration_date=datetime.now()
        )

        db.session.add(brand)
        db.session.flush()  # ID 생성
        return brand

    def _create_default_store(self,  brand_id,  brand_data):
        """기본 매장 생성"""
        store = Store(
            brand_id=brand_id,
            name=f"{brand_data['name'] if brand_data is not None else None} 본점",
            description="기본 매장",
            address=brand_data.get() if brand_data else None'address', '') if brand_data else None,
            zipcode=brand_data.get() if brand_data else None'zipcode', '') if brand_data else None,
            road_address=brand_data.get() if brand_data else None'road_address', '') if brand_data else None,
            jibun_address=brand_data.get() if brand_data else None'jibun_address', '') if brand_data else None,
            detail_address=brand_data.get() if brand_data else None'detail_address', '') if brand_data else None,
            latitude=brand_data.get() if brand_data else None'latitude') if brand_data else None,
            longitude=brand_data.get() if brand_data else None'longitude') if brand_data else None,
            phone=brand_data.get() if brand_data else None'phone', '') if brand_data else None,
            email=brand_data.get() if brand_data else None'email', '') if brand_data else None,
            store_type='main',
            status='active',
            opening_hours='09:00-18:00',
            created_by=brand_data.get() if brand_data else None'created_by') if brand_data else None,
            created_at=datetime.now()
        )

        db.session.add(store)
        db.session.flush()
        return store

    def _create_brand_admin(self,  brand_id,  creator_user_id):
        """브랜드 관리자 생성"""
        # 기존 사용자를 브랜드 관리자로 설정
        admin_role = EmployeeRole(
            brand_id=brand_id,
            user_id=creator_user_id,
            role='brand_admin',
            permissions=json.dumps([
                'brand_management',
                'store_management',
                'employee_management',
                'menu_management',
                'inventory_management',
                'order_management',
                'report_management',
                'settings_management'
            ]),
            is_active=True,
            created_at=datetime.now()
        )

        db.session.add(admin_role)
        db.session.flush()
        return admin_role

    def _create_brand_settings(self,  brand_id):
        """브랜드 기본 설정 생성"""
        settings = BrandSettings(
            brand_id=brand_id,
            settings_type='general',
            settings_data=json.dumps({
                'business_hours': {
                    'monday': {'open': '09:00', 'close': '18:00'},
                    'tuesday': {'open': '09:00', 'close': '18:00'},
                    'wednesday': {'open': '09:00', 'close': '18:00'},
                    'thursday': {'open': '09:00', 'close': '18:00'},
                    'friday': {'open': '09:00', 'close': '18:00'},
                    'saturday': {'open': '10:00', 'close': '17:00'},
                    'sunday': {'open': '10:00', 'close': '17:00'}
                },
                'notifications': {
                    'attendance_alerts': True,
                    'inventory_alerts': True,
                    'sales_alerts': True,
                    'system_alerts': True
                },
                'work_rules': {
                    'overtime_threshold': 8,
                    'break_time': 60,
                    'weekly_work_hours': 40
                },
                'inventory': {
                    'low_stock_threshold': 10,
                    'auto_reorder': False,
                    'stock_check_frequency': 'daily'
                }
            }),
            created_at=datetime.now()
        )

        db.session.add(settings)
        db.session.flush()
        return settings

    def _create_menu_categories(self,  brand_id):
        """메뉴 카테고리 생성"""
        categories = []
        for cat_data in self.default_templates['menu_categories'] if default_templates is not None else None:
            category = MenuCategory(
                brand_id=brand_id,
                name=cat_data['name'] if cat_data is not None else None,
                description=cat_data['description'] if cat_data is not None else None,
                sort_order=cat_data['sort_order'] if cat_data is not None else None,
                is_active=True,
                created_at=datetime.now()
            )
            db.session.add(category)
            categories.append(category)

        db.session.flush()
        return categories

    def _create_work_rules(self,  brand_id):
        """근무 규칙 생성"""
        rules = []
        for rule_data in self.default_templates['work_rules'] if default_templates is not None else None:
            rule = WorkRule(
                brand_id=brand_id,
                name=rule_data['name'] if rule_data is not None else None,
                work_start_time=rule_data['work_start_time'] if rule_data is not None else None,
                work_end_time=rule_data['work_end_time'] if rule_data is not None else None,
                break_start_time=rule_data['break_start_time'] if rule_data is not None else None,
                break_end_time=rule_data['break_end_time'] if rule_data is not None else None,
                overtime_threshold=rule_data['overtime_threshold'] if rule_data is not None else None,
                weekly_work_hours=rule_data['weekly_work_hours'] if rule_data is not None else None,
                is_active=True,
                created_at=datetime.now()
            )
            db.session.add(rule)
            rules.append(rule)

        db.session.flush()
        return rules

    def _create_notification_templates(self,  brand_id):
        """알림 템플릿 생성"""
        templates = []
        for template_data in self.default_templates['notification_templates'] if default_templates is not None else None:
            template = NotificationTemplate(
                brand_id=brand_id,
                name=template_data['name'] if template_data is not None else None,
                type=template_data['type'] if template_data is not None else None,
                title=template_data['title'] if template_data is not None else None,
                message=template_data['message'] if template_data is not None else None,
                is_active=template_data['is_active'] if template_data is not None else None,
                created_at=datetime.now()
            )
            db.session.add(template)
            templates.append(template)

        db.session.flush()
        return templates

    def _create_inventory_categories(self,  brand_id):
        """재고 카테고리 생성"""
        categories = []
        for cat_data in self.default_templates['inventory_categories'] if default_templates is not None else None:
            category = InventoryCategory(
                brand_id=brand_id,
                name=cat_data['name'] if cat_data is not None else None,
                description=cat_data['description'] if cat_data is not None else None,
                is_active=True,
                created_at=datetime.now()
            )
            db.session.add(category)
            categories.append(category)

        db.session.flush()
        return categories

    def _create_report_templates(self,  brand_id):
        """보고서 템플릿 생성"""
        templates = []
        for template_data in self.default_templates['report_templates'] if default_templates is not None else None:
            template = ReportTemplate(
                brand_id=brand_id,
                name=template_data['name'] if template_data is not None else None,
                type=template_data['type'] if template_data is not None else None,
                description=template_data['description'] if template_data is not None else None,
                is_active=template_data['is_active'] if template_data is not None else None,
                created_at=datetime.now()
            )
            db.session.add(template)
            templates.append(template)

        db.session.flush()
        return templates

    def _create_order_templates(self,  brand_id):
        """발주 템플릿 생성"""
        # 기본 발주 템플릿 생성
        order_template = OrderTemplate(
            brand_id=brand_id,
            name='기본 발주 템플릿',
            description='기본 발주 템플릿',
            template_data=json.dumps({
                'supplier_info': {},
                'items': [],
                'delivery_schedule': 'weekly',
                'payment_terms': 'net_30'
            }),
            is_active=True,
            created_at=datetime.now()
        )

        db.session.add(order_template)
        db.session.flush()
        return [order_template]

    def _create_onboarding_status(self,  brand_id):
        """온보딩 상태 생성"""
        onboarding = {
            'brand_id': brand_id,
            'step': 'brand_created',
            'completed_steps': ['brand_created'],
            'pending_steps': [
                'store_setup',
                'employee_setup',
                'menu_setup',
                'inventory_setup',
                'settings_configuration',
                'training_completed'
            ],
            'progress': 10,
            'created_at': datetime.now()
        }

        # 온보딩 상태를 시스템 설정에 저장
        system_setting = SystemSettings(
            setting_key=f'onboarding_status_{brand_id}',
            setting_value=json.dumps(onboarding),
            created_at=datetime.now()
        )

        db.session.add(system_setting)
        db.session.flush()
        return onboarding


# 전역 인스턴스
brand_registration_system = BrandRegistrationSystem()


@brand_registration_bp.route('/api/admin/create-brand-with-related-data', methods=['POST'])
@login_required
def create_brand_with_related_data():
    """브랜드와 연관 데이터를 함께 생성하는 API"""
    try:
        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'address']
        for field in required_fields if required_fields is not None:
            if not data.get() if data else Nonefield) if data else None:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 누락되었습니다: {field}'
                }), 400

        # 브랜드명 중복 체크
        existing_brand = Brand.query.filter(
            Brand.name == data['name'] if data is not None else None
        ).first()

        if existing_brand:
            return jsonify({
                'success': False,
                'error': '이미 존재하는 브랜드명입니다.'
            }), 400

        # 주소 중복 체크 (선택적)
        if data.get() if data else None'address') if data else None:
            existing_address = Brand.query.filter(
                Brand.address == data['address'] if data is not None else None
            ).first()

            if existing_address:
                return jsonify({
                    'success': False,
                    'error': '이미 등록된 주소입니다.',
                    'existing_brand': existing_address.name
                }), 400

        # 브랜드 및 연관 데이터 생성
        result = brand_registration_system.create_brand_with_related_data(
            data, current_user.id
        )

        logger.info(f"브랜드 생성 완료: {result['brand'] if result is not None else None.name} (ID: {result['brand'] if result is not None else None.id})")

        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'brand_id': result['brand'] if result is not None else None.id,
            'brand_name': result['brand'] if result is not None else None.name,
            'onboarding_url': f'/admin/brand-onboarding/{result["brand"] if result is not None else None.id}',
            'related_data_summary': {
                'store_count': 1,
                'admin_count': 1,
                'menu_categories': len(result['related_data'] if result is not None else None['menu_categories']),
                'work_rules': len(result['related_data'] if result is not None else None['work_rules']),
                'notification_templates': len(result['related_data'] if result is not None else None['notification_templates']),
                'inventory_categories': len(result['related_data'] if result is not None else None['inventory_categories']),
                'report_templates': len(result['related_data'] if result is not None else None['report_templates'])
            }
        })

    except Exception as e:
        logger.error(f"브랜드 생성 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'브랜드 생성 중 오류가 발생했습니다: {str(e)}'
        }), 500


@brand_registration_bp.route('/api/admin/check-brand-duplicate', methods=['POST'])
@login_required
def check_brand_duplicate():
    """브랜드 중복 체크 API"""
    try:
        data = request.get_json()
        name = data.get() if data else None'name', '') if data else None.strip() if None is not None else ''
        address = data.get() if data else None'address', '') if data else None.strip() if None is not None else ''
        exclude_id = data.get() if data else None'exclude_id') if data else None

        duplicates = []

        # 브랜드명 중복 체크
        if name:
            name_query = Brand.query.filter(Brand.name == name)
            if exclude_id:
                name_query = name_query.filter(Brand.id != exclude_id)

            existing_name = name_query.first()
            if existing_name:
                duplicates.append({
                    'type': 'name',
                    'field': '브랜드명',
                    'value': name,
                    'existing_brand': existing_name.name,
                    'existing_id': existing_name.id
                })

        # 주소 중복 체크
        if address:
            address_query = Brand.query.filter(Brand.address == address)
            if exclude_id:
                address_query = address_query.filter(Brand.id != exclude_id)

            existing_address = address_query.first()
            if existing_address:
                duplicates.append({
                    'type': 'address',
                    'field': '주소',
                    'value': address,
                    'existing_brand': existing_address.name,
                    'existing_id': existing_address.id
                })

        return jsonify({
            'success': True,
            'has_duplicates': len(duplicates) > 0,
            'duplicates': duplicates
        })

    except Exception as e:
        logger.error(f"브랜드 중복 체크 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'중복 체크 중 오류가 발생했습니다: {str(e)}'
        }), 500


@brand_registration_bp.route('/api/admin/get-brand-related-data/<int:brand_id>', methods=['GET'])
@login_required
def get_brand_related_data(brand_id):
    """브랜드 연관 데이터 조회 API"""
    try:
        brand = Brand.query.get_or_404(brand_id)

        # 연관 데이터 조회
        stores = Store.query.filter(Store.brand_id == brand_id).all()
        employees = Employee.query.filter(Employee.brand_id == brand_id).all()
        menu_categories = MenuCategory.query.filter(MenuCategory.brand_id == brand_id).all()
        work_rules = WorkRule.query.filter(WorkRule.brand_id == brand_id).all()
        notification_templates = NotificationTemplate.query.filter(
            NotificationTemplate.brand_id == brand_id
        ).all()
        inventory_categories = InventoryCategory.query.filter(
            InventoryCategory.brand_id == brand_id
        ).all()

        return jsonify({
            'success': True,
            'brand': {
                'id': brand.id,
                'name': brand.name,
                'status': brand.status,
                'created_at': brand.created_at.isoformat()
            },
            'related_data': {
                'stores': [{'id': s.id, 'name': s.name, 'status': s.status} for s in stores],
                'employees': [{'id': e.id, 'name': e.name, 'role': e.role} for e in employees],
                'menu_categories': [{'id': c.id, 'name': c.name} for c in menu_categories],
                'work_rules': [{'id': r.id, 'name': r.name} for r in work_rules],
                'notification_templates': [{'id': t.id, 'name': t.name} for t in notification_templates],
                'inventory_categories': [{'id': c.id, 'name': c.name} for c in inventory_categories]
            }
        })

    except Exception as e:
        logger.error(f"브랜드 연관 데이터 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@brand_registration_bp.route('/api/admin/sync-brand-data/<int:brand_id>', methods=['POST'])
@login_required
def sync_brand_data(brand_id):
    """브랜드 데이터 동기화 API"""
    try:
        data = request.get_json()
        sync_type = data.get() if data else None'sync_type', 'all') if data else None  # all, stores, employees, settings

        brand = Brand.query.get_or_404(brand_id)

        sync_results = {}

        if sync_type in ['all', 'stores']:
            # 매장 정보 동기화
            stores = Store.query.filter(Store.brand_id == brand_id).all()
            for store in stores if stores is not None:
                store.name = f"{brand.name} {store.name.split(' ')[-1]}" if '본점' in store.name else store.name
                store.phone = brand.phone
                store.email = brand.email
                store.address = brand.address
                store.zipcode = brand.zipcode
                store.road_address = brand.road_address
                store.jibun_address = brand.jibun_address
                store.detail_address = brand.detail_address
                store.latitude = brand.latitude
                store.longitude = brand.longitude

            sync_results['stores'] if sync_results is not None else None = len(stores)

        if sync_type in ['all', 'settings']:
            # 브랜드 설정 동기화
            brand_settings = BrandSettings.query.filter(
                BrandSettings.brand_id == brand_id
            ).first()

            if brand_settings:
                settings_data = json.loads(brand_settings.settings_data)
                # 설정 업데이트 로직
                brand_settings.settings_data = json.dumps(settings_data)
                sync_results['settings'] if sync_results is not None else None = 1

        db.session.commit()

        logger.info(f"브랜드 데이터 동기화 완료: {brand.name} (ID: {brand_id})")

        return jsonify({
            'success': True,
            'message': '브랜드 데이터 동기화가 완료되었습니다.',
            'sync_results': sync_results
        })

    except Exception as e:
        logger.error(f"브랜드 데이터 동기화 오류: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'데이터 동기화 중 오류가 발생했습니다: {str(e)}'
        }), 500
