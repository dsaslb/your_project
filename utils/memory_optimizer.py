"""
메모리 사용량 최적화 시스템
메모리 누수 방지 및 효율적 메모리 관리
"""

import gc
import psutil
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from weakref import WeakValueDictionary

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    def __init__(self, auto_cleanup: bool = True, cleanup_interval: int = 300):
        self.auto_cleanup = auto_cleanup
        self.cleanup_interval = cleanup_interval
        self.memory_threshold = 0.8  # 80% 메모리 사용 시 경고
        self.weak_refs = WeakValueDictionary()
        self.memory_stats = {
            'peak_memory': 0,
            'current_memory': 0,
            'cleanup_count': 0,
            'last_cleanup': time.time()
        }
        
        if auto_cleanup:
            self.cleanup_thread = threading.Thread(target=self._auto_cleanup_loop, daemon=True)
            self.cleanup_thread.start()
        
        logger.info("메모리 최적화 시스템 초기화 완료")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 조회"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # 물리 메모리
            'vms': memory_info.vms,  # 가상 메모리
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
            'total': psutil.virtual_memory().total
        }
    
    def check_memory_health(self) -> Dict[str, Any]:
        """메모리 상태 점검"""
        memory_usage = self.get_memory_usage()
        current_memory = memory_usage['percent']
        
        # 피크 메모리 업데이트
        if current_memory > self.memory_stats['peak_memory']:
            self.memory_stats['peak_memory'] = current_memory
        
        self.memory_stats['current_memory'] = current_memory
        
        health_status = {
            'status': 'healthy',
            'memory_usage': current_memory,
            'peak_memory': self.memory_stats['peak_memory'],
            'warning': current_memory > self.memory_threshold * 100,
            'critical': current_memory > 90
        }
        
        if health_status['critical']:
            logger.critical(f"메모리 사용량 위험: {current_memory:.1f}%")
            health_status['status'] = 'critical'
        elif health_status['warning']:
            logger.warning(f"메모리 사용량 높음: {current_memory:.1f}%")
            health_status['status'] = 'warning'
        
        return health_status
    
    def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화 실행"""
        start_time = time.time()
        initial_memory = self.get_memory_usage()
        
        # 가비지 컬렉션 실행
        collected = gc.collect()
        
        # 약한 참조 정리
        weak_ref_count = len(self.weak_refs)
        self.weak_refs.clear()
        
        # 메모리 최적화 후 상태
        final_memory = self.get_memory_usage()
        
        optimization_result = {
            'garbage_collected': collected,
            'weak_refs_cleared': weak_ref_count,
            'memory_freed_mb': (initial_memory['rss'] - final_memory['rss']) / 1024 / 1024,
            'execution_time': time.time() - start_time
        }
        
        self.memory_stats['cleanup_count'] += 1
        self.memory_stats['last_cleanup'] = time.time()
        
        logger.info(f"메모리 최적화 완료: {optimization_result['memory_freed_mb']:.2f}MB 해제")
        
        return optimization_result
    
    def _auto_cleanup_loop(self):
        """자동 정리 루프"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                
                # 메모리 상태 확인
                health = self.check_memory_health()
                
                # 메모리 사용량이 높으면 정리 실행
                if health['warning']:
                    self.optimize_memory()
                    
            except Exception as e:
                logger.error(f"자동 정리 루프 오류: {e}")
    
    def add_weak_reference(self, key: str, obj: Any):
        """약한 참조 추가"""
        self.weak_refs[key] = obj
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """최적화 통계 조회"""
        return {
            **self.memory_stats,
            'current_usage': self.get_memory_usage(),
            'health_status': self.check_memory_health(),
            'weak_refs_count': len(self.weak_refs)
        }
    
    def set_memory_threshold(self, threshold: float):
        """메모리 임계값 설정"""
        self.memory_threshold = threshold
        logger.info(f"메모리 임계값 설정: {threshold * 100}%")

# 전역 인스턴스
memory_optimizer = MemoryOptimizer() 