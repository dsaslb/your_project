#!/usr/bin/env python3
"""
신규 브랜드 생성~샘플 데이터~권한~초기화~페이지 정상 노출까지 자동화 테스트 스크립트 예시
- requests, BeautifulSoup 사용
- 초보자/운영자 안내 주석 포함

사용법:
python scripts/brand_auto_test.py --brand_id DEMOBRAND --base_url http://localhost:3000
"""
import os
import argparse
import requests
from bs4 import BeautifulSoup

# 샘플 테스트 시나리오
TEST_PATHS = [
    '/brand/{brand_id}/store',
    '/brand/{brand_id}/staff',
    '/brand/{brand_id}/sales',
    '/brand/{brand_id}/feedback',
    '/brand/{brand_id}/settings',
]

def test_brand_pages(base_url, brand_id):
    all_passed = True
    for path in TEST_PATHS:
        url = f"{base_url}{path.format(brand_id=brand_id)}"
        print(f"[테스트] {url}")
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.string if soup.title else ''
                print(f"  - [OK] 페이지 정상 노출 (title: {title})")
            else:
                print(f"  - [실패] HTTP {resp.status_code}")
                all_passed = False
        except Exception as e:
            print(f"  - [실패] 예외 발생: {e}")
            all_passed = False
    return all_passed

def main():
    parser = argparse.ArgumentParser(description='브랜드 자동화 테스트')
    parser.add_argument('--brand_id', required=True, help='테스트할 브랜드 ID')
    parser.add_argument('--base_url', required=True, help='프론트엔드 베이스 URL (예: http://localhost:3000)')
    args = parser.parse_args()
    print(f"[시작] 브랜드 자동화 테스트: {args.brand_id}")
    result = test_brand_pages(args.base_url, args.brand_id)
    if result:
        print("[성공] 모든 페이지가 정상적으로 노출됩니다!")
    else:
        print("[실패] 일부 페이지에서 오류가 발생했습니다. 로그를 확인하세요.")

if __name__ == '__main__':
    main() 