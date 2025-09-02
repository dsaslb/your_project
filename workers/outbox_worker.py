"""
Outbox 워커
- 주기적으로 Outbox 이벤트를 처리하여 SocketIO로 전송
- 운영 환경에서 안정적인 이벤트 전송 보장
"""
import os
import sys
import time
import signal
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app, socketio
from utils.outbox import deliver_pending_events, get_outbox_stats
from models_sync import SyncMetrics
from extensions import db

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OutboxWorker:
    def __init__(self, interval=1.0, batch_size=100):
        """
        Outbox 워커 초기화
        
        Args:
            interval: 처리 간격 (초)
            batch_size: 한 번에 처리할 최대 이벤트 수
        """
        self.interval = interval
        self.batch_size = batch_size
        self.running = False
        self.stats = {
            'processed': 0,
            'delivered': 0,
            'failed': 0,
            'start_time': time.time()
        }
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        logger.info(f"시그널 {signum} 수신, 워커 종료 중...")
        self.running = False
    
    def _record_metrics(self, stats):
        """메트릭 기록"""
        try:
            with app.app_context():
                # 처리 통계 메트릭
                metrics_data = [
                    ('outbox_processed_total', stats['processed']),
                    ('outbox_delivered_total', stats['delivered']),
                    ('outbox_failed_total', stats['failed']),
                    ('outbox_processing_rate', stats['processed'] / (time.time() - self.stats['start_time']))
                ]
                
                for metric_name, metric_value in metrics_data:
                    metric = SyncMetrics(
                        metric_name=metric_name,
                        metric_value=metric_value,
                        labels={'worker': 'outbox'}
                    )
                    db.session.add(metric)
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"메트릭 기록 실패: {e}")
    
    def _cleanup_old_metrics(self):
        """오래된 메트릭 정리"""
        try:
            with app.app_context():
                from datetime import datetime, timedelta
                
                # 7일 이상 된 메트릭 삭제
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                deleted_count = SyncMetrics.query.filter(
                    SyncMetrics.timestamp < cutoff_date
                ).delete()
                
                if deleted_count > 0:
                    db.session.commit()
                    logger.info(f"오래된 메트릭 {deleted_count}개 정리 완료")
                    
        except Exception as e:
            logger.error(f"메트릭 정리 실패: {e}")
    
    def run(self):
        """워커 실행"""
        logger.info("🚀 Outbox 워커 시작")
        logger.info(f"📊 설정: 간격={self.interval}초, 배치크기={self.batch_size}")
        
        self.running = True
        last_cleanup = time.time()
        
        while self.running:
            try:
                start_time = time.time()
                
                with app.app_context():
                    # Outbox 이벤트 처리
                    result = deliver_pending_events(
                        limit=self.batch_size,
                        retry_failed=True
                    )
                    
                    # 통계 업데이트
                    self.stats['processed'] += result['processed']
                    self.stats['delivered'] += result['delivered']
                    self.stats['failed'] += result['failed']
                    
                    # 처리 결과 로깅
                    if result['processed'] > 0:
                        logger.info(f"📦 이벤트 처리: {result}")
                    
                    # Outbox 상태 확인
                    outbox_stats = get_outbox_stats()
                    if outbox_stats['pending'] > 50:
                        logger.warning(f"⚠️ 대기 중인 이벤트 많음: {outbox_stats['pending']}개")
                
                # 메트릭 기록 (5분마다)
                if time.time() - last_cleanup > 300:
                    self._record_metrics(self.stats)
                    self._cleanup_old_metrics()
                    last_cleanup = time.time()
                
                # 다음 처리까지 대기
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"워커 실행 중 오류: {e}")
                time.sleep(self.interval)
        
        logger.info("🛑 Outbox 워커 종료")
        logger.info(f"📊 최종 통계: {self.stats}")

def main():
    """메인 실행 함수"""
    # 환경 변수에서 설정 읽기
    interval = float(os.getenv('OUTBOX_INTERVAL', '1.0'))
    batch_size = int(os.getenv('OUTBOX_BATCH_SIZE', '100'))
    
    # 워커 생성 및 실행
    worker = OutboxWorker(interval=interval, batch_size=batch_size)
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"워커 실행 실패: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())