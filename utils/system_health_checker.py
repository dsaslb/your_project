# -*- coding: utf-8 -*-
"""
시스템 전체 상태 점검 도구
백엔드, 프론트엔드, 데이터베이스, 플러그인 등 모든 구성 요소의 상태를 확인
"""

import requests
import psutil
import sqlite3
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SystemHealthChecker:
    """시스템 전체 상태 점검 클래스"""
    
    def __init__(self):
        self.health_status = {}
        self.last_check = None
        self.check_interval = 300  # 5분마다 체크
        
    def check_backend_health(self) -> Dict[str, Any]:
        """백엔드 서버 상태 확인"""
        try:
            start_time = time.time()
            response = requests.get('http://localhost:5000/health', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'response_time': round(response_time, 3),
                    'timestamp': data.get('timestamp'),
                    'version': data.get('version')
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': round(response_time, 3),
                    'error': f'HTTP {response.status_code}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_frontend_health(self) -> Dict[str, Any]:
        """프론트엔드 서버 상태 확인"""
        try:
            start_time = time.time()
            response = requests.get('http://localhost:3000', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': round(response_time, 3)
                }
            else:
                return {
                    'status': 'unhealthy',
                    'response_time': round(response_time, 3),
                    'error': f'HTTP {response.status_code}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_database_health(self) -> Dict[str, Any]:
        """데이터베이스 상태 확인"""
        try:
            # SQLite 데이터베이스 파일들 확인
            db_files = [
                'marketplace.db',
                'performance_analytics.db',
                'menu_system.db',
                'security_monitor.db',
                'advanced_monitoring.db',
                'alerts.db'
            ]
            
            db_status = {}
            total_size = 0
            
            for db_file in db_files:
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    total_size += size
                    
                    # 데이터베이스 연결 테스트
                    try:
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        table_count = cursor.fetchone()[0]
                        conn.close()
                        
                        db_status[db_file] = {
                            'status': 'healthy',
                            'size_mb': round(size / (1024 * 1024), 2),
                            'table_count': table_count
                        }
                    except Exception as e:
                        db_status[db_file] = {
                            'status': 'unhealthy',
                            'size_mb': round(size / (1024 * 1024), 2),
                            'error': str(e)
                        }
                else:
                    db_status[db_file] = {
                        'status': 'not_found'
                    }
            
            return {
                'status': 'healthy' if all(db.get('status') == 'healthy' for db in db_status.values() if db.get('status') != 'not_found') else 'warning',
                'databases': db_status,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 상태 확인"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 프로세스 확인
            python_processes = []
            node_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                    elif 'node' in proc.info['name'].lower():
                        node_processes.append({
                            'pid': proc.info['pid'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'python_processes': python_processes,
                'node_processes': node_processes
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_plugin_health(self) -> Dict[str, Any]:
        """플러그인 시스템 상태 확인"""
        try:
            plugin_dir = 'plugins'
            if not os.path.exists(plugin_dir):
                return {
                    'status': 'not_found',
                    'error': '플러그인 디렉토리가 존재하지 않습니다.'
                }
            
            plugins = []
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                if os.path.isdir(item_path):
                    # 플러그인 설정 파일 확인
                    config_file = os.path.join(item_path, 'config.json')
                    if os.path.exists(config_file):
                        try:
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            plugins.append({
                                'name': item,
                                'status': 'configured',
                                'config': config
                            })
                        except Exception as e:
                            plugins.append({
                                'name': item,
                                'status': 'config_error',
                                'error': str(e)
                            })
                    else:
                        plugins.append({
                            'name': item,
                            'status': 'no_config'
                        })
            
            return {
                'status': 'healthy',
                'plugin_count': len(plugins),
                'plugins': plugins
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def run_full_health_check(self) -> Dict[str, Any]:
        """전체 시스템 상태 점검 실행"""
        logger.info("시스템 전체 상태 점검 시작")
        
        start_time = time.time()
        
        health_check = {
            'timestamp': datetime.now().isoformat(),
            'backend': self.check_backend_health(),
            'frontend': self.check_frontend_health(),
            'database': self.check_database_health(),
            'system_resources': self.check_system_resources(),
            'plugins': self.check_plugin_health(),
            'check_duration': round(time.time() - start_time, 3)
        }
        
        # 전체 상태 평가
        all_statuses = [
            health_check['backend']['status'],
            health_check['frontend']['status'],
            health_check['database']['status'],
            health_check['system_resources']['status'],
            health_check['plugins']['status']
        ]
        
        if all(status == 'healthy' for status in all_statuses):
            health_check['overall_status'] = 'healthy'
        elif any(status == 'unhealthy' for status in all_statuses):
            health_check['overall_status'] = 'unhealthy'
        else:
            health_check['overall_status'] = 'warning'
        
        self.health_status = health_check
        self.last_check = datetime.now()
        
        logger.info(f"시스템 상태 점검 완료: {health_check['overall_status']}")
        
        return health_check
    
    def get_health_summary(self) -> Dict[str, Any]:
        """상태 요약 정보 반환"""
        if not self.health_status:
            return {'status': 'no_data'}
        
        return {
            'overall_status': self.health_status.get('overall_status'),
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'check_duration': self.health_status.get('check_duration'),
            'components': {
                'backend': self.health_status['backend']['status'],
                'frontend': self.health_status['frontend']['status'],
                'database': self.health_status['database']['status'],
                'system_resources': self.health_status['system_resources']['status'],
                'plugins': self.health_status['plugins']['status']
            }
        }
    
    def save_health_report(self, filename: str = None) -> str:
        """상태 보고서를 파일로 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'health_report_{timestamp}.json'
        
        report_path = os.path.join('logs', filename)
        os.makedirs('logs', exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.health_status, f, ensure_ascii=False, indent=2)
        
        logger.info(f"상태 보고서 저장됨: {report_path}")
        return report_path


# 전역 인스턴스
health_checker = SystemHealthChecker()


def run_quick_health_check():
    """빠른 상태 점검 실행"""
    try:
        # 백엔드만 빠르게 확인
        backend_status = health_checker.check_backend_health()
        if backend_status['status'] == 'healthy':
            return {
                'status': 'healthy',
                'message': '시스템이 정상 작동 중입니다.',
                'backend_response_time': backend_status.get('response_time', 0)
            }
        else:
            return {
                'status': 'unhealthy',
                'message': '백엔드 서버에 문제가 있습니다.',
                'error': backend_status.get('error', '알 수 없는 오류')
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': '상태 점검 중 오류가 발생했습니다.',
            'error': str(e)
        }


if __name__ == "__main__":
    # 전체 상태 점검 실행
    result = health_checker.run_full_health_check()
    print(json.dumps(result, ensure_ascii=False, indent=2)) 