import requests
import time
import logging
from datetime import datetime

logging.basicConfig(filename='reward_scheduler.log', level=logging.INFO)

API_BASE = 'http://localhost:5000/api/reward'

while True:
    try:
        # 포인트/리워드 지급
        reward_res = requests.post(f'{API_BASE}/reward', json={"user_id": 1, "amount": 1000}).json()
        logging.info(f"[{datetime.now()}] 리워드 지급: {reward_res}")
        # 이벤트/쿠폰 발급
        event_res = requests.post(f'{API_BASE}/event', json={"event": "웰컴쿠폰"}).json()
        logging.info(f"[{datetime.now()}] 이벤트/쿠폰 발급: {event_res}")
    except Exception as e:
        logging.error(f"[{datetime.now()}] 복지/리워드 자동화 오류: {str(e)}")
    time.sleep(3600)  # 1시간마다 실행 