import re
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PlatformInfo:
    """플랫폼 정보 데이터 클래스"""
    platform: str  # 'web', 'mobile', 'pos', 'tablet'
    device_type: str  # 'smartphone', 'tablet', 'desktop', 'laptop', 'pos_terminal'
    os: str  # 'ios', 'android', 'windows', 'macos', 'linux'
    browser: str  # 'chrome', 'firefox', 'safari', 'edge'
    screen_width: int
    screen_height: int
    user_agent: str
    touch_support: bool
    is_retina: bool

class PluginPlatformManager:
    """플러그인 플랫폼 관리자"""
    
    def __init__(self):
        self.platform_patterns = {
            'mobile': {
                'ios': r'iPad|iPhone|iPod',
                'android': r'Android',
                'windows_phone': r'Windows Phone'
            },
            'tablet': {
                'ipad': r'iPad',
                'android_tablet': r'Android.*Tablet|Tablet.*Android'
            },
            'desktop': {
                'windows': r'Windows NT',
                'macos': r'Mac OS X',
                'linux': r'Linux'
            }
        }
        
        self.browser_patterns = {
            'chrome': r'Chrome/(\d+)',
            'firefox': r'Firefox/(\d+)',
            'safari': r'Safari/(\d+)',
            'edge': r'Edge/(\d+)'
        }
        
    def detect_platform(self, user_agent: str, screen_width: int = 1920, screen_height: int = 1080) -> PlatformInfo:
        """플랫폼 감지"""
        user_agent_lower = user_agent.lower()
        
        # 모바일 감지
        if self._is_mobile(user_agent):
            platform = 'mobile'
            device_type = 'smartphone'
            os = self._detect_mobile_os(user_agent)
        # 태블릿 감지
        elif self._is_tablet(user_agent):
            platform = 'tablet'
            device_type = 'tablet'
            os = self._detect_tablet_os(user_agent)
        # 데스크톱 감지
        else:
            platform = 'web'
            device_type = 'desktop'
            os = self._detect_desktop_os(user_agent)
            
        # 브라우저 감지
        browser = self._detect_browser(user_agent)
        
        # 터치 지원 감지
        touch_support = self._has_touch_support(user_agent)
        
        # Retina 디스플레이 감지
        is_retina = self._is_retina_display(user_agent)
        
        return PlatformInfo(
            platform=platform,
            device_type=device_type,
            os=os,
            browser=browser,
            screen_width=screen_width,
            screen_height=screen_height,
            user_agent=user_agent,
            touch_support=touch_support,
            is_retina=is_retina
        )
        
    def _is_mobile(self, user_agent: str) -> bool:
        """모바일 기기인지 확인"""
        mobile_patterns = [
            r'Mobile|Android|iPhone|iPad|iPod|BlackBerry|Windows Phone'
        ]
        return any(re.search(pattern, user_agent, re.IGNORECASE) for pattern in mobile_patterns)
        
    def _is_tablet(self, user_agent: str) -> bool:
        """태블릿 기기인지 확인"""
        tablet_patterns = [
            r'iPad|Android.*Tablet|Tablet.*Android'
        ]
        return any(re.search(pattern, user_agent, re.IGNORECASE) for pattern in tablet_patterns)
        
    def _detect_mobile_os(self, user_agent: str) -> str:
        """모바일 OS 감지"""
        if re.search(r'iPad|iPhone|iPod', user_agent, re.IGNORECASE):
            return 'ios'
        elif re.search(r'Android', user_agent, re.IGNORECASE):
            return 'android'
        elif re.search(r'Windows Phone', user_agent, re.IGNORECASE):
            return 'windows_phone'
        return 'unknown'
        
    def _detect_tablet_os(self, user_agent: str) -> str:
        """태블릿 OS 감지"""
        if re.search(r'iPad', user_agent, re.IGNORECASE):
            return 'ios'
        elif re.search(r'Android.*Tablet|Tablet.*Android', user_agent, re.IGNORECASE):
            return 'android'
        return 'unknown'
        
    def _detect_desktop_os(self, user_agent: str) -> str:
        """데스크톱 OS 감지"""
        if re.search(r'Windows NT', user_agent, re.IGNORECASE):
            return 'windows'
        elif re.search(r'Mac OS X', user_agent, re.IGNORECASE):
            return 'macos'
        elif re.search(r'Linux', user_agent, re.IGNORECASE):
            return 'linux'
        return 'unknown'
        
    def _detect_browser(self, user_agent: str) -> str:
        """브라우저 감지"""
        for browser, pattern in self.browser_patterns.items():
            if re.search(pattern, user_agent, re.IGNORECASE):
                return browser
        return 'unknown'
        
    def _has_touch_support(self, user_agent: str) -> bool:
        """터치 지원 여부 확인"""
        touch_patterns = [
            r'touch|Touch',
            r'Mobile|Android|iPhone|iPad'
        ]
        return any(re.search(pattern, user_agent, re.IGNORECASE) for pattern in touch_patterns)
        
    def _is_retina_display(self, user_agent: str) -> bool:
        """Retina 디스플레이 여부 확인"""
        return 'Retina' in user_agent
        
    def get_platform_config(self, plugin_id: int, platform_info: PlatformInfo) -> Dict[str, Any]:
        """플랫폼별 설정 조회"""
        try:
            # 실제 구현에서는 DB에서 플랫폼 설정 조회
            # 여기서는 더미 설정 반환
            return {
                'platform': platform_info.platform,
                'enabled': True,
                'priority': 1,
                'restrictions': [],
                'ui_schema': self._get_default_ui_schema(platform_info),
                'responsive_config': self._get_responsive_config(platform_info),
                'accessibility_config': self._get_accessibility_config(platform_info)
            }
        except Exception as e:
            logger.error(f"플랫폼 설정 조회 실패: {e}")
            return self._get_fallback_config(platform_info)
            
    def _get_default_ui_schema(self, platform_info: PlatformInfo) -> Dict[str, Any]:
        """기본 UI 스키마 생성"""
        if platform_info.platform == 'mobile':
            return {
                'layout': 'stacked',
                'components': [
                    {'type': 'header', 'position': 'top'},
                    {'type': 'content', 'position': 'center'},
                    {'type': 'navigation', 'position': 'bottom'}
                ],
                'navigation': {
                    'type': 'bottom_tabs',
                    'items': ['home', 'settings', 'profile']
                },
                'themes': {
                    'primary_color': '#007AFF',
                    'background_color': '#F2F2F7',
                    'text_color': '#000000'
                }
            }
        elif platform_info.platform == 'tablet':
            return {
                'layout': 'grid',
                'components': [
                    {'type': 'sidebar', 'position': 'left'},
                    {'type': 'content', 'position': 'center'},
                    {'type': 'toolbar', 'position': 'top'}
                ],
                'navigation': {
                    'type': 'sidebar_menu',
                    'items': ['dashboard', 'analytics', 'settings']
                },
                'themes': {
                    'primary_color': '#34C759',
                    'background_color': '#FFFFFF',
                    'text_color': '#1D1D1F'
                }
            }
        else:  # web/desktop
            return {
                'layout': 'sidebar',
                'components': [
                    {'type': 'header', 'position': 'top'},
                    {'type': 'sidebar', 'position': 'left'},
                    {'type': 'content', 'position': 'center'},
                    {'type': 'footer', 'position': 'bottom'}
                ],
                'navigation': {
                    'type': 'sidebar_menu',
                    'items': ['dashboard', 'plugins', 'analytics', 'settings']
                },
                'themes': {
                    'primary_color': '#007AFF',
                    'background_color': '#FFFFFF',
                    'text_color': '#1D1D1F'
                }
            }
            
    def _get_responsive_config(self, platform_info: PlatformInfo) -> Dict[str, Any]:
        """반응형 설정 생성"""
        if platform_info.platform == 'mobile':
            return {
                'breakpoints': {
                    'xs': {'max_width': 480},
                    'sm': {'max_width': 768},
                    'md': {'max_width': 1024}
                },
                'touch_friendly': True,
                'gesture_support': True,
                'orientation_support': True
            }
        elif platform_info.platform == 'tablet':
            return {
                'breakpoints': {
                    'sm': {'max_width': 768},
                    'md': {'max_width': 1024},
                    'lg': {'max_width': 1440}
                },
                'touch_friendly': True,
                'gesture_support': True,
                'orientation_support': True
            }
        else:
            return {
                'breakpoints': {
                    'md': {'min_width': 1024},
                    'lg': {'min_width': 1440},
                    'xl': {'min_width': 1920}
                },
                'touch_friendly': False,
                'gesture_support': False,
                'orientation_support': False
            }
            
    def _get_accessibility_config(self, platform_info: PlatformInfo) -> Dict[str, Any]:
        """접근성 설정 생성"""
        return {
            'high_contrast': False,
            'large_text': False,
            'screen_reader': True,
            'keyboard_navigation': True,
            'reduced_motion': False,
            'focus_indicators': True
        }
        
    def _get_fallback_config(self, platform_info: PlatformInfo) -> Dict[str, Any]:
        """폴백 설정"""
        return {
            'platform': platform_info.platform,
            'enabled': True,
            'priority': 1,
            'restrictions': [],
            'ui_schema': self._get_default_ui_schema(platform_info),
            'responsive_config': self._get_responsive_config(platform_info),
            'accessibility_config': self._get_accessibility_config(platform_info)
        }

