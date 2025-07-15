import logging
from datetime import datetime

logging.basicConfig(filename='system_monitor.log', level=logging.INFO)

class SystemMonitor:
    def __init__(self):
        self.error_history = []
        self.event_history = []

    def log_event(self, event):
        entry = {'type': 'event', 'event': event, 'timestamp': datetime.now()}
        self.event_history.append(entry)
        logging.info(f"EVENT: {event} at {entry['timestamp']}")

    def log_error(self, error):
        entry = {'type': 'error', 'error': error, 'timestamp': datetime.now()}
        self.error_history.append(entry)
        logging.error(f"ERROR: {error} at {entry['timestamp']}")
        self.send_alert(error)

    def send_alert(self, message):
        # 실제 구현 시 이메일/슬랙 등 알림 연동
        logging.warning(f"ALERT: {message} (관리자에게 알림)")

    def get_error_history(self):
        return self.error_history

    def get_event_history(self):
        return self.event_history 