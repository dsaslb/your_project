import os
import sqlite3
import time
import threading
import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional
import logging
import base64
import hmac
import hashlib
import json
import requests
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
from typing import Optional
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
외부 플랫폼 통합 시스템
- POS, 회계, 배달앱, 리뷰 플랫폼 실시간 연동
- API 키 관리 및 보안
- 데이터 동기화 및 충돌 해결
- 실시간 모니터링 및 알림
- 자동화된 데이터 백업 및 복구
"""


external_platform_integration = Blueprint('external_platform_integration', __name__, url_prefix='/api/external')

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """외부 플랫폼 유형"""
    POS = "pos"
    ACCOUNTING = "accounting"
    DELIVERY = "delivery"
    REVIEW = "review"
    INVENTORY = "inventory"
    PAYMENT = "payment"


class SyncStatus(Enum):
    """동기화 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class DataConflictResolution(Enum):
    """데이터 충돌 해결 방법"""
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MERGE = "merge"
    MANUAL = "manual"


class AdvancedPlatformManager:
    """고도화된 플랫폼 관리자"""

    def __init__(self):
        self.platforms = {}
        self.api_keys = {}
        self.sync_queue = []
        self.sync_history = []
        self.conflict_resolutions = {}
        self.monitoring_thread = None
        self.is_monitoring = False

        # 플랫폼별 설정 로드
        self._load_platform_configs()
        self._load_api_keys()

    def _load_platform_configs(self):
        """플랫폼 설정 로드"""
        self.platforms = {
            PlatformType.POS: {
                'name': 'POS 시스템',
                'endpoints': {
                    'orders': '/api/orders',
                    'inventory': '/api/inventory',
                    'sales': '/api/sales'
                },
                'sync_interval': 300,  # 5분
                'retry_attempts': 3,
                'timeout': 30,
                'enabled': True
            },
            PlatformType.ACCOUNTING: {
                'name': '회계 시스템',
                'endpoints': {
                    'transactions': '/api/transactions',
                    'reports': '/api/reports',
                    'ledger': '/api/ledger'
                },
                'sync_interval': 1800,  # 30분
                'retry_attempts': 3,
                'timeout': 60,
                'enabled': True
            },
            PlatformType.DELIVERY: {
                'name': '배달 플랫폼',
                'endpoints': {
                    'orders': '/api/delivery/orders',
                    'status': '/api/delivery/status',
                    'drivers': '/api/delivery/drivers'
                },
                'sync_interval': 60,  # 1분
                'retry_attempts': 5,
                'timeout': 15,
                'enabled': True
            },
            PlatformType.REVIEW: {
                'name': '리뷰 플랫폼',
                'endpoints': {
                    'reviews': '/api/reviews',
                    'ratings': '/api/ratings',
                    'sentiment': '/api/sentiment'
                },
                'sync_interval': 600,  # 10분
                'retry_attempts': 3,
                'timeout': 45,
                'enabled': True
            }
        }

    def _load_api_keys(self):
        """API 키 로드"""
        try:
            # 데이터베이스에서 API 키 로드
            api_keys = ExternalAPIKey.query.filter_by(is_active=True).all()

            for key in api_keys if api_keys is not None:
                self.api_keys[key.platform_type] if api_keys is not None else None = {
                    'key': key.api_key,
                    'secret': key.api_secret,
                    'base_url': key.base_url,
                    'last_used': key.last_used,
                    'usage_count': key.usage_count
                }

        except Exception as e:
            logger.error(f"API 키 로드 오류: {e}")

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("외부 플랫폼 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("외부 플랫폼 모니터링 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 각 플랫폼별 동기화 체크
                for platform_type, config in self.platforms.items() if platforms is not None else []:
                    if config['enabled'] if config is not None else None:
                        self._check_sync_needed(platform_type,  config)

                # 동기화 큐 처리
                self._process_sync_queue()

                # 30초 대기
                time.sleep(30)

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)

    def _check_sync_needed(self,  platform_type: PlatformType,  config: Dict):
        """동기화 필요 여부 체크"""
        try:
            # 마지막 동기화 시간 확인
            last_sync = self._get_last_sync_time(platform_type)
            current_time = datetime.utcnow()

            if not last_sync or (current_time - last_sync).total_seconds() >= config['sync_interval'] if config is not None else None:
                # 동기화 큐에 추가
                self.sync_queue.append({
                    'platform_type': platform_type,
                    'priority': 'normal',
                    'created_at': current_time,
                    'retry_count': 0
                })

        except Exception as e:
            logger.error(f"동기화 필요 여부 체크 오류 ({platform_type.value if platform_type is not None else None}): {e}")

    def _get_last_sync_time(self,  platform_type: PlatformType) -> Optional[datetime] if Optional is not None else None:
        """마지막 동기화 시간 조회"""
        try:
            # 데이터베이스에서 마지막 동기화 시간 조회
            last_sync = DataSyncLog.query.filter_by(
                platform_type=platform_type.value if platform_type is not None else None,
                status=SyncStatus.COMPLETED.value if COMPLETED is not None else None
            ).order_by(DataSyncLog.synced_at.desc()).first()

            return last_sync.synced_at if last_sync else None

        except Exception as e:
            logger.error(f"마지막 동기화 시간 조회 오류: {e}")
            return None

    def _process_sync_queue(self):
        """동기화 큐 처리"""
        try:
            if not self.sync_queue:
                return

            # 우선순위별 정렬
            self.sync_queue.sort(key=lambda x: (
                x['priority'] if x is not None else None == 'high',
                x['created_at'] if x is not None else None
            ))

            # 큐에서 하나씩 처리
            sync_item = self.sync_queue.pop(0)
            platform_type = sync_item['platform_type'] if sync_item is not None else None

            # 동기화 실행
            success = self._sync_platform(platform_type)

            if not success and sync_item['retry_count'] if sync_item is not None else None < self.platforms[platform_type] if platforms is not None else None['retry_attempts']:
                # 재시도
                sync_item['retry_count'] if sync_item is not None else None += 1
                sync_item['created_at'] if sync_item is not None else None = datetime.utcnow()
                self.sync_queue.append(sync_item)

        except Exception as e:
            logger.error(f"동기화 큐 처리 오류: {e}")

    def _sync_platform(self,  platform_type: PlatformType) -> bool:
        """플랫폼 동기화"""
        try:
            platform_config = self.platforms[platform_type] if platforms is not None else None
            api_config = self.api_keys.get() if api_keys else Noneplatform_type) if api_keys else None

            if not api_config:
                logger.error(f"API 설정이 없습니다: {platform_type.value if platform_type is not None else None}")
                return False

            # 동기화 로그 생성
            sync_log = DataSyncLog(
                platform_type=platform_type.value if platform_type is not None else None,
                status=SyncStatus.IN_PROGRESS.value if IN_PROGRESS is not None else None,
                started_at=datetime.utcnow()
            )
            db.session.add(sync_log)
            db.session.commit()

            # 플랫폼별 동기화 실행
            if platform_type == PlatformType.POS:
                success = self._sync_pos_data(api_config,  platform_config)
            elif platform_type == PlatformType.ACCOUNTING:
                success = self._sync_accounting_data(api_config, platform_config)
            elif platform_type == PlatformType.DELIVERY:
                success = self._sync_delivery_data(api_config, platform_config)
            elif platform_type == PlatformType.REVIEW:
                success = self._sync_review_data(api_config, platform_config)
            else:
                success = False

            # 동기화 결과 업데이트
            sync_log.status = SyncStatus.COMPLETED.value if COMPLETED is not None else None if success else SyncStatus.FAILED.value if FAILED is not None else None
            sync_log.completed_at = datetime.utcnow()
            db.session.commit()

            return success

        except Exception as e:
            logger.error(f"플랫폼 동기화 오류 ({platform_type.value if platform_type is not None else None}): {e}")
            return False

    def _sync_pos_data(self,  api_config: Dict,  platform_config: Dict) -> bool:
        """POS 데이터 동기화"""
        try:
            headers = self._get_auth_headers(api_config)

            # 주문 데이터 동기화
            orders_response = requests.get() if requests else None
                f"{api_config['base_url'] if api_config is not None else None}{platform_config['endpoints'] if platform_config is not None else None['orders']}",
                headers=headers,
                timeout=platform_config['timeout'] if platform_config is not None else None
            ) if requests else None

            if orders_response.status_code == 200:
                orders_data = orders_response.json()
                self._process_pos_orders(orders_data)

            # 재고 데이터 동기화
            inventory_response = requests.get() if requests else None
                f"{api_config['base_url'] if api_config is not None else None}{platform_config['endpoints'] if platform_config is not None else None['inventory']}",
                headers=headers,
                timeout=platform_config['timeout'] if platform_config is not None else None
            ) if requests else None

            if inventory_response.status_code == 200:
                inventory_data = inventory_response.json()
                self._process_pos_inventory(inventory_data)

            return True

        except Exception as e:
            logger.error(f"POS 데이터 동기화 오류: {e}")
            return False

    def _sync_accounting_data(self, api_config: Dict, platform_config: Dict) -> bool:
        """회계 데이터 동기화"""
        try:
            headers = self._get_auth_headers(api_config)

            # 거래 데이터 동기화
            transactions_response = requests.get() if requests else None
                f"{api_config['base_url'] if api_config is not None else None}{platform_config['endpoints'] if platform_config is not None else None['transactions']}",
                headers=headers,
                timeout=platform_config['timeout'] if platform_config is not None else None
            ) if requests else None

            if transactions_response.status_code == 200:
                transactions_data = transactions_response.json()
                self._process_accounting_transactions(transactions_data)

            return True

        except Exception as e:
            logger.error(f"회계 데이터 동기화 오류: {e}")
            return False

    def _sync_delivery_data(self, api_config: Dict, platform_config: Dict) -> bool:
        """배달 데이터 동기화"""
        try:
            headers = self._get_auth_headers(api_config)

            # 배달 주문 상태 동기화
            delivery_response = requests.get() if requests else None
                f"{api_config['base_url'] if api_config is not None else None}{platform_config['endpoints'] if platform_config is not None else None['orders']}",
                headers=headers,
                timeout=platform_config['timeout'] if platform_config is not None else None
            ) if requests else None

            if delivery_response.status_code == 200:
                delivery_data = delivery_response.json()
                self._process_delivery_orders(delivery_data)

            return True

        except Exception as e:
            logger.error(f"배달 데이터 동기화 오류: {e}")
            return False

    def _sync_review_data(self, api_config: Dict, platform_config: Dict) -> bool:
        """리뷰 데이터 동기화"""
        try:
            headers = self._get_auth_headers(api_config)

            # 리뷰 데이터 동기화
            reviews_response = requests.get() if requests else None
                f"{api_config['base_url'] if api_config is not None else None}{platform_config['endpoints'] if platform_config is not None else None['reviews']}",
                headers=headers,
                timeout=platform_config['timeout'] if platform_config is not None else None
            ) if requests else None

            if reviews_response.status_code == 200:
                reviews_data = reviews_response.json()
                self._process_reviews(reviews_data)

            return True

        except Exception as e:
            logger.error(f"리뷰 데이터 동기화 오류: {e}")
            return False

    def _get_auth_headers(self, api_config: Dict) -> Dict:
        """인증 헤더 생성"""
        timestamp = str(int(time.time()))
        signature = self._generate_signature(api_config['secret'] if api_config is not None else None, timestamp)

        return {
            'Authorization': f'Bearer {api_config["key"] if api_config is not None else None}',
            'X-Timestamp': timestamp,
            'X-Signature': signature,
            'Content-Type': 'application/json'
        }

    def _generate_signature(self, secret: str, timestamp: str) -> str:
        """서명 생성"""
        message = f"timestamp={timestamp}"
        signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return base64.b64encode(signature.encode('utf-8')).decode('utf-8')

    def _process_pos_orders(self, orders_data: List[Dict] if List is not None else None):
        """POS 주문 데이터 처리"""
        try:
            for order_data in orders_data if orders_data is not None:
                # 기존 주문 확인
                existing_order = Order.query.filter_by(
                    external_id=order_data.get() if order_data else None'id') if order_data else None,
                    platform_type=PlatformType.POS.value if POS is not None else None
                ).first()

                if existing_order:
                    # 업데이트
                    self._update_order(existing_order,  order_data)
                else:
                    # 새 주문 생성
                    self._create_order(order_data,  PlatformType.POS)

        except Exception as e:
            logger.error(f"POS 주문 데이터 처리 오류: {e}")

    def _process_pos_inventory(self,  inventory_data: List[Dict] if List is not None else None):
        """POS 재고 데이터 처리"""
        try:
            for item_data in inventory_data if inventory_data is not None:
                # 재고 데이터 처리 로직
                # 실제 구현에서는 Inventory 모델과 연동
                pass

        except Exception as e:
            logger.error(f"POS 재고 데이터 처리 오류: {e}")

    def _process_accounting_transactions(self,  transactions_data: List[Dict] if List is not None else None):
        """회계 거래 데이터 처리"""
        try:
            for transaction_data in transactions_data if transactions_data is not None:
                # 회계 거래 데이터 처리 로직
                # 실제 구현에서는 Transaction 모델과 연동
                pass

        except Exception as e:
            logger.error(f"회계 거래 데이터 처리 오류: {e}")

    def _process_delivery_orders(self,  delivery_data: List[Dict] if List is not None else None):
        """배달 주문 데이터 처리"""
        try:
            for delivery_order in delivery_data if delivery_data is not None:
                # 배달 주문 상태 업데이트
                order = Order.query.filter_by(
                    external_id=delivery_order.get() if delivery_order else None'order_id') if delivery_order else None,
                    platform_type=PlatformType.DELIVERY.value if DELIVERY is not None else None
                ).first()

                if order:
                    order.status = delivery_order.get() if delivery_order else None'status', order.status) if delivery_order else None
                    order.delivery_info = delivery_order
                    db.session.commit()

        except Exception as e:
            logger.error(f"배달 주문 데이터 처리 오류: {e}")

    def _process_reviews(self,  reviews_data: List[Dict] if List is not None else None):
        """리뷰 데이터 처리"""
        try:
            for review_data in reviews_data if reviews_data is not None:
                # 기존 리뷰 확인
                existing_review = Review.query.filter_by(
                    external_id=review_data.get() if review_data else None'id') if review_data else None,
                    platform_type=PlatformType.REVIEW.value if REVIEW is not None else None
                ).first()

                if existing_review:
                    # 업데이트
                    self._update_review(existing_review,  review_data)
                else:
                    # 새 리뷰 생성
                    self._create_review(review_data,  PlatformType.REVIEW)

        except Exception as e:
            logger.error(f"리뷰 데이터 처리 오류: {e}")

    def _create_order(self,  order_data: Dict,  platform_type: PlatformType):
        """주문 생성"""
        try:
            order = Order(
                external_id=order_data.get() if order_data else None'id') if order_data else None,
                platform_type=platform_type.value if platform_type is not None else None,
                customer_name=order_data.get() if order_data else None'customer_name') if order_data else None,
                total_amount=order_data.get() if order_data else None'total_amount') if order_data else None,
                status=order_data.get() if order_data else None'status', 'pending') if order_data else None,
                order_items=order_data.get() if order_data else None'items', []) if order_data else None,
                created_at=datetime.fromisoformat(order_data.get() if order_data else None'created_at') if order_data else None),
                external_data=order_data
            )

            db.session.add(order)
            db.session.commit()

            logger.info(f"새 주문 생성: {order.external_id}")

        except Exception as e:
            logger.error(f"주문 생성 오류: {e}")
            db.session.rollback()

    def _update_order(self,  order: Order,  order_data: Dict):
        """주문 업데이트"""
        try:
            # 충돌 체크
            if self._has_conflict(order,  order_data):
                self._handle_conflict(order, order_data)
                return

            # 업데이트
            order.customer_name = order_data.get() if order_data else None'customer_name', order.customer_name) if order_data else None
            order.total_amount = order_data.get() if order_data else None'total_amount', order.total_amount) if order_data else None
            order.status = order_data.get() if order_data else None'status', order.status) if order_data else None
            order.order_items = order_data.get() if order_data else None'items', order.order_items) if order_data else None
            order.external_data = order_data
            order.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"주문 업데이트: {order.external_id}")

        except Exception as e:
            logger.error(f"주문 업데이트 오류: {e}")
            db.session.rollback()

    def _create_review(self,  review_data: Dict,  platform_type: PlatformType):
        """리뷰 생성"""
        try:
            review = Review(
                external_id=review_data.get() if review_data else None'id') if review_data else None,
                platform_type=platform_type.value if platform_type is not None else None,
                customer_name=review_data.get() if review_data else None'customer_name') if review_data else None,
                rating=review_data.get() if review_data else None'rating') if review_data else None,
                content=review_data.get() if review_data else None'content') if review_data else None,
                sentiment=review_data.get() if review_data else None'sentiment') if review_data else None,
                created_at=datetime.fromisoformat(review_data.get() if review_data else None'created_at') if review_data else None),
                external_data=review_data
            )

            db.session.add(review)
            db.session.commit()

            # 부정 리뷰 알림
            if review.rating <= 2:
                self._send_negative_review_alert(review)

            logger.info(f"새 리뷰 생성: {review.external_id}")

        except Exception as e:
            logger.error(f"리뷰 생성 오류: {e}")
            db.session.rollback()

    def _update_review(self,  review: Review,  review_data: Dict):
        """리뷰 업데이트"""
        try:
            # 충돌 체크
            if self._has_conflict(review,  review_data):
                self._handle_conflict(review, review_data)
                return

            # 업데이트
            review.customer_name = review_data.get() if review_data else None'customer_name', review.customer_name) if review_data else None
            review.rating = review_data.get() if review_data else None'rating', review.rating) if review_data else None
            review.content = review_data.get() if review_data else None'content', review.content) if review_data else None
            review.sentiment = review_data.get() if review_data else None'sentiment', review.sentiment) if review_data else None
            review.external_data = review_data
            review.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"리뷰 업데이트: {review.external_id}")

        except Exception as e:
            logger.error(f"리뷰 업데이트 오류: {e}")
            db.session.rollback()

    def _has_conflict(self,  local_item: Any,  remote_data: Dict) -> bool:
        """충돌 여부 확인"""
        try:
            # 수정 시간 비교
            local_updated = local_item.updated_at or local_item.created_at
            remote_updated = datetime.fromisoformat(remote_data.get() if remote_data else None
                'updated_at', remote_data.get() if remote_data else None'created_at') if remote_data else None))

            # 로컬이 더 최신이면 충돌
            return local_updated > remote_updated

        except Exception as e:
            logger.error(f"충돌 확인 오류: {e}")
            return False

    def _handle_conflict(self, local_item: Any, remote_data: Dict):
        """충돌 처리"""
        try:
            conflict_id = f"{local_item.__class__.__name__}_{local_item.id}_{int(time.time())}"

            conflict = DataConflict(
                conflict_id=conflict_id,
                item_type=local_item.__class__.__name__,
                item_id=local_item.id,
                local_data=local_item.to_dict(),
                remote_data=remote_data,
                status='pending',
                created_at=datetime.utcnow()
            )

            db.session.add(conflict)
            db.session.commit()

            logger.warning(f"데이터 충돌 발생: {conflict_id}")

        except Exception as e:
            logger.error(f"충돌 처리 오류: {e}")
            db.session.rollback()

    def _send_negative_review_alert(self,  review: Review):
        """부정 리뷰 알림 발송"""
        try:
            # 리뷰 평점이 3점 이하인 경우 알림 발송
            if review.rating <= 3:
                message = f"부정 리뷰 알림: {review.rating}점 리뷰가 등록되었습니다. (내용: {review.content[:50] if content is not None else None}...)"

                # 브랜드별 관리자에게 알림
                if review.brand_id:
                    brand_admins = User.query.filter_by(brand_id=review.brand_id, role='brand_admin').all()
                    for admin in brand_admins if brand_admins is not None:
                        notification = Notification()
                        notification.user_id = admin.id
                        notification.title = "부정 리뷰 알림"
                        notification.content = message
                        notification.category = "REVIEW_ALERT"
                        notification.priority = "중요"
                        notification.ai_priority = "medium"
                        db.session.add(notification)
                else:
                    # 전체 관리자에게 알림
                    admins = User.query.filter_by(role='admin').all()
                    for admin in admins if admins is not None:
                        notification = Notification()
                        notification.user_id = admin.id
                        notification.title = "부정 리뷰 알림"
                        notification.content = message
                        notification.category = "REVIEW_ALERT"
                        notification.priority = "중요"
                        notification.ai_priority = "medium"
                        db.session.add(notification)

                db.session.commit()
                logger.info(f"부정 리뷰 알림 발송 완료: {review.id}")

        except Exception as e:
            logger.error(f"부정 리뷰 알림 발송 오류: {e}")
            db.session.rollback()


