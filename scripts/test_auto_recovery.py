import multiprocessing
import time
import requests
import os

def simulate_high_cpu():
    def cpu_load():
        while True: pass
    procs = [multiprocessing.Process(target=cpu_load) for _ in range(2)]
    for p in procs: p.start()
    time.sleep(60)  # 1분간 부하
    for p in procs: p.terminate()

def check_alerts():
    # 알림/이력 API에서 최근 장애/복구 알림 확인 (토큰 필요)
    token = os.getenv('ADMIN_API_TOKEN', 'YOUR_ADMIN_TOKEN')
    r = requests.get('http://localhost:5000/api/monitoring/logs/errors', headers={'Authorization': f'Bearer {token}'})
    print('최근 장애/복구 알림:', r.json())

if __name__ == '__main__':
    print('--- CPU 부하 테스트 시작 ---')
    simulate_high_cpu()
    print('--- 부하 후 알림/복구 이력 확인 ---')
    check_alerts() 