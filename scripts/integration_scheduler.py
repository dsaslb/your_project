import requests
import time
import logging
from datetime import datetime

logging.basicConfig(filename='integration_scheduler.log', level=logging.INFO)

API_BASE = 'http://localhost:5000/api/integration'

while True:
    try:
        # 1. POS 연동
        pos_res = requests.post(f'{API_BASE}/pos', json={"data": "sample"}).json()
        logging.info(f"[{datetime.now()}] POS: {pos_res}")
        # 2. 회계 연동
        acc_res = requests.post(f'{API_BASE}/accounting', json={"data": "sample"}).json()
        logging.info(f"[{datetime.now()}] Accounting: {acc_res}")
        # 3. 리뷰 연동/감성분석
        rev_res = requests.post(f'{API_BASE}/review', json={"data": "sample"}).json()
        logging.info(f"[{datetime.now()}] Review: {rev_res}")
    except Exception as e:
        logging.error(f"[{datetime.now()}] 외부 연동 자동화 오류: {str(e)}")
    time.sleep(3600)  # 1시간마다 실행 