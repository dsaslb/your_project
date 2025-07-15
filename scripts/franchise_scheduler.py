import requests
import time
import logging
from datetime import datetime

logging.basicConfig(filename='franchise_scheduler.log', level=logging.INFO)

API_BASE = 'http://localhost:5000/api/franchise'

while True:
    try:
        # 정책 일괄 적용
        res = requests.post(f'{API_BASE}/apply_policy', json={"policy": "매출 급감 경보"}).json()
        logging.info(f"[{datetime.now()}] 정책 일괄 적용: {res}")
    except Exception as e:
        logging.error(f"[{datetime.now()}] 프랜차이즈 자동화 오류: {str(e)}")
    time.sleep(3600)  # 1시간마다 실행 