# 전역 플랫폼 관리자 인스턴스
platform_manager = AdvancedPlatformManager()


@external_platform_integration.route('/sync/<platform>', methods=['POST'])
@login_required
def sync_platform(platform):
    """플랫폼 데이터 동기화"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json() or {}
        data_type = data.get() if data else None'data_type', 'all') if data else None

        try:
            platform_enum = PlatformType(platform)
        except ValueError:
            return jsonify({'error': '지원하지 않는 플랫폼입니다.'}), 400

        result = platform_manager.sync_platform_data(platform_enum, data_type)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"플랫폼 동기화 오류: {e}")
        return jsonify({'error': '동기화에 실패했습니다.'}), 500


@external_platform_integration.route('/sync/all', methods=['POST'])
@login_required
def sync_all_platforms():
    """모든 플랫폼 동기화"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        results = {}

        for platform in PlatformType if PlatformType is not None:
            if platform_manager.platform_configs[platform] if platform_configs is not None else None['enabled']:
                try:
                    result = platform_manager.sync_platform_data(platform, 'all')
                    results[platform.value if platform is not None else None] if results is not None else None = result
                except Exception as e:
                    results[platform.value if platform is not None else None] if results is not None else None = {'error': str(e)}

        return jsonify({
            'results': results,
            'sync_time': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"전체 플랫폼 동기화 오류: {e}")
        return jsonify({'error': '동기화에 실패했습니다.'}), 500


@external_platform_integration.route('/status', methods=['GET'])
@login_required
def get_platform_status():
    """플랫폼 상태 조회"""
    try:
        status = platform_manager.get_sync_status()
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"플랫폼 상태 조회 오류: {e}")
        return jsonify({'error': '상태 조회에 실패했습니다.'}), 500


