import requests
import time
import logging
from datetime import datetime

logging.basicConfig(filename='ai_automation_scheduler.log', level=logging.INFO)

API_BASE = 'http://localhost:5000/api/ai/automation'

while True:
    try:
        # 1. KPI 모니터링
        kpi_res = requests.get(f'{API_BASE}/kpi_monitor').json()
        logging.info(f"[{datetime.now()}] KPI: {kpi_res}")
        # 2. 자동 리포트
        report_res = requests.post(f'{API_BASE}/gpt_report', json={"type": "summary"}).json()
        logging.info(f"[{datetime.now()}] Report: {report_res}")
        # 3. 대시보드
        dash_res = requests.get(f'{API_BASE}/dashboard').json()
        logging.info(f"[{datetime.now()}] Dashboard: {dash_res}")
    except Exception as e:
        logging.error(f"[{datetime.now()}] 자동화 오류: {str(e)}")
    time.sleep(3600)  # 1시간마다 실행 