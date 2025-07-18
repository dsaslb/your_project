import hashlib
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import json
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, g, current_app
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
사용자 경험 향상 API
개인화 설정, 테마 관리, 접근성 기능, 사용자 피드백, 온보딩 가이드, 성능 모니터링
"""


logger = logging.getLogger(__name__)

ux_bp = Blueprint('ux', __name__, url_prefix='/api/ux')


@dataclass
class UserPreference:
    """사용자 선호도"""
    user_id: int
    theme: str
    language: str
    font_size: str
    color_scheme: str
    accessibility_mode: bool
    notifications_enabled: bool
    auto_save: bool
    dashboard_layout: str
    created_at: datetime
    updated_at: datetime


@dataclass
class UserFeedback:
    """사용자 피드백"""
    id: int
    user_id: int
    feedback_type: str  # bug, feature, general, praise
    title: str
    description: str
    rating: int  # 1-5
    category: str
    priority: str  # low, medium, high, critical
    status: str  # pending, in_progress, resolved, closed
    created_at: datetime
    updated_at: datetime


@dataclass
class OnboardingStep:
    """온보딩 단계"""
    id: int
    step_name: str
    title: str
    description: str
    order: int
    required: bool
    completed: bool
    user_id: int


class ThemeManager:
    """테마 관리 시스템"""

    def __init__(self):
        self.available_themes = {
            'light': {
                'name': '라이트 테마',
                'primary_color': '#3B82F6',
                'secondary_color': '#6B7280',
                'background_color': '#FFFFFF',
                'text_color': '#1F2937',
                'accent_color': '#10B981'
            },
            'dark': {
                'name': '다크 테마',
                'primary_color': '#60A5FA',
                'secondary_color': '#9CA3AF',
                'background_color': '#1F2937',
                'text_color': '#F9FAFB',
                'accent_color': '#34D399'
            },
            'blue': {
                'name': '블루 테마',
                'primary_color': '#1E40AF',
                'secondary_color': '#3B82F6',
                'background_color': '#EFF6FF',
                'text_color': '#1E293B',
                'accent_color': '#06B6D4'
            },
            'green': {
                'name': '그린 테마',
                'primary_color': '#059669',
                'secondary_color': '#10B981',
                'background_color': '#F0FDF4',
                'text_color': '#064E3B',
                'accent_color': '#84CC16'
            }
        }

    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        """테마 정보 반환"""
        if not self.available_themes:
            return {}
        return self.available_themes.get(theme_name) or self.available_themes['light']

    def get_all_themes(self) -> Dict[str, Any]:
        """모든 테마 반환"""
        return self.available_themes

    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> Dict[str, Any]:
        """커스텀 테마 생성"""
        if not name:
            name = 'custom'
        if not colors:
            colors = {}
        custom_theme = {
            'name': name,
            'primary_color': colors.get('primary', '#3B82F6'),
            'secondary_color': colors.get('secondary', '#6B7280'),
            'background_color': colors.get('background', '#FFFFFF'),
            'text_color': colors.get('text', '#1F2937'),
            'accent_color': colors.get('accent', '#10B981')
        }
        return custom_theme


class AccessibilityManager:
    """접근성 관리 시스템"""

    def __init__(self):
        self.accessibility_features = {
            'high_contrast': {
                'name': '고대비 모드',
                'description': '텍스트와 배경의 대비를 높여 가독성을 향상시킵니다.',
                'enabled': False
            },
            'large_text': {
                'name': '큰 텍스트',
                'description': '텍스트 크기를 키워 가독성을 향상시킵니다.',
                'enabled': False
            },
            'screen_reader': {
                'name': '스크린 리더 지원',
                'description': '스크린 리더 사용자를 위한 ARIA 라벨을 제공합니다.',
                'enabled': False
            },
            'keyboard_navigation': {
                'name': '키보드 네비게이션',
                'description': '마우스 없이 키보드만으로 모든 기능을 사용할 수 있습니다.',
                'enabled': False
            },
            'reduced_motion': {
                'name': '움직임 감소',
                'description': '애니메이션과 전환 효과를 줄여 모션 민감성을 고려합니다.',
                'enabled': False
            }
        }

    def get_accessibility_settings(self,  user_id: int) -> Dict[str, Any]:
        """사용자별 접근성 설정 반환"""
        # 실제로는 데이터베이스에서 조회
        return {
            'features': self.accessibility_features,
            'font_size': 'medium',
            'line_height': 'normal',
            'color_blindness_support': False
        }

    def update_accessibility_settings(self,  user_id: int,  settings: Dict[str,  Any]) -> bool:
        """접근성 설정 업데이트"""
        try:
            # 실제로는 데이터베이스에 저장
            logger.info(f"사용자 {user_id}의 접근성 설정 업데이트: {settings}")
            return True
        except Exception as e:
            logger.error(f"접근성 설정 업데이트 실패: {e}")
            return False


class FeedbackManager:
    """피드백 관리 시스템"""

    def __init__(self):
        self.feedback_categories = [
            'ui_ux', 'performance', 'functionality', 'bug', 'feature_request', 'general'
        ]

    def submit_feedback(self, user_id: int, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """피드백 제출"""
        try:
            feedback = UserFeedback(
                id=time.time_ns(),  # 임시 ID
                user_id=user_id,
                feedback_type=feedback_data.get('type', 'general') if feedback_data else 'general',
                title=feedback_data.get('title', '') if feedback_data else '',
                description=feedback_data.get('description', '') if feedback_data else '',
                rating=feedback_data.get('rating', 3) if feedback_data else 3,
                category=feedback_data.get('category', 'general') if feedback_data else 'general',
                priority=self._calculate_priority(feedback_data),
                status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # 실제로는 데이터베이스에 저장
            logger.info(f"피드백 제출: {feedback.title}")

            return {
                'success': True,
                'feedback_id': feedback.id,
                'message': '피드백이 성공적으로 제출되었습니다.'
            }

        except Exception as e:
            logger.error(f"피드백 제출 실패: {e}")
            return {
                'success': False,
                'error': '피드백 제출에 실패했습니다.'
            }

    def _calculate_priority(self, feedback_data: Dict[str, Any]) -> str:
        """우선순위 계산"""
        rating = feedback_data.get('rating', 3) if feedback_data else 3
        feedback_type = feedback_data.get('type', 'general') if feedback_data else 'general'

        if feedback_type == 'bug' and rating <= 2:
            return 'critical'
        elif feedback_type == 'bug':
            return 'high'
        elif rating <= 2:
            return 'high'
        elif rating >= 4:
            return 'low'
        else:
            return 'medium'

    def get_user_feedback(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 피드백 조회"""
        # 실제로는 데이터베이스에서 조회
        return [
            {
                'id': 1,
                'title': '대시보드 개선 제안',
                'description': '대시보드에 더 많은 차트를 추가하면 좋겠습니다.',
                'rating': 4,
                'category': 'feature_request',
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
        ][:limit]


class OnboardingManager:
    """온보딩 관리 시스템"""

    def __init__(self):
        self.onboarding_steps = [
            {
                'step_name': 'welcome',
                'title': '환영합니다!',
                'description': 'Your Program에 오신 것을 환영합니다. 빠른 가이드를 통해 시스템을 알아보세요.',
                'order': 1,
                'required': True
            },
            {
                'step_name': 'dashboard_tour',
                'title': '대시보드 둘러보기',
                'description': '대시보드의 주요 기능들을 살펴보고 데이터를 확인해보세요.',
                'order': 2,
                'required': True
            },
            {
                'step_name': 'first_order',
                'title': '첫 주문 생성',
                'description': '시스템의 핵심 기능인 주문 생성을 연습해보세요.',
                'order': 3,
                'required': True
            },
            {
                'step_name': 'reports',
                'title': '리포트 확인',
                'description': '다양한 리포트를 생성하고 분석해보세요.',
                'order': 4,
                'required': False
            },
            {
                'step_name': 'settings',
                'title': '설정 완료',
                'description': '개인 설정을 완료하고 시스템을 최적화하세요.',
                'order': 5,
                'required': False
            }
        ]

    def get_onboarding_progress(self, user_id: int) -> Dict[str, Any]:
        """온보딩 진행 상황 조회"""
        # 실제로는 데이터베이스에서 조회
        completed_steps = set()
        progress = {'user_id': user_id, 'steps': []}
        for step in self.onboarding_steps:
            step_info = {**step, 'completed': step['step_name'] in completed_steps}
            progress['steps'].append(step_info)
        return progress

    def complete_step(self, user_id: int, step_name: str) -> bool:
        """온보딩 단계 완료"""
        try:
            # 실제로는 데이터베이스에 저장
            logger.info(f"사용자 {user_id}의 온보딩 단계 완료: {step_name}")
            return True
        except Exception as e:
            logger.error(f"온보딩 단계 완료 실패: {e}")
            return False


class PerformanceMonitor:
    """성능 모니터링 시스템"""

    def __init__(self):
        self.performance_metrics = {}

    def track_page_load(self, user_id: int, page_name: str, load_time: float):
        """페이지 로드 시간 추적"""
        if not isinstance(page_name, str) or not isinstance(load_time, float):
            return
        if not isinstance(self.performance_metrics.get(page_name), list):
            self.performance_metrics[page_name] = []
        self.performance_metrics[page_name].append({
            'user_id': user_id,
            'load_time': load_time,
            'timestamp': datetime.utcnow().isoformat()
        })
        # 최근 100개만 유지
        if len(self.performance_metrics[page_name]) > 100:
            self.performance_metrics[page_name] = self.performance_metrics[page_name][-100:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        stats = {}

        for page_name, metrics in self.performance_metrics.items():
            if metrics:
                load_times = [m['load_time'] for m in metrics]
                stats[page_name] = {
                    'average_load_time': sum(load_times) / len(load_times),
                    'min_load_time': min(load_times),
                    'max_load_time': max(load_times),
                    'total_requests': len(metrics)
                }

        return stats


# 전역 매니저 인스턴스
theme_manager = ThemeManager()
accessibility_manager = AccessibilityManager()
feedback_manager = FeedbackManager()
onboarding_manager = OnboardingManager()
performance_monitor = PerformanceMonitor()


@ux_bp.route('/preferences', methods=['GET'])
@login_required
def get_user_preferences():
    """사용자 선호도 조회"""
    try:
        user_id = current_user.id

        # 실제로는 데이터베이스에서 조회
        preferences = {
            'theme': 'light',
            'language': 'ko',
            'font_size': 'medium',
            'color_scheme': 'default',
            'accessibility_mode': False,
            'notifications_enabled': True,
            'auto_save': True,
            'dashboard_layout': 'default'
        }

        return jsonify({
            'success': True,
            'preferences': preferences
        })

    except Exception as e:
        logger.error(f"사용자 선호도 조회 실패: {e}")
        return jsonify({'error': '사용자 선호도 조회에 실패했습니다.'}), 500


@ux_bp.route('/preferences', methods=['PUT'])
@login_required
def update_user_preferences():
    """사용자 선호도 업데이트"""
    try:
        user_id = current_user.id
        data = request.get_json()

        if not data:
            return jsonify({'error': '업데이트할 데이터가 없습니다.'}), 400

        # 실제로는 데이터베이스에 저장
        logger.info(f"사용자 {user_id}의 선호도 업데이트: {data}")

        return jsonify({
            'success': True,
            'message': '사용자 선호도가 업데이트되었습니다.'
        })

    except Exception as e:
        logger.error(f"사용자 선호도 업데이트 실패: {e}")
        return jsonify({'error': '사용자 선호도 업데이트에 실패했습니다.'}), 500


@ux_bp.route('/themes', methods=['GET'])
def get_themes():
    """사용 가능한 테마 조회"""
    try:
        themes = theme_manager.get_all_themes()

        return jsonify({
            'success': True,
            'themes': themes
        })

    except Exception as e:
        logger.error(f"테마 조회 실패: {e}")
        return jsonify({'error': '테마 조회에 실패했습니다.'}), 500


@ux_bp.route('/themes/custom', methods=['POST'])
@login_required
def create_custom_theme():
    data = request.get_json() or {}
    name = data.get('name') or 'custom'
    colors = data.get('colors') or {}
    return jsonify(theme_manager.create_custom_theme(str(name), dict(colors)))


@ux_bp.route('/accessibility', methods=['GET'])
@login_required
def get_accessibility_settings():
    """접근성 설정 조회"""
    try:
        user_id = current_user.id
        settings = accessibility_manager.get_accessibility_settings(user_id)

        return jsonify({
            'success': True,
            'settings': settings
        })

    except Exception as e:
        logger.error(f"접근성 설정 조회 실패: {e}")
        return jsonify({'error': '접근성 설정 조회에 실패했습니다.'}), 500


@ux_bp.route('/accessibility', methods=['PUT'])
@login_required
def update_accessibility_settings():
    """접근성 설정 업데이트"""
    try:
        user_id = current_user.id
        data = request.get_json()

        if not data:
            return jsonify({'error': '업데이트할 설정이 없습니다.'}), 400

        success = accessibility_manager.update_accessibility_settings(user_id,  data)

        if success:
            return jsonify({
                'success': True,
                'message': '접근성 설정이 업데이트되었습니다.'
            })
        else:
            return jsonify({'error': '접근성 설정 업데이트에 실패했습니다.'}), 500

    except Exception as e:
        logger.error(f"접근성 설정 업데이트 실패: {e}")
        return jsonify({'error': '접근성 설정 업데이트에 실패했습니다.'}), 500


@ux_bp.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    """피드백 제출"""
    try:
        user_id = current_user.id
        data = request.get_json()

        if not data:
            return jsonify({'error': '피드백 내용이 필요합니다.'}), 400

        result = feedback_manager.submit_feedback(user_id,  data)

        return jsonify(result)

    except Exception as e:
        logger.error(f"피드백 제출 실패: {e}")
        return jsonify({'error': '피드백 제출에 실패했습니다.'}), 500


@ux_bp.route('/feedback', methods=['GET'])
@login_required
def get_user_feedback():
    """사용자 피드백 조회"""
    try:
        user_id = current_user.id
        limit = request.args.get('limit', 10, type=int) if args else 10

        feedback_list = feedback_manager.get_user_feedback(user_id,  limit)

        return jsonify({
            'success': True,
            'feedback': feedback_list
        })

    except Exception as e:
        logger.error(f"사용자 피드백 조회 실패: {e}")
        return jsonify({'error': '사용자 피드백 조회에 실패했습니다.'}), 500


@ux_bp.route('/onboarding/progress', methods=['GET'])
@login_required
def get_onboarding_progress():
    """온보딩 진행 상황 조회"""
    try:
        user_id = current_user.id
        progress = onboarding_manager.get_onboarding_progress(user_id)

        return jsonify({
            'success': True,
            'progress': progress
        })

    except Exception as e:
        logger.error(f"온보딩 진행 상황 조회 실패: {e}")
        return jsonify({'error': '온보딩 진행 상황 조회에 실패했습니다.'}), 500


@ux_bp.route('/onboarding/complete-step', methods=['POST'])
@login_required
def complete_onboarding_step():
    data = request.get_json() or {}
    user_id = current_user.id
    step_name = data.get('step_name') or ''
    return jsonify({'success': onboarding_manager.complete_step(user_id, str(step_name))})


@ux_bp.route('/performance/track', methods=['POST'])
@login_required
def track_performance():
    data = request.get_json() or {}
    user_id = current_user.id
    page_name = data.get('page_name') or ''
    load_time = data.get('load_time')
    if load_time is None:
        load_time = 0.0
    try:
        load_time = float(load_time)
    except (TypeError, ValueError):
        load_time = 0.0
    if not hasattr(performance_monitor, 'performance_metrics') or not isinstance(performance_monitor.performance_metrics, dict):
        performance_monitor.performance_metrics = {}
    performance_monitor.track_page_load(user_id, str(page_name), load_time)
    return jsonify({'success': True})


@ux_bp.route('/performance/stats', methods=['GET'])
@login_required
def get_performance_stats():
    """성능 통계 조회"""
    try:
        stats = performance_monitor.get_performance_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"성능 통계 조회 실패: {e}")
        return jsonify({'error': '성능 통계 조회에 실패했습니다.'}), 500
