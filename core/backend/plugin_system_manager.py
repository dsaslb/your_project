"""
플러그인 시스템 통합 매니저
전체 플러그인 시스템을 관리하고 운영 환경에서 사용할 수 있도록 통합
"""

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict

# 플러그인 시스템 모듈들 import
plugin_registry = None
plugin_api = None
plugin_config = None
plugin_events = None
plugin_database = None
plugin_security = None
plugin_marketplace = None
plugin_integration_test = None
system_optimizer = None

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_registry_module = importlib.import_module('core.backend.plugin_registry')
    plugin_registry = plugin_registry_module.plugin_registry
except ImportError as e:
    logging.warning(f"plugin_registry 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_api_module = importlib.import_module('core.backend.plugin_api')
    plugin_api = plugin_api_module.plugin_api
except ImportError as e:
    logging.warning(f"plugin_api 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_config_module = importlib.import_module('core.backend.plugin_config')
    plugin_config = plugin_config_module.plugin_config
except ImportError as e:
    logging.warning(f"plugin_config 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_events_module = importlib.import_module('core.backend.plugin_events')
    plugin_events = plugin_events_module.plugin_events
except ImportError as e:
    logging.warning(f"plugin_events 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_database_module = importlib.import_module('core.backend.plugin_database')
    plugin_database = plugin_database_module.plugin_database
except ImportError as e:
    logging.warning(f"plugin_database 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_security_module = importlib.import_module('core.backend.plugin_security')
    plugin_security = plugin_security_module.plugin_security
except ImportError as e:
    logging.warning(f"plugin_security 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_marketplace_module = importlib.import_module('core.backend.plugin_marketplace')
    plugin_marketplace = plugin_marketplace_module.plugin_marketplace
except ImportError as e:
    logging.warning(f"plugin_marketplace 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_integration_test_module = importlib.import_module('core.backend.plugin_integration_test')
    plugin_integration_test = plugin_integration_test_module.plugin_integration_test
except ImportError as e:
    logging.warning(f"plugin_integration_test 모듈을 import할 수 없습니다: {e}")

try:
    # 동적 import로 안전하게 처리
    import importlib
    plugin_optimizer_module = importlib.import_module('core.backend.plugin_optimizer')
    system_optimizer = plugin_optimizer_module.system_optimizer
except ImportError as e:
    logging.warning(f"plugin_optimizer 모듈을 import할 수 없습니다: {e}")

logger = logging.getLogger(__name__)

class PluginSystemManager:
    """플러그인 시스템 통합 매니저"""
    
    def __init__(self):
        self.system_status = {
            'initialized': False,
            'started': False,
            'health_status': 'unknown',
            'last_check': None,
            'active_plugins': 0,
            'total_plugins': 0
        }
        
        self.components: Dict[str, Any] = {
            'registry': None,
            'api': None,
            'config': None,
            'events': None,
            'database': None,
            'security': None,
            'marketplace': None,
            'optimizer': None
        }
        
        self.health_check_thread = None
        self.health_check_interval = 60  # 1분
        
    def initialize_system(self) -> Any:
        """플러그인 시스템 초기화"""
        logger.info("플러그인 시스템 초기화 시작")
        
        init_results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. 플러그인 레지스트리 초기화
            try:
                self.components['registry'] = plugin_registry
                init_results['components']['registry'] = 'success'
                logger.info("플러그인 레지스트리 초기화 완료")
            except Exception as e:
                init_results['components']['registry'] = 'failed'
                init_results['errors'].append(f"레지스트리 초기화 실패: {e}")
                logger.error(f"레지스트리 초기화 실패: {e}")
            
            # 2. 플러그인 설정 초기화
            try:
                self.components['config'] = plugin_config
                init_results['components']['config'] = 'success'
                logger.info("플러그인 설정 초기화 완료")
            except Exception as e:
                init_results['components']['config'] = 'failed'
                init_results['errors'].append(f"설정 초기화 실패: {e}")
                logger.error(f"설정 초기화 실패: {e}")
            
            # 3. 플러그인 이벤트 시스템 초기화
            try:
                self.components['events'] = plugin_events
                init_results['components']['events'] = 'success'
                logger.info("플러그인 이벤트 시스템 초기화 완료")
            except Exception as e:
                init_results['components']['events'] = 'failed'
                init_results['errors'].append(f"이벤트 시스템 초기화 실패: {e}")
                logger.error(f"이벤트 시스템 초기화 실패: {e}")
            
            # 4. 플러그인 데이터베이스 초기화
            try:
                self.components['database'] = plugin_database
                init_results['components']['database'] = 'success'
                logger.info("플러그인 데이터베이스 초기화 완료")
            except Exception as e:
                init_results['components']['database'] = 'failed'
                init_results['errors'].append(f"데이터베이스 초기화 실패: {e}")
                logger.error(f"데이터베이스 초기화 실패: {e}")
            
            # 5. 플러그인 보안 시스템 초기화
            try:
                self.components['security'] = plugin_security
                init_results['components']['security'] = 'success'
                logger.info("플러그인 보안 시스템 초기화 완료")
            except Exception as e:
                init_results['components']['security'] = 'failed'
                init_results['errors'].append(f"보안 시스템 초기화 실패: {e}")
                logger.error(f"보안 시스템 초기화 실패: {e}")
            
            # 6. 플러그인 마켓플레이스 초기화
            try:
                self.components['marketplace'] = plugin_marketplace
                init_results['components']['marketplace'] = 'success'
                logger.info("플러그인 마켓플레이스 초기화 완료")
            except Exception as e:
                init_results['components']['marketplace'] = 'failed'
                init_results['errors'].append(f"마켓플레이스 초기화 실패: {e}")
                logger.error(f"마켓플레이스 초기화 실패: {e}")
            
            # 7. 플러그인 최적화 시스템 초기화
            try:
                if system_optimizer is not None:
                    self.components['optimizer'] = system_optimizer
                    init_results['components']['optimizer'] = 'success'
                    logger.info("플러그인 최적화 시스템 초기화 완료")
                else:
                    init_results['components']['optimizer'] = 'failed'
                    init_results['errors'].append("최적화 시스템 모듈을 찾을 수 없습니다")
                    logger.error("최적화 시스템 모듈을 찾을 수 없습니다")
            except Exception as e:
                init_results['components']['optimizer'] = 'failed'
                init_results['errors'].append(f"최적화 시스템 초기화 실패: {e}")
                logger.error(f"최적화 시스템 초기화 실패: {e}")
            
            # 8. 플러그인 API 초기화
            try:
                self.components['api'] = plugin_api
                init_results['components']['api'] = 'success'
                logger.info("플러그인 API 초기화 완료")
            except Exception as e:
                init_results['components']['api'] = 'failed'
                init_results['errors'].append(f"API 초기화 실패: {e}")
                logger.error(f"API 초기화 실패: {e}")
            
            # 초기화 상태 업데이트
            success_count = sum(1 for status in init_results['components'].values() if status == 'success')
            total_count = len(init_results['components'])
            
            if success_count == total_count:
                self.system_status['initialized'] = True
                self.system_status['health_status'] = 'healthy'
                logger.info("플러그인 시스템 초기화 완료")
            elif success_count > total_count // 2:
                self.system_status['initialized'] = True
                self.system_status['health_status'] = 'degraded'
                logger.warning("플러그인 시스템 초기화 완료 (일부 컴포넌트 실패)")
            else:
                self.system_status['health_status'] = 'unhealthy'
                logger.error("플러그인 시스템 초기화 실패")
            
            self.system_status['last_check'] = datetime.now()
            
        except Exception as e:
            init_results['errors'].append(f"시스템 초기화 중 오류: {e}")
            logger.error(f"시스템 초기화 중 오류: {e}")
        
        return init_results
    
    def start_system(self) -> Any:
        """플러그인 시스템 시작"""
        if not self.system_status['initialized']:
            return {'error': '시스템이 초기화되지 않았습니다'}
        
        logger.info("플러그인 시스템 시작")
        
        start_results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'errors': []
        }
        
        try:
            # 1. 플러그인 로드
            if self.components['registry']:
                try:
                    self.components['registry'].load_all_plugins()
                    start_results['components']['plugin_loading'] = 'success'
                    logger.info("플러그인 로드 완료")
                except Exception as e:
                    start_results['components']['plugin_loading'] = 'failed'
                    start_results['errors'].append(f"플러그인 로드 실패: {e}")
                    logger.error(f"플러그인 로드 실패: {e}")
            
            # 2. 이벤트 시스템 시작
            if self.components['events']:
                try:
                    self.components['events'].start_event_system()
                    start_results['components']['event_system'] = 'success'
                    logger.info("이벤트 시스템 시작 완료")
                except Exception as e:
                    start_results['components']['event_system'] = 'failed'
                    start_results['errors'].append(f"이벤트 시스템 시작 실패: {e}")
                    logger.error(f"이벤트 시스템 시작 실패: {e}")
            
            # 3. 최적화 시스템 시작
            if self.components['optimizer']:
                try:
                    self.components['optimizer'].start_auto_optimization()
                    start_results['components']['optimizer'] = 'success'
                    logger.info("최적화 시스템 시작 완료")
                except Exception as e:
                    start_results['components']['optimizer'] = 'failed'
                    start_results['errors'].append(f"최적화 시스템 시작 실패: {e}")
                    logger.error(f"최적화 시스템 시작 실패: {e}")
            
            # 4. 헬스 체크 시작
            self._start_health_check()
            start_results['components']['health_check'] = 'success'
            logger.info("헬스 체크 시작 완료")
            
            # 시스템 상태 업데이트
            self.system_status['started'] = True
            self.system_status['last_check'] = datetime.now()
            
            # 활성 플러그인 수 업데이트
            if self.components['registry']:
                try:
                    self.system_status['active_plugins'] = len(self.components['registry'].get_active_plugins())
                    self.system_status['total_plugins'] = len(self.components['registry'].get_all_plugins())
                except Exception:
                    pass
            
            logger.info("플러그인 시스템 시작 완료")
            
        except Exception as e:
            start_results['errors'].append(f"시스템 시작 중 오류: {e}")
            logger.error(f"시스템 시작 중 오류: {e}")
        
        return start_results
    
    def stop_system(self) -> Any:
        """플러그인 시스템 중지"""
        logger.info("플러그인 시스템 중지")
        
        stop_results = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'errors': []
        }
        
        try:
            # 1. 헬스 체크 중지
            self._stop_health_check()
            stop_results['components']['health_check'] = 'stopped'
            
            # 2. 최적화 시스템 중지
            if self.components['optimizer']:
                try:
                    self.components['optimizer'].stop_auto_optimization()
                    stop_results['components']['optimizer'] = 'stopped'
                except Exception as e:
                    stop_results['errors'].append(f"최적화 시스템 중지 실패: {e}")
            
            # 3. 이벤트 시스템 중지
            if self.components['events']:
                try:
                    self.components['events'].stop_event_system()
                    stop_results['components']['event_system'] = 'stopped'
                except Exception as e:
                    stop_results['errors'].append(f"이벤트 시스템 중지 실패: {e}")
            
            # 4. 플러그인 언로드
            if self.components['registry']:
                try:
                    self.components['registry'].unload_all_plugins()
                    stop_results['components']['plugin_unloading'] = 'success'
                except Exception as e:
                    stop_results['errors'].append(f"플러그인 언로드 실패: {e}")
            
            # 시스템 상태 업데이트
            self.system_status['started'] = False
            self.system_status['health_status'] = 'stopped'
            self.system_status['last_check'] = datetime.now()
            
            logger.info("플러그인 시스템 중지 완료")
            
        except Exception as e:
            stop_results['errors'].append(f"시스템 중지 중 오류: {e}")
            logger.error(f"시스템 중지 중 오류: {e}")
        
        return stop_results
    
    def get_system_status(self) -> Any:
        """시스템 상태 조회"""
        status = self.system_status.copy()
        
        # 컴포넌트별 상태 추가
        status['components'] = {}
        for name, component in self.components.items():
            if component:
                try:
                    if hasattr(component, 'get_status'):
                        status['components'][name] = component.get_status()
                    else:
                        status['components'][name] = 'available'
                except Exception:
                    status['components'][name] = 'error'
            else:
                status['components'][name] = 'unavailable'
        
        # 성능 정보 추가
        if self.components['optimizer']:
            try:
                performance_report = self.components['optimizer'].get_system_status()
                status['performance'] = performance_report
            except Exception:
                pass
        
        return status
    
    def run_health_check(self) -> Any:
        """헬스 체크 실행"""
        health_result = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'components': {},
            'errors': []
        }
        
        try:
            # 각 컴포넌트별 헬스 체크
            for name, component in self.components.items():
                if component:
                    try:
                        if hasattr(component, 'health_check'):
                            component_status = component.health_check()
                        else:
                            component_status = {'status': 'available'}
                        health_result['components'][name] = component_status
                    except Exception as e:
                        health_result['components'][name] = {'status': 'error', 'error': str(e)}
                        health_result['errors'].append(f"{name}: {e}")
                else:
                    health_result['components'][name] = {'status': 'unavailable'}
            
            # 전체 상태 결정
            error_count = sum(1 for comp in health_result['components'].values() 
                            if comp.get('status') == 'error')
            unavailable_count = sum(1 for comp in health_result['components'].values() 
                                  if comp.get('status') == 'unavailable')
            
            if error_count == 0 and unavailable_count == 0:
                health_result['overall_status'] = 'healthy'
                self.system_status['health_status'] = 'healthy'
            elif error_count == 0:
                health_result['overall_status'] = 'degraded'
                self.system_status['health_status'] = 'degraded'
            else:
                health_result['overall_status'] = 'unhealthy'
                self.system_status['health_status'] = 'unhealthy'
            
            self.system_status['last_check'] = datetime.now()
            
        except Exception as e:
            health_result['overall_status'] = 'error'
            health_result['errors'].append(f"헬스 체크 실행 중 오류: {e}")
            logger.error(f"헬스 체크 실행 중 오류: {e}")
        
        return health_result
    
    def _start_health_check(self):
        """헬스 체크 스레드 시작"""
        if self.health_check_thread is None or not self.health_check_thread.is_alive():
            self.health_check_thread = threading.Thread(
                target=self._health_check_loop,
                daemon=True
            )
            self.health_check_thread.start()
    
    def _stop_health_check(self):
        """헬스 체크 스레드 중지"""
        # 스레드 중지 로직 (간단한 구현)
        pass
    
    def _health_check_loop(self):
        """헬스 체크 루프"""
        while self.system_status['started']:
            try:
                self.run_health_check()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"헬스 체크 루프 오류: {e}")
                time.sleep(self.health_check_interval)
    
    def get_system_info(self) -> Any:
        """시스템 정보 조회"""
        return {
            'version': '1.0.0',
            'components_count': len(self.components),
            'initialized': self.system_status['initialized'],
            'started': self.system_status['started'],
            'health_status': self.system_status['health_status'],
            'last_check': self.system_status['last_check'],
            'active_plugins': self.system_status['active_plugins'],
            'total_plugins': self.system_status['total_plugins']
        }

# 전역 인스턴스
plugin_system_manager = PluginSystemManager() 