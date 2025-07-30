# -*- coding: utf-8 -*-
"""
자동화된 시스템 유지보수 스크립트
정기적인 시스템 점검, 최적화, 백업을 자동으로 수행
"""

import os
import json
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import shutil
import zipfile

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_maintenance.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomatedMaintenance:
    """자동화된 유지보수 클래스"""
    
    def __init__(self):
        self.maintenance_config = {
            'health_check_interval': 30,  # 30분마다 상태 점검
            'optimization_interval': 1440,  # 24시간마다 최적화
            'backup_interval': 10080,  # 7일마다 백업
            'log_cleanup_interval': 10080,  # 7일마다 로그 정리
            'max_backup_count': 10,  # 최대 백업 개수
            'backup_retention_days': 30,  # 백업 보관 기간
        }
        self.maintenance_history = []
        self.is_running = False
        self.maintenance_thread = None
        
    def create_backup(self) -> Dict[str, Any]:
        """시스템 백업 생성"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = 'backups'
            backup_name = f'system_backup_{timestamp}'
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 백업 디렉토리 생성
            os.makedirs(backup_path, exist_ok=True)
            
            # 백업할 파일/디렉토리 목록
            backup_items = [
                'marketplace.db',
                'performance_analytics.db',
                'menu_system.db',
                'security_monitor.db',
                'advanced_monitoring.db',
                'alerts.db',
                'config',
                'templates',
                'static',
                'logs'
            ]
            
            backed_up_items = []
            total_size = 0
            
            for item in backup_items:
                if os.path.exists(item):
                    item_backup_path = os.path.join(backup_path, item)
                    if os.path.isfile(item):
                        shutil.copy2(item, item_backup_path)
                        size = os.path.getsize(item_backup_path)
                    else:
                        shutil.copytree(item, item_backup_path)
                        size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                 for dirpath, dirnames, filenames in os.walk(item_backup_path)
                                 for filename in filenames)
                    
                    backed_up_items.append(item)
                    total_size += size
            
            # 백업 정보 저장
            backup_info = {
                'timestamp': timestamp,
                'backup_path': backup_path,
                'items': backed_up_items,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'status': 'success'
            }
            
            # 백업 정보 파일 저장
            info_file = os.path.join(backup_path, 'backup_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            # 압축 파일 생성
            zip_path = f"{backup_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_path)
                        zipf.write(file_path, arcname)
            
            # 원본 백업 디렉토리 삭제
            shutil.rmtree(backup_path)
            
            # 오래된 백업 정리
            self.cleanup_old_backups()
            
            logger.info(f"백업 생성 완료: {zip_path} ({backup_info['total_size_mb']}MB)")
            
            return {
                'status': 'success',
                'backup_path': zip_path,
                'total_size_mb': backup_info['total_size_mb'],
                'items_count': len(backed_up_items),
                'message': f'백업 생성 완료: {backup_info["total_size_mb"]}MB'
            }
            
        except Exception as e:
            logger.error(f"백업 생성 오류: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': '백업 생성 중 오류가 발생했습니다.'
            }
    
    def cleanup_old_backups(self):
        """오래된 백업 파일 정리"""
        try:
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                return
            
            # 백업 파일 목록 조회
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.zip') and filename.startswith('system_backup_'):
                    file_path = os.path.join(backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append((file_path, file_time))
            
            # 날짜순 정렬
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 최대 개수 초과 시 오래된 것 삭제
            if len(backup_files) > self.maintenance_config['max_backup_count']:
                files_to_delete = backup_files[self.maintenance_config['max_backup_count']:]
                for file_path, file_time in files_to_delete:
                    os.remove(file_path)
                    logger.info(f"오래된 백업 파일 삭제: {file_path}")
            
            # 보관 기간 초과 시 삭제
            cutoff_date = datetime.now() - timedelta(days=self.maintenance_config['backup_retention_days'])
            for file_path, file_time in backup_files:
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"보관 기간 초과 백업 파일 삭제: {file_path}")
                    
        except Exception as e:
            logger.error(f"백업 정리 오류: {e}")
    
    def cleanup_logs(self) -> Dict[str, Any]:
        """로그 파일 정리"""
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                return {'status': 'no_logs', 'message': '로그 디렉토리가 없습니다.'}
            
            cleaned_files = []
            total_freed_mb = 0
            
            # 30일 이상 된 로그 파일 삭제
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for filename in os.listdir(log_dir):
                file_path = os.path.join(log_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        os.remove(file_path)
                        cleaned_files.append(filename)
                        total_freed_mb += file_size_mb
            
            return {
                'status': 'success',
                'cleaned_files': cleaned_files,
                'freed_mb': round(total_freed_mb, 2),
                'message': f'{len(cleaned_files)}개 로그 파일 정리, {round(total_freed_mb, 2)}MB 공간 확보'
            }
            
        except Exception as e:
            logger.error(f"로그 정리 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_health_check(self) -> Dict[str, Any]:
        """상태 점검 실행"""
        try:
            from utils.system_health_checker import run_quick_health_check
            result = run_quick_health_check()
            
            if result['status'] == 'healthy':
                logger.info("상태 점검: 정상")
            else:
                logger.warning(f"상태 점검: 문제 발견 - {result.get('error', '알 수 없는 오류')}")
            
            return result
            
        except Exception as e:
            logger.error(f"상태 점검 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_optimization(self) -> Dict[str, Any]:
        """최적화 실행"""
        try:
            from scripts.system_optimizer import run_quick_optimization
            result = run_quick_optimization()
            
            if result['status'] == 'success':
                logger.info(f"최적화 완료: {result['message']}")
            else:
                logger.warning(f"최적화 실패: {result.get('error', '알 수 없는 오류')}")
            
            return result
            
        except Exception as e:
            logger.error(f"최적화 오류: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_maintenance_cycle(self):
        """유지보수 사이클 실행"""
        try:
            logger.info("자동화된 유지보수 사이클 시작")
            
            maintenance_result = {
                'timestamp': datetime.now().isoformat(),
                'health_check': self.run_health_check(),
                'optimization': self.run_optimization(),
                'log_cleanup': self.cleanup_logs()
            }
            
            # 백업은 주기적으로만 실행
            current_time = datetime.now()
            if not hasattr(self, 'last_backup_time') or \
               (current_time - self.last_backup_time).total_seconds() > self.maintenance_config['backup_interval'] * 60:
                maintenance_result['backup'] = self.create_backup()
                self.last_backup_time = current_time
            
            # 유지보수 이력 저장
            self.maintenance_history.append(maintenance_result)
            
            # 이력이 너무 많으면 오래된 것 삭제
            if len(self.maintenance_history) > 100:
                self.maintenance_history = self.maintenance_history[-100:]
            
            logger.info("자동화된 유지보수 사이클 완료")
            
        except Exception as e:
            logger.error(f"유지보수 사이클 오류: {e}")
    
    def start_automated_maintenance(self):
        """자동화된 유지보수 시작"""
        if self.is_running:
            logger.warning("자동화된 유지보수가 이미 실행 중입니다.")
            return
        
        self.is_running = True
        
        # 스케줄 설정
        schedule.every(self.maintenance_config['health_check_interval']).minutes.do(self.run_maintenance_cycle)
        
        def maintenance_loop():
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # 1분마다 스케줄 확인
                except Exception as e:
                    logger.error(f"유지보수 루프 오류: {e}")
                    time.sleep(60)
        
        self.maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        self.maintenance_thread.start()
        
        logger.info("자동화된 유지보수가 시작되었습니다.")
    
    def stop_automated_maintenance(self):
        """자동화된 유지보수 중지"""
        if not self.is_running:
            logger.warning("자동화된 유지보수가 실행 중이 아닙니다.")
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.maintenance_thread:
            self.maintenance_thread.join(timeout=10)
        
        logger.info("자동화된 유지보수가 중지되었습니다.")
    
    def get_maintenance_status(self) -> Dict[str, Any]:
        """유지보수 상태 조회"""
        return {
            'is_running': self.is_running,
            'config': self.maintenance_config,
            'history_count': len(self.maintenance_history),
            'last_maintenance': self.maintenance_history[-1] if self.maintenance_history else None
        }
    
    def save_maintenance_report(self, filename: str = None) -> str:
        """유지보수 보고서 저장"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'maintenance_report_{timestamp}.json'
        
        report_path = os.path.join('logs', filename)
        os.makedirs('logs', exist_ok=True)
        
        report_data = {
            'status': self.get_maintenance_status(),
            'history': self.maintenance_history[-10:] if self.maintenance_history else []  # 최근 10개만
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"유지보수 보고서 저장됨: {report_path}")
        return report_path


# 전역 인스턴스
automated_maintenance = AutomatedMaintenance()


def start_maintenance():
    """유지보수 시작"""
    automated_maintenance.start_automated_maintenance()


def stop_maintenance():
    """유지보수 중지"""
    automated_maintenance.stop_automated_maintenance()


def run_manual_maintenance():
    """수동 유지보수 실행"""
    return automated_maintenance.run_maintenance_cycle()


if __name__ == "__main__":
    # 수동 유지보수 실행
    result = run_manual_maintenance()
    print(json.dumps(result, ensure_ascii=False, indent=2)) 