"""
비동기 작업 큐 시스템
Celery, Redis, 작업 스케줄링
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable
from celery import Celery, Task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import redis
from datetime import datetime, timedelta
import os
import glob
from scripts.security_scan import main as security_scan_main
import smtplib
from email.mime.text import MIMEText
import requests

logger = logging.getLogger(__name__)

class AsyncQueueManager:
    """비동기 작업 큐 관리자"""
    
    def __init__(self, broker_url: str, result_backend: str):
        self.broker_url = broker_url
        self.result_backend = result_backend
        self.celery_app = Celery(
            'your_program',
            broker=broker_url,
            backend=result_backend,
            include=['utils.async_queue']
        )
        
        # Celery 설정
        self.celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='Asia/Seoul',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=30 * 60,  # 30분
            task_soft_time_limit=25 * 60,  # 25분
            worker_prefetch_multiplier=1,
            worker_max_tasks_per_child=1000,
            result_expires=3600,  # 1시간
            task_ignore_result=False,
            task_store_errors_even_if_ignored=True
        )
        
        # 스케줄된 작업 설정
        self.celery_app.conf.beat_schedule = {
            'daily-backup': {
                'task': 'utils.async_queue.daily_backup',
                'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
            },
            'cleanup-logs': {
                'task': 'utils.async_queue.cleanup_logs',
                'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
            },
            'optimize-database': {
                'task': 'utils.async_queue.optimize_database',
                'schedule': crontab(hour=4, minute=0),  # 매일 새벽 4시
            },
            'generate-reports': {
                'task': 'utils.async_queue.generate_reports',
                'schedule': crontab(hour=8, minute=0),  # 매일 오전 8시
            },
            'monitor-system': {
                'task': 'utils.async_queue.monitor_system',
                'schedule': crontab(minute='*/5'),  # 5분마다
            },
            'cache-optimization': {
                'task': 'utils.async_queue.optimize_cache',
                'schedule': crontab(minute='*/30'),  # 30분마다
            }
        }
    
    def get_celery_app(self) -> Celery:
        """Celery 앱 반환"""
        return self.celery_app

class BaseTask(Task):
    """기본 작업 클래스"""
    
    abstract = True
    
    def on_success(self, retval, task_id, args, kwargs):
        """작업 성공 시 호출"""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """작업 실패 시 호출"""
        logger.error(f"Task {task_id} failed: {exc}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """작업 재시도 시 호출"""
        logger.warning(f"Task {task_id} retrying: {exc}")

# Celery 앱 인스턴스
celery_app = None

def init_celery_app(broker_url: str, result_backend: str):
    """Celery 앱 초기화"""
    global celery_app
    queue_manager = AsyncQueueManager(broker_url, result_backend)
    celery_app = queue_manager.get_celery_app()
    logger.info("Celery 앱 초기화 완료")

def get_celery_app() -> Optional[Celery]:
    """Celery 앱 반환"""
    return celery_app

# 비동기 작업들
@celery_app.task(base=BaseTask, bind=True)
def daily_backup(self):
    """일일 백업 작업"""
    try:
        logger.info("일일 백업 작업 시작")
        
        # 백업 스크립트 실행
        from scripts.backup import backup_full
        result = backup_full()
        
        logger.info("일일 백업 작업 완료")
        return result
        
    except Exception as e:
        logger.error(f"일일 백업 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def cleanup_logs(self):
    """로그 정리 작업"""
    try:
        logger.info("로그 정리 작업 시작")
        
        # 30일 이상 된 로그 파일 삭제
        import os
        import glob
        from datetime import datetime, timedelta
        
        log_dir = "logs"
        cutoff_date = datetime.now() - timedelta(days=30)
        
        deleted_count = 0
        for log_file in glob.glob(f"{log_dir}/*.log.*"):
            file_time = datetime.fromtimestamp(os.path.getctime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                deleted_count += 1
        
        logger.info(f"로그 정리 작업 완료: {deleted_count}개 파일 삭제")
        return {'deleted_files': deleted_count}
        
    except Exception as e:
        logger.error(f"로그 정리 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def optimize_database(self):
    """데이터베이스 최적화 작업"""
    try:
        logger.info("데이터베이스 최적화 작업 시작")
        
        from utils.database_optimizer import get_database_optimizer
        
        db_optimizer = get_database_optimizer()
        if db_optimizer:
            # 주요 테이블 최적화
            main_tables = ['users', 'brands', 'branches', 'employees', 'attendance_records']
            results = {}
            
            for table in main_tables:
                try:
                    result = db_optimizer.optimize_table(table)
                    results[table] = result
                except Exception as e:
                    logger.warning(f"테이블 {table} 최적화 실패: {e}")
            
            logger.info("데이터베이스 최적화 작업 완료")
            return results
        
    except Exception as e:
        logger.error(f"데이터베이스 최적화 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def generate_reports(self):
    """리포트 생성 작업"""
    try:
        logger.info("리포트 생성 작업 시작")
        
        from scripts.operations import generate_report
        result = generate_report()
        
        logger.info("리포트 생성 작업 완료")
        return result
        
    except Exception as e:
        logger.error(f"리포트 생성 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def monitor_system(self):
    """시스템 모니터링 작업"""
    try:
        logger.info("시스템 모니터링 작업 시작")
        
        from scripts.operations import monitor_all
        result = monitor_all()
        
        logger.info("시스템 모니터링 작업 완료")
        return result
        
    except Exception as e:
        logger.error(f"시스템 모니터링 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def optimize_cache(self):
    """캐시 최적화 작업"""
    try:
        logger.info("캐시 최적화 작업 시작")
        
        from utils.cache_optimizer import get_cache_manager
        
        cache_manager = get_cache_manager()
        if cache_manager:
            result = cache_manager.optimize_memory()
            
            logger.info("캐시 최적화 작업 완료")
            return result
        
    except Exception as e:
        logger.error(f"캐시 최적화 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def send_notification(self, user_id: int, message: str, notification_type: str = 'email'):
    """알림 전송 작업"""
    try:
        logger.info(f"알림 전송 작업 시작: user_id={user_id}, type={notification_type}")
        
        # 알림 전송 로직
        if notification_type == 'email':
            # 이메일 전송
            pass
        elif notification_type == 'sms':
            # SMS 전송
            pass
        elif notification_type == 'push':
            # 푸시 알림
            pass
        
        logger.info(f"알림 전송 작업 완료: user_id={user_id}")
        return {'status': 'sent', 'user_id': user_id, 'type': notification_type}
        
    except Exception as e:
        logger.error(f"알림 전송 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def process_data_export(self, user_id: int, export_type: str, filters: Dict):
    """데이터 내보내기 작업"""
    try:
        logger.info(f"데이터 내보내기 작업 시작: user_id={user_id}, type={export_type}")
        
        # 데이터 내보내기 로직
        if export_type == 'attendance':
            # 출근 기록 내보내기
            pass
        elif export_type == 'reports':
            # 리포트 내보내기
            pass
        elif export_type == 'analytics':
            # 분석 데이터 내보내기
            pass
        
        logger.info(f"데이터 내보내기 작업 완료: user_id={user_id}")
        return {'status': 'completed', 'user_id': user_id, 'type': export_type}
        
    except Exception as e:
        logger.error(f"데이터 내보내기 작업 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def sync_external_data(self, sync_type: str, last_sync_time: str = None):
    """외부 데이터 동기화 작업"""
    try:
        logger.info(f"외부 데이터 동기화 작업 시작: type={sync_type}")
        
        # 외부 데이터 동기화 로직
        if sync_type == 'weather':
            # 날씨 데이터 동기화
            pass
        elif sync_type == 'holidays':
            # 공휴일 데이터 동기화
            pass
        elif sync_type == 'exchange_rates':
            # 환율 데이터 동기화
            pass
        
        logger.info(f"외부 데이터 동기화 작업 완료: type={sync_type}")
        return {'status': 'synced', 'type': sync_type}
        
    except Exception as e:
        logger.error(f"외부 데이터 동기화 작업 실패: {e}")
        raise

class TaskScheduler:
    """작업 스케줄러"""
    
    def __init__(self, celery_app: Celery):
        self.celery_app = celery_app
    
    def schedule_task(self, task_name: str, args: List = None, kwargs: Dict = None, 
                     countdown: int = None, eta: datetime = None, 
                     expires: int = None) -> str:
        """작업 스케줄링"""
        try:
            task = self.celery_app.send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {},
                countdown=countdown,
                eta=eta,
                expires=expires
            )
            
            logger.info(f"작업 스케줄링 완료: {task_name}, task_id={task.id}")
            return task.id
            
        except Exception as e:
            logger.error(f"작업 스케줄링 실패: {e}")
            raise
    
    def schedule_periodic_task(self, task_name: str, schedule: crontab, 
                             args: List = None, kwargs: Dict = None):
        """주기적 작업 스케줄링"""
        try:
            self.celery_app.conf.beat_schedule[f'periodic-{task_name}'] = {
                'task': task_name,
                'schedule': schedule,
                'args': args or [],
                'kwargs': kwargs or {}
            }
            
            logger.info(f"주기적 작업 스케줄링 완료: {task_name}")
            
        except Exception as e:
            logger.error(f"주기적 작업 스케줄링 실패: {e}")
            raise
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        try:
            self.celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"작업 취소 완료: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"작업 취소 실패: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Dict:
        """작업 상태 조회"""
        try:
            task_result = self.celery_app.AsyncResult(task_id)
            
            return {
                'task_id': task_id,
                'status': task_result.status,
                'result': task_result.result,
                'info': task_result.info
            }
            
        except Exception as e:
            logger.error(f"작업 상태 조회 실패: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_active_tasks(self) -> List[Dict]:
        """활성 작업 목록 조회"""
        try:
            active_tasks = self.celery_app.control.inspect().active()
            
            tasks = []
            for worker, worker_tasks in active_tasks.items():
                for task in worker_tasks:
                    tasks.append({
                        'worker': worker,
                        'task_id': task['id'],
                        'task_name': task['name'],
                        'args': task['args'],
                        'kwargs': task['kwargs'],
                        'time_start': task['time_start']
                    })
            
            return tasks
            
        except Exception as e:
            logger.error(f"활성 작업 목록 조회 실패: {e}")
            return []
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """예약된 작업 목록 조회"""
        try:
            scheduled_tasks = self.celery_app.control.inspect().scheduled()
            
            tasks = []
            for worker, worker_tasks in scheduled_tasks.items():
                for task in worker_tasks:
                    tasks.append({
                        'worker': worker,
                        'task_id': task['request']['id'],
                        'task_name': task['request']['name'],
                        'eta': task['eta'],
                        'priority': task['priority']
                    })
            
            return tasks
            
        except Exception as e:
            logger.error(f"예약된 작업 목록 조회 실패: {e}")
            return []

# 전역 작업 스케줄러 인스턴스
task_scheduler = None

def init_task_scheduler(celery_app: Celery):
    """작업 스케줄러 초기화"""
    global task_scheduler
    task_scheduler = TaskScheduler(celery_app)
    logger.info("작업 스케줄러 초기화 완료")

def get_task_scheduler() -> Optional[TaskScheduler]:
    """작업 스케줄러 반환"""
    return task_scheduler 

# 정기 리포트/알림 작업 추가
@celery_app.task(base=BaseTask, bind=True)
def send_ops_report(self):
    """운영 리포트 이메일/슬랙 발송"""
    try:
        logger.info("운영 리포트 발송 작업 시작")
        # 예시: 최근 상태/로그/알림 요약
        from api.admin_ops_api import get_status, get_logs, get_alerts
        status = get_status().json
        logs = get_logs().json
        alerts = get_alerts().json
        report = f"[운영 리포트]\n\n상태:\n{status.get('output','')}\n\n최근 로그:\n{''.join(logs.get('logs', []))}\n\n최근 알림:\n{''.join(alerts.get('alerts', []))}"
        # 이메일 발송
        send_email("운영 리포트", report)
        # 슬랙 발송
        send_slack("운영 리포트", report)
        logger.info("운영 리포트 발송 완료")
        return True
    except Exception as e:
        logger.error(f"운영 리포트 발송 실패: {e}")
        raise

@celery_app.task(base=BaseTask, bind=True)
def send_security_report(self):
    """보안 점검 리포트 이메일/슬랙 발송"""
    try:
        logger.info("보안 점검 리포트 발송 작업 시작")
        # 보안 점검 실행 및 리포트 요약
        security_scan_main(['scan'])
        with open('logs/security_scan.log', 'r', encoding='utf-8') as f:
            log_lines = f.readlines()[-30:]
        report = '[보안 점검 리포트]\n' + ''.join(log_lines)
        send_email("보안 점검 리포트", report)
        send_slack("보안 점검 리포트", report)
        logger.info("보안 점검 리포트 발송 완료")
        return True
    except Exception as e:
        logger.error(f"보안 점검 리포트 발송 실패: {e}")
        raise

def send_email(subject: str, message: str):
    try:
        smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('EMAIL_PORT', 587))
        smtp_user = os.getenv('EMAIL_USERNAME')
        smtp_pass = os.getenv('EMAIL_PASSWORD')
        to_addr = os.getenv('ALERT_EMAIL', 'admin@yourprogram.com')
        if not smtp_user or not smtp_pass:
            logger.warning("이메일 환경변수 미설정, 이메일 발송 생략")
            return
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_addr
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_addr], msg.as_string())
        logger.info("이메일 발송 완료")
    except Exception as e:
        logger.error(f"이메일 발송 실패: {e}")

def send_slack(subject: str, message: str):
    try:
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            logger.warning("슬랙 웹훅 미설정, 슬랙 발송 생략")
            return
        payload = {"text": f"[{subject}]\n{message}"}
        requests.post(webhook_url, json=payload, timeout=5)
        logger.info("슬랙 발송 완료")
    except Exception as e:
        logger.error(f"슬랙 발송 실패: {e}")

# Celery beat 스케줄에 정기 리포트/알림 작업 추가
celery_app.conf.beat_schedule.update({
    'send-ops-report': {
        'task': 'utils.async_queue.send_ops_report',
        'schedule': crontab(hour=9, minute=0),  # 매일 오전 9시
    },
    'send-security-report': {
        'task': 'utils.async_queue.send_security_report',
        'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
    },
}) 

@celery_app.task(base=BaseTask, bind=True)
def handle_event_auto_action(self, event_type: str, details: dict):
    """이벤트 기반 자동화: 장애/성능/보안 이벤트 발생 시 자동 롤백/스케일업/알림"""
    try:
        logger.info(f"이벤트 자동화 트리거: {event_type}, details={details}")
        if event_type == 'failure':
            # 장애 발생: 자동 롤백/재시작
            import subprocess
            subprocess.call(['bash', './scripts/auto_recover.sh', 'recover'])
            send_email("[장애 자동 복구]", f"장애 발생: {details}\n자동 복구/롤백이 실행되었습니다.")
            send_slack("[장애 자동 복구]", f"장애 발생: {details}\n자동 복구/롤백이 실행되었습니다.")
        elif event_type == 'performance':
            # 성능 임계치 초과: 자동 스케일업
            # (실제 스케일업 로직은 인프라에 맞게 구현)
            logger.info("성능 임계치 초과: 스케일업 트리거")
            send_email("[성능 자동 스케일업]", f"성능 임계치 초과: {details}\n스케일업이 트리거되었습니다.")
            send_slack("[성능 자동 스케일업]", f"성능 임계치 초과: {details}\n스케일업이 트리거되었습니다.")
        elif event_type == 'security':
            # 보안 이슈: 즉시 관리자/운영자 알림
            send_email("[보안 경고]", f"보안 이슈 감지: {details}")
            send_slack("[보안 경고]", f"보안 이슈 감지: {details}")
        else:
            logger.warning(f"알 수 없는 이벤트 타입: {event_type}")
        return {'status': 'ok'}
    except Exception as e:
        logger.error(f"이벤트 자동화 실패: {e}")
        return {'status': 'fail', 'error': str(e)} 