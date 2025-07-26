import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
from contextlib import contextmanager
import signal
import os
import sys

# psutil이 없을 경우를 대비한 안전한 import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)

class PluginSandbox:
    """플러그인 샌드박스 실행 환경"""
    
    def __init__(self, plugin_id: int, permissions: Dict[str, Any]):
        self.plugin_id = plugin_id
        self.permissions = permissions
        self.execution_start = None
        self.resource_monitor = None
        self.is_suspended = False
        
    def __enter__(self):
        """샌드박스 진입"""
        self.execution_start = time.time()
        self._start_resource_monitoring()
        self._apply_security_restrictions()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """샌드박스 종료"""
        self._stop_resource_monitoring()
        self._log_execution_summary()
        
    def _start_resource_monitoring(self):
        """리소스 모니터링 시작"""
        if PSUTIL_AVAILABLE:
            self.resource_monitor = ResourceMonitor(self.plugin_id, self.permissions)
            self.resource_monitor.start()
        
    def _stop_resource_monitoring(self):
        """리소스 모니터링 중지"""
        if self.resource_monitor:
            self.resource_monitor.stop()
            
    def _apply_security_restrictions(self):
        """보안 제한 적용"""
        # 파일시스템 제한
        if self.permissions.get('sandbox_settings', {}).get('readonly_filesystem', True):
            self._restrict_filesystem()
            
        # 네트워크 제한
        if self.permissions.get('sandbox_settings', {}).get('restricted_network', True):
            self._restrict_network()
            
    def _restrict_filesystem(self):
        """파일시스템 접근 제한"""
        # 읽기 전용 디렉토리만 허용
        allowed_paths = [
            f'/tmp/plugin_{self.plugin_id}',
            '/usr/share/plugin_common'
        ]
        
        # 실제 구현에서는 chroot나 파일시스템 네임스페이스 사용
        logger.info(f"플러그인 {self.plugin_id}: 파일시스템 제한 적용")
        
    def _restrict_network(self):
        """네트워크 접근 제한"""
        # 화이트리스트 기반 네트워크 제한
        allowed_domains = self.permissions.get('whitelist', {}).get('network_domains', [])
        
        # 실제 구현에서는 네트워크 네임스페이스나 방화벽 규칙 사용
        logger.info(f"플러그인 {self.plugin_id}: 네트워크 제한 적용 - 허용 도메인: {allowed_domains}")
        
    def _log_execution_summary(self):
        """실행 요약 로깅"""
        if self.execution_start:
            execution_time = time.time() - self.execution_start
            logger.info(f"플러그인 {self.plugin_id} 실행 완료 - 소요시간: {execution_time:.2f}초")

class ResourceMonitor:
    """리소스 사용량 모니터링"""
    
    def __init__(self, plugin_id: int, permissions: Dict[str, Any]):
        self.plugin_id = plugin_id
        self.permissions = permissions
        self.monitoring = False
        self.thread = None
        self.current_process = psutil.Process() if PSUTIL_AVAILABLE else None
        
    def start(self):
        """모니터링 시작"""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil이 설치되지 않아 리소스 모니터링을 건너뜁니다.")
            return
            
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """모니터링 중지"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
            
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                self._check_resource_limits()
                time.sleep(1)  # 1초마다 체크
            except Exception as e:
                logger.error(f"리소스 모니터링 오류: {e}")
                
    def _check_resource_limits(self):
        """리소스 제한 체크"""
        if not self.current_process:
            return
            
        # CPU 사용량 체크
        cpu_percent = self.current_process.cpu_percent()
        cpu_limit = self.permissions.get('execution_limits', {}).get('max_cpu_percent', 100)
        
        if cpu_percent > cpu_limit:
            self._handle_resource_violation('cpu', cpu_percent, cpu_limit)
            
        # 메모리 사용량 체크
        memory_info = self.current_process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_limit = self.permissions.get('execution_limits', {}).get('max_memory_mb', 512)
        
        if memory_mb > memory_limit:
            self._handle_resource_violation('memory', memory_mb, memory_limit)
            
    def _handle_resource_violation(self, resource_type: str, current: float, limit: float):
        """리소스 위반 처리"""
        logger.warning(f"플러그인 {self.plugin_id}: {resource_type} 제한 위반 - 현재: {current:.2f}, 제한: {limit}")
        
        # 보안 로그 기록
        log_security_event(self.plugin_id, 'resource_limit', {
            'resource_type': resource_type,
            'current_value': current,
            'limit_value': limit,
            'violation_percent': (current / limit) * 100
        })
        
        # 심각한 위반 시 플러그인 중단
        if (current / limit) > 1.5:  # 50% 초과
            self._suspend_plugin()
            
    def _suspend_plugin(self):
        """플러그인 중단"""
        logger.critical(f"플러그인 {self.plugin_id}: 리소스 제한 초과로 중단됨")
        # 실제 구현에서는 플러그인 프로세스 종료
        self.monitoring = False

def require_permission(permission_type: str, resource: str):
    """권한 검증 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 실제 구현에서는 현재 플러그인 컨텍스트에서 권한 확인
            plugin_context = get_current_plugin_context()
            
            if not plugin_context:
                raise PermissionError("플러그인 컨텍스트가 없습니다.")
                
            if not _check_permission(plugin_context, permission_type, resource):
                raise PermissionError(f"권한 없음: {permission_type} - {resource}")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _check_permission(plugin_context: Dict[str, Any], permission_type: str, resource: str) -> bool:
    """권한 확인"""
    permissions = plugin_context.get('permissions', {})
    
    if permission_type == 'data_access':
        return permissions.get('data_access', {}).get(resource, False)
    elif permission_type == 'api_access':
        return permissions.get('api_access', {}).get(resource, False)
    elif permission_type == 'file_access':
        return permissions.get('execution_limits', {}).get('allow_file_upload', False)
    elif permission_type == 'network_access':
        return permissions.get('execution_limits', {}).get('allow_network', False)
        
    return False

