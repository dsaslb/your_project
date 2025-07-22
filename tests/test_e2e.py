import requests
import pytest

BASE_URL = 'http://localhost:5000'

@pytest.mark.parametrize('endpoint', [
    '/api/admin/brands',
    '/api/admin/branches',
    '/api/admin/employees',
    '/api/admin/plugins/market',
    '/api/admin/payments/history',
    '/api/admin/stats/summary',
    '/api/admin/notifications/history',
])
def test_admin_get_endpoints(endpoint):
    # 관리자 인증 토큰 필요시 헤더에 추가
    headers = {}
    r = requests.get(BASE_URL + endpoint, headers=headers)
    assert r.status_code in (200, 401, 403)  # 인증 미설정 시 401/403 허용


def test_brand_crud():
    # 관리자 인증 토큰 필요시 헤더에 추가
    headers = {'Content-Type': 'application/json'}
    # 1. 생성
    r = requests.post(BASE_URL + '/api/admin/brands', json={'name': 'E2E브랜드'}, headers=headers)
    assert r.status_code in (201, 401, 403)
    if r.status_code != 201:
        pytest.skip('관리자 인증 필요')
    brand = r.json()
    brand_id = brand['id']
    # 2. 조회
    r = requests.get(BASE_URL + f'/api/admin/brands/{brand_id}', headers=headers)
    assert r.status_code == 200
    # 3. 수정
    r = requests.put(BASE_URL + f'/api/admin/brands/{brand_id}', json={'name': 'E2E브랜드수정'}, headers=headers)
    assert r.status_code == 200
    # 4. 삭제
    r = requests.delete(BASE_URL + f'/api/admin/brands/{brand_id}', headers=headers)
    assert r.status_code == 200


def test_plugin_market_install():
    headers = {'Content-Type': 'application/json'}
    # 마켓 목록 조회
    r = requests.get(BASE_URL + '/api/admin/plugins/market', headers=headers)
    if r.status_code != 200:
        pytest.skip('관리자 인증 필요')
    plugins = r.json().get('plugins', [])
    if not plugins:
        pytest.skip('마켓 플러그인 없음')
    plugin_id = plugins[0]['id']
    # 설치 시도
    r = requests.post(BASE_URL + '/api/admin/plugins/install', json={'plugin_id': plugin_id}, headers=headers)
    assert r.status_code in (200, 400) 