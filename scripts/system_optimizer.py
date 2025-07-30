# -*- coding: utf-8 -*-
"""
시스템 성능 최적화 및 자동 개선 스크립트
시스템 상태를 분석하고 자동으로 최적화 작업을 수행
"""

import os
import json
import shutil
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
import gc

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemOptimizer:
    """시스템 최적화 클래스"""
    
    def __init__(self):
        self.optimization_history = []
        self.optimization_config = {
            'max_log_size_mb': 50,  # 로그 파일 최대 크기
            'max_cache_size_mb': 100,  # 캐시 최대 크기
            'db_cleanup_days': 30,  # 오래된 데이터 정리 기준
            'memory_threshold': 80,  # 메모리 사용률 임계값
            'disk_threshold': 85,  # 디스크 사용률 임계값
        }
    
    def optimize_logs(self) -> Dict[str, Any]:
        """로그 파일 최적화"""
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                return {'status': 'no_logs', 'message': '로그 디렉토리가 없습니다.'}
            
            cleaned_files = []
            total_freed_mb = 0
            
            for filename in os.listdir(log_dir):
                file_path = os.path.join(log_dir, filename)
                if os.path.isfile(file_path):
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    
                    # 큰 로그 파일 압축 또는 삭제
                    if file_size_mb > self.optimization_config['max_log_size_mb']:
                        if filename.endswith('.log'):
                            # 30일 이상 된 로그 파일 삭제
                            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
                            if file_age.days > 30:
                                os.remove(file_path)
                                cleaned_files.append(filename)
                                total_freed_mb += file_size_mb
                                logger.info(f"오래된 로그 파일 삭제: {filename}")
            
            return {
                'status': 'success',
                'cleaned_files': cleaned_files,
                'freed_mb': round(total_freed_mb, 2),
                'message': f'{len(cleaned_files)}개 파일 정리, {round(total_freed_mb, 2)}MB 공간 확보'
            }
            
        except Exception as e:
            logger.error(f"로그 최적화 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def optimize_cache(self) -> Dict[str, Any]:
        """캐시 디렉토리 최적화"""
        try:
            cache_dir = 'cache'
            if not os.path.exists(cache_dir):
                return {'status': 'no_cache', 'message': '캐시 디렉토리가 없습니다.'}
            
            cleaned_files = []
            total_freed_mb = 0
            
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path):
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 7일 이상 된 캐시 파일 삭제
                    if file_age.days > 7:
                        os.remove(file_path)
                        cleaned_files.append(filename)
                        total_freed_mb += file_size_mb
            
            return {
                'status': 'success',
                'cleaned_files': cleaned_files,
                'freed_mb': round(total_freed_mb, 2),
                'message': f'{len(cleaned_files)}개 캐시 파일 정리, {round(total_freed_mb, 2)}MB 공간 확보'
            }
            
        except Exception as e:
            logger.error(f"캐시 최적화 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def optimize_databases(self) -> Dict[str, Any]:
        """데이터베이스 최적화"""
        try:
            db_files = [
                'marketplace.db',
                'performance_analytics.db',
                'menu_system.db',
                'security_monitor.db',
                'advanced_monitoring.db',
                'alerts.db'
            ]
            
            optimization_results = {}
            total_freed_mb = 0
            
            for db_file in db_files:
                if os.path.exists(db_file):
                    try:
                        # 데이터베이스 백업
                        backup_file = f"{db_file}.backup"
                        shutil.copy2(db_file, backup_file)
                        
                        # 데이터베이스 최적화
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        
                        # VACUUM 실행 (공간 정리)
                        cursor.execute("VACUUM")
                        
                        # 인덱스 재구성
                        cursor.execute("REINDEX")
                        
                        # 분석 정보 업데이트
                        cursor.execute("ANALYZE")
                        
                        conn.commit()
                        conn.close()
                        
                        # 백업 파일 삭제
                        os.remove(backup_file)
                        
                        # 크기 변화 확인
                        original_size = os.path.getsize(backup_file) if os.path.exists(backup_file) else 0
                        optimized_size = os.path.getsize(db_file)
                        freed_mb = (original_size - optimized_size) / (1024 * 1024)
                        total_freed_mb += freed_mb
                        
                        optimization_results[db_file] = {
                            'status': 'success',
                            'freed_mb': round(freed_mb, 2)
                        }
                        
                    except Exception as e:
                        optimization_results[db_file] = {
                            'status': 'error',
                            'error': str(e)
                        }
                else:
                    optimization_results[db_file] = {
                        'status': 'not_found'
                    }
            
            return {
                'status': 'success',
                'databases': optimization_results,
                'total_freed_mb': round(total_freed_mb, 2),
                'message': f'데이터베이스 최적화 완료, {round(total_freed_mb, 2)}MB 공간 확보'
            }
            
        except Exception as e:
            logger.error(f"데이터베이스 최적화 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화"""
        try:
            # 가비지 컬렉션 실행
            collected = gc.collect()
            
            # 메모리 사용량 확인
            memory = psutil.virtual_memory()
            
            # 불필요한 프로세스 확인
            unnecessary_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 5:  # 5% 이상 메모리 사용
                        proc_name = proc.info['name'].lower()
                        if any(keyword in proc_name for keyword in ['python', 'node']):
                            unnecessary_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'memory_percent': proc.info['memory_percent']
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'status': 'success',
                'garbage_collected': collected,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'unnecessary_processes': unnecessary_processes,
                'message': f'메모리 최적화 완료, 가비지 컬렉션: {collected}개 객체'
            }
            
        except Exception as e:
            logger.error(f"메모리 최적화 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """임시 파일 정리"""
        try:
            temp_patterns = [
                '*.tmp',
                '*.temp',
                '*.log',
                '*.cache',
                '__pycache__',
                '*.pyc',
                '*.pyo'
            ]
            
            cleaned_files = []
            total_freed_mb = 0
            
            for root, dirs, files in os.walk('.'):
                # __pycache__ 디렉토리 삭제
                if '__pycache__' in dirs:
                    cache_dir = os.path.join(root, '__pycache__')
                    try:
                        shutil.rmtree(cache_dir)
                        cleaned_files.append(cache_dir)
                        logger.info(f"캐시 디렉토리 삭제: {cache_dir}")
                    except Exception as e:
                        logger.warning(f"캐시 디렉토리 삭제 실패: {cache_dir}, {e}")
                
                # 임시 파일 삭제
                for file in files:
                    if any(file.endswith(pattern.replace('*', '')) for pattern in temp_patterns if '*' in pattern):
                        file_path = os.path.join(root, file)
                        try:
                            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                            os.remove(file_path)
                            cleaned_files.append(file_path)
                            total_freed_mb += file_size_mb
                        except Exception as e:
                            logger.warning(f"임시 파일 삭제 실패: {file_path}, {e}")
            
            return {
                'status': 'success',
                'cleaned_files': cleaned_files,
                'freed_mb': round(total_freed_mb, 2),
                'message': f'{len(cleaned_files)}개 임시 파일 정리, {round(total_freed_mb, 2)}MB 공간 확보'
            }
            
        except Exception as e:
            logger.error(f"임시 파일 정리 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_full_optimization(self) -> Dict[str, Any]:
        """전체 시스템 최적화 실행"""
        logger.info("시스템 전체 최적화 시작")
        
        start_time = datetime.now()
        
        optimization_results = {
            'timestamp': start_time.isoformat(),
            'logs': self.optimize_logs(),
            'cache': self.optimize_cache(),
            'databases': self.optimize_databases(),
            'memory': self.optimize_memory(),
            'temp_files': self.cleanup_temp_files(),
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }
        
        # 전체 결과 요약
        total_freed_mb = (
            optimization_results['logs'].get('freed_mb', 0) +
            optimization_results['cache'].get('freed_mb', 0) +
            optimization_results['databases'].get('total_freed_mb', 0) +
            optimization_results['temp_files'].get('freed_mb', 0)
        )
        
        optimization_results['summary'] = {
            'total_freed_mb': round(total_freed_mb, 2),
            'success_count': sum(1 for result in optimization_results.values() 
                               if isinstance(result, dict) and result.get('status') == 'success'),
            'total_operations': len([k for k in optimization_results.keys() 
                                   if k not in ['timestamp', 'summary', 'duration_seconds']])
        }
        
        # 최적화 이력 저장
        self.optimization_history.append(optimization_results)
        
        # 이력이 너무 많으면 오래된 것 삭제
        if len(self.optimization_history) > 10:
            self.optimization_history = self.optimization_history[-10:]
        
        logger.info(f"시스템 최적화 완료: {total_freed_mb:.2f}MB 공간 확보")
        
        return optimization_results
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """최적화 이력 조회"""
        return self.optimization_history
    
    def save_optimization_report(self, filename: str = None) -> str:
        """최적화 보고서 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'optimization_report_{timestamp}.json'
        
        report_path = os.path.join('logs', filename)
        os.makedirs('logs', exist_ok=True)
        
        latest_result = self.optimization_history[-1] if self.optimization_history else {}
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(latest_result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"최적화 보고서 저장됨: {report_path}")
        return report_path


# 전역 인스턴스
system_optimizer = SystemOptimizer()


def run_quick_optimization():
    """빠른 최적화 실행"""
    try:
        # 가장 중요한 최적화만 실행
        results = {
            'memory': system_optimizer.optimize_memory(),
            'temp_files': system_optimizer.cleanup_temp_files(),
            'timestamp': datetime.now().isoformat()
        }
        
        total_freed_mb = (
            results['memory'].get('freed_mb', 0) +
            results['temp_files'].get('freed_mb', 0)
        )
        
        return {
            'status': 'success',
            'message': f'빠른 최적화 완료, {round(total_freed_mb, 2)}MB 공간 확보',
            'results': results
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': '최적화 중 오류가 발생했습니다.',
            'error': str(e)
        }


if __name__ == "__main__":
    # 전체 최적화 실행
    result = system_optimizer.run_full_optimization()
    print(json.dumps(result, ensure_ascii=False, indent=2)) 