class PluginUIRenderer:
    """플러그인 UI 렌더러"""
    
    def __init__(self, platform_manager: PluginPlatformManager):
        self.platform_manager = platform_manager
        
    def render_ui(self, plugin_id: int, ui_schema: Dict[str, Any], platform_info: PlatformInfo) -> Dict[str, Any]:
        """UI 렌더링"""
        try:
            # 플랫폼별 설정 적용
            platform_config = self.platform_manager.get_platform_config(plugin_id, platform_info)
            
            # UI 스키마 병합
            merged_schema = self._merge_ui_schemas(ui_schema, platform_config['ui_schema'])
            
            # 반응형 설정 적용
            responsive_schema = self._apply_responsive_config(merged_schema, platform_config['responsive_config'])
            
            # 접근성 설정 적용
            accessible_schema = self._apply_accessibility_config(responsive_schema, platform_config['accessibility_config'])
            
            # 플랫폼별 최적화
            optimized_schema = self._optimize_for_platform(accessible_schema, platform_info)
            
            return {
                'success': True,
                'rendered_ui': optimized_schema,
                'platform_info': platform_info,
                'render_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"UI 렌더링 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_ui': self._get_fallback_ui(platform_info)
            }
            
    def _merge_ui_schemas(self, base_schema: Dict[str, Any], platform_schema: Dict[str, Any]) -> Dict[str, Any]:
        """UI 스키마 병합"""
        merged = base_schema.copy()
        
        # 컴포넌트 병합
        if 'components' in platform_schema:
            merged['components'] = platform_schema['components']
            
        # 네비게이션 병합
        if 'navigation' in platform_schema:
            merged['navigation'] = platform_schema['navigation']
            
        # 테마 병합
        if 'themes' in platform_schema:
            merged['themes'] = {**merged.get('themes', {}), **platform_schema['themes']}
            
        return merged
        
    def _apply_responsive_config(self, schema: Dict[str, Any], responsive_config: Dict[str, Any]) -> Dict[str, Any]:
        """반응형 설정 적용"""
        schema['responsive'] = responsive_config
        return schema
        
    def _apply_accessibility_config(self, schema: Dict[str, Any], accessibility_config: Dict[str, Any]) -> Dict[str, Any]:
        """접근성 설정 적용"""
        schema['accessibility'] = accessibility_config
        return schema
        
    def _optimize_for_platform(self, schema: Dict[str, Any], platform_info: PlatformInfo) -> Dict[str, Any]:
        """플랫폼별 최적화"""
        if platform_info.platform == 'mobile':
            # 모바일 최적화
            schema['optimizations'] = {
                'lazy_loading': True,
                'image_optimization': True,
                'touch_targets': True,
                'gesture_support': True
            }
        elif platform_info.platform == 'tablet':
            # 태블릿 최적화
            schema['optimizations'] = {
                'lazy_loading': True,
                'image_optimization': True,
                'touch_targets': True,
                'gesture_support': True,
                'split_view': True
            }
        else:
            # 데스크톱 최적화
            schema['optimizations'] = {
                'lazy_loading': False,
                'image_optimization': False,
                'touch_targets': False,
                'gesture_support': False,
                'keyboard_shortcuts': True
            }
            
        return schema
        
    def _get_fallback_ui(self, platform_info: PlatformInfo) -> Dict[str, Any]:
        """폴백 UI"""
        return {
            'layout': 'basic',
            'components': [
                {'type': 'content', 'position': 'center'}
            ],
            'themes': {
                'primary_color': '#007AFF',
                'background_color': '#FFFFFF',
                'text_color': '#000000'
            }
        }

