import requests
import os

def test_ai_prediction():
    token = os.getenv('ADMIN_API_TOKEN', 'YOUR_ADMIN_TOKEN')
    url = 'http://localhost:5000/api/ai/advanced/analysis/sales/predict'
    r = requests.post(url,
                      json={'model_type': 'compare'},
                      headers={'Authorization': f'Bearer {token}'})
    data = r.json()
    print('응답 코드:', r.status_code)
    print('AI 예측 결과:', data)
    assert data.get('success'), 'AI 예측 API 실패!'
    print('두 모델(랜덤포레스트/Prophet) 예측 결과/트렌드/신뢰도 비교 완료')

if __name__ == '__main__':
    test_ai_prediction() 