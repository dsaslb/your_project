import time
from utils.system_monitor import SystemMonitor
import random

monitor = SystemMonitor()

while True:
    try:
        # 이벤트 감지(더미)
        event = f"정상 이벤트-{random.randint(1,100)}"
        monitor.log_event(event)
        # 장애 감지(더미)
        if random.random() < 0.1:
            error = f"장애 발생-{random.randint(1,100)}"
            monitor.log_error(error)
    except Exception as e:
        monitor.log_error(f"시스템 모니터 스케줄러 오류: {str(e)}")
    time.sleep(600)  # 10분마다 실행 