"""
비동기 처리 최적화 시스템
백그라운드 작업 및 비동기 처리 관리
"""

import asyncio
import threading
import queue
import time
import logging
from typing import Callable, Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps

logger = logging.getLogger(__name__)

class AsyncProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.Queue()
        self.running_tasks = {}
        self.task_stats = {}
        
        # 백그라운드 워커 시작
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info(f"비동기 처리기 초기화 완료 (워커: {max_workers}개)")
    
    def async_task(self, task_type: str = "thread"):
        """비동기 작업 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if task_type == "thread":
                    return self.thread_pool.submit(func, *args, **kwargs)
                elif task_type == "process":
                    return self.process_pool.submit(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def background_task(self, priority: int = 1):
        """백그라운드 작업 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                task_id = f"{func.__name__}_{int(time.time())}"
                self.task_queue.put((priority, task_id, func, args, kwargs))
                logger.info(f"백그라운드 작업 등록: {task_id}")
                return task_id
            return wrapper
        return decorator
    
    def _worker_loop(self):
        """백그라운드 워커 루프"""
        while True:
            try:
                priority, task_id, func, args, kwargs = self.task_queue.get(timeout=1)
                
                start_time = time.time()
                self.running_tasks[task_id] = {
                    'func': func.__name__,
                    'start_time': start_time,
                    'status': 'running'
                }
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    self.running_tasks[task_id].update({
                        'status': 'completed',
                        'execution_time': execution_time,
                        'result': result
                    })
                    
                    logger.info(f"백그라운드 작업 완료: {task_id} ({execution_time:.2f}초)")
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.running_tasks[task_id].update({
                        'status': 'failed',
                        'execution_time': execution_time,
                        'error': str(e)
                    })
                    logger.error(f"백그라운드 작업 실패: {task_id} - {e}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"워커 루프 오류: {e}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """작업 상태 조회"""
        return self.running_tasks.get(task_id, {})
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """모든 작업 상태 조회"""
        return {
            'running': len([t for t in self.running_tasks.values() if t['status'] == 'running']),
            'completed': len([t for t in self.running_tasks.values() if t['status'] == 'completed']),
            'failed': len([t for t in self.running_tasks.values() if t['status'] == 'failed']),
            'queue_size': self.task_queue.qsize(),
            'tasks': self.running_tasks
        }
    
    def cleanup_completed_tasks(self, max_age: int = 3600):
        """완료된 작업 정리"""
        current_time = time.time()
        tasks_to_remove = []
        
        for task_id, task_info in self.running_tasks.items():
            if task_info['status'] in ['completed', 'failed']:
                if current_time - task_info['start_time'] > max_age:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.running_tasks[task_id]
        
        logger.info(f"완료된 작업 정리: {len(tasks_to_remove)}개")
    
    def shutdown(self):
        """프로세서 종료"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        logger.info("비동기 처리기 종료 완료")

# 전역 인스턴스
async_processor = AsyncProcessor() 