class PluginLocalizationManager:
    """플러그인 다국어 관리자"""
    
    def __init__(self):
        self.supported_languages = ['ko', 'en', 'ja', 'zh']
        self.default_language = 'ko'
        
    def get_translation(self, plugin_id: int, language: str, key: str) -> str:
        """번역 텍스트 조회"""
        try:
            # 실제 구현에서는 DB에서 번역 데이터 조회
            # 여기서는 더미 번역 반환
            translations = self._get_dummy_translations(plugin_id)
            
            if language in translations and key in translations[language]:
                return translations[language][key]
            elif self.default_language in translations and key in translations[self.default_language]:
                return translations[self.default_language][key]
            else:
                return key
                
        except Exception as e:
            logger.error(f"번역 조회 실패: {e}")
            return key
            
    def _get_dummy_translations(self, plugin_id: int) -> Dict[str, Dict[str, str]]:
        """더미 번역 데이터"""
        return {
            'ko': {
                'title': '플러그인 제목',
                'description': '플러그인 설명',
                'install': '설치',
                'uninstall': '제거',
                'settings': '설정',
                'update': '업데이트'
            },
            'en': {
                'title': 'Plugin Title',
                'description': 'Plugin Description',
                'install': 'Install',
                'uninstall': 'Uninstall',
                'settings': 'Settings',
                'update': 'Update'
            },
            'ja': {
                'title': 'プラグインタイトル',
                'description': 'プラグイン説明',
                'install': 'インストール',
                'uninstall': 'アンインストール',
                'settings': '設定',
                'update': '更新'
            },
            'zh': {
                'title': '插件标题',
                'description': '插件描述',
                'install': '安装',
                'uninstall': '卸载',
                'settings': '设置',
                'update': '更新'
            }
        }
        
    def format_localized_data(self, data: Any, language: str, config: Dict[str, Any]) -> Any:
        """지역화된 데이터 포맷팅"""
        try:
            if isinstance(data, dict):
                return {k: self.format_localized_data(v, language, config) for k, v in data.items()}
            elif isinstance(data, list):
                return [self.format_localized_data(item, language, config) for item in data]
            elif isinstance(data, str):
                # 날짜/시간 포맷팅
                if self._is_date_string(data):
                    return self._format_date(data, language, config)
                # 숫자 포맷팅
                elif self._is_number_string(data):
                    return self._format_number(data, language, config)
                else:
                    return data
            else:
                return data
                
        except Exception as e:
            logger.error(f"데이터 포맷팅 실패: {e}")
            return data
            
    def _is_date_string(self, text: str) -> bool:
        """날짜 문자열인지 확인"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}\.\d{2}\.\d{2}'
        ]
        return any(re.search(pattern, text) for pattern in date_patterns)
        
    def _is_number_string(self, text: str) -> bool:
        """숫자 문자열인지 확인"""
        return re.match(r'^\d+(\.\d+)?$', text) is not None
        
    def _format_date(self, date_str: str, language: str, config: Dict[str, Any]) -> str:
        """날짜 포맷팅"""
        # 실제 구현에서는 언어별 날짜 포맷 적용
        return date_str
        
    def _format_number(self, number_str: str, language: str, config: Dict[str, Any]) -> str:
        """숫자 포맷팅"""
        # 실제 구현에서는 언어별 숫자 포맷 적용
        return number_str 