def get_current_plugin_context() -> Optional[Dict[str, Any]]:
    """현재 플러그인 컨텍스트 가져오기"""
    # 실제 구현에서는 thread-local storage나 context manager 사용
    return getattr(threading.current_thread(), '_plugin_context', None)

def set_current_plugin_context(context: Dict[str, Any]):
    """현재 플러그인 컨텍스트 설정"""
    threading.current_thread()._plugin_context = context

@contextmanager
def plugin_execution_context(plugin_id: int, permissions: Dict[str, Any]):
    """플러그인 실행 컨텍스트"""
    context = {
        'plugin_id': plugin_id,
        'permissions': permissions,
        'execution_start': datetime.utcnow()
    }
    
    set_current_plugin_context(context)
    
    try:
        with PluginSandbox(plugin_id, permissions):
            yield context
    finally:
        set_current_plugin_context(None)

def validate_plugin_security(plugin_file_path: str) -> Dict[str, Any]:
    """플러그인 보안 검증"""
    security_report = {
        'is_safe': True,
        'warnings': [],
        'errors': [],
        'recommendations': []
    }
    
    try:
        # 파일 크기 체크
        file_size = os.path.getsize(plugin_file_path)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            security_report['warnings'].append(f"파일 크기가 큽니다: {file_size / 1024 / 1024:.2f}MB")
            
        # 파일 내용 스캔 (간단한 예시)
        try:
            with open(plugin_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 위험한 패턴 체크
            dangerous_patterns = [
                'eval(',
                'exec(',
                '__import__',
                'open(',
                'subprocess',
                'os.system'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in content:
                    security_report['errors'].append(f"위험한 패턴 발견: {pattern}")
                    security_report['is_safe'] = False
        except UnicodeDecodeError:
            security_report['warnings'].append("바이너리 파일이므로 내용 스캔을 건너뜁니다.")
                
        # 권장사항
        if not security_report['errors']:
            security_report['recommendations'].append("플러그인 보안 검증을 통과했습니다.")
            
    except Exception as e:
        security_report['errors'].append(f"보안 검증 중 오류: {e}")
        security_report['is_safe'] = False
        
    return security_report

def log_security_event(plugin_id: int, event_type: str, details: Dict[str, Any], level: str = 'info'):
    """보안 이벤트 로깅"""
    log_entry = {
        'plugin_id': plugin_id,
        'event_type': event_type,
        'details': details,
        'level': level,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logger.log(
        logging.WARNING if level in ['warning', 'error', 'critical'] else logging.INFO,
        f"보안 이벤트: {log_entry}"
    )
    
    # 실제 구현에서는 DB에 저장
    # save_security_log_to_db(log_entry) 