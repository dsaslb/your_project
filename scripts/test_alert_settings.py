import requests
import os

def update_alert_settings():
    token = os.getenv('ADMIN_API_TOKEN', 'YOUR_ADMIN_TOKEN')
    url = 'http://localhost:5000/api/monitoring/alerts/settings'
    payload = {
        'cpu_threshold': 70,
        'memory_threshold': 80,
        'slack_notifications': True,
        'mobile_notifications': True
    }
    r = requests.put(url, json=payload, headers={'Authorization': f'Bearer {token}'})
    print('응답 코드:', r.status_code)
    print('알림/임계값 설정 변경 결과:', r.json())
    assert r.status_code == 200, '알림/임계값 설정 변경 실패!'
    print('임계값/알림 채널 실시간 변경 및 Slack/모바일 알림 활성화 테스트 완료')

if __name__ == '__main__':
    update_alert_settings() 