@external_platform_integration.route('/config', methods=['GET'])
@login_required
def get_platform_configs():
    """플랫폼 설정 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        configs = {}
        for platform, config in platform_manager.platform_configs.items() if platform_configs is not None else []:
            configs[platform.value if platform is not None else None] if configs is not None else None = {
                'name': config['name'] if config is not None else None,
                'enabled': config['enabled'] if config is not None else None,
                'sync_interval': config['sync_interval'] if config is not None else None,
                'has_api_key': bool(config['api_key'] if config is not None else None)
            }

        return jsonify({'configs': configs}), 200

    except Exception as e:
        logger.error(f"플랫폼 설정 조회 오류: {e}")
        return jsonify({'error': '설정 조회에 실패했습니다.'}), 500


@external_platform_integration.route('/config/<platform>', methods=['PUT'])
@login_required
def update_platform_config(platform):
    """플랫폼 설정 업데이트"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '설정 데이터가 필요합니다.'}), 400

        try:
            platform_enum = PlatformType(platform)
        except ValueError:
            return jsonify({'error': '지원하지 않는 플랫폼입니다.'}), 400

        config = platform_manager.platform_configs[platform_enum] if platform_configs is not None else None

        # 설정 업데이트
        if 'enabled' in data:
            config['enabled'] if config is not None else None = data['enabled'] if data is not None else None
        if 'sync_interval' in data:
            config['sync_interval'] if config is not None else None = data['sync_interval'] if data is not None else None
        if 'api_key' in data:
            platform_manager.set_api_key(platform_enum, data['api_key'] if data is not None else None)

        return jsonify({
            'success': True,
            'message': '플랫폼 설정이 업데이트되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"플랫폼 설정 업데이트 오류: {e}")
        return jsonify({'error': '설정 업데이트에 실패했습니다.'}), 500


@external_platform_integration.route('/reviews/report', methods=['GET'])
@login_required
def get_review_report():
    """리뷰 리포트 조회"""
    try:
        days = int(request.args.get() if args else None'days', 7) if args else None)
        report = platform_manager.generate_review_report(days)

        return jsonify(report), 200

    except Exception as e:
        logger.error(f"리뷰 리포트 조회 오류: {e}")
        return jsonify({'error': '리포트 생성에 실패했습니다.'